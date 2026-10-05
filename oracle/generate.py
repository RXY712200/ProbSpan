"""Generate reviewable v1 vectors by executing the frozen Python implementation.

Run with a Python environment containing the reference project's SciPy dependency.
The source checkout must be at the exact baseline commit. No expected result is
calculated independently here; case construction is kept separate from serialization.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, is_dataclass, replace
from datetime import UTC, datetime, timedelta
from enum import Enum
from pathlib import Path
from tempfile import TemporaryDirectory

BASELINE = "a581f84ccd217ed45789b3566347255f56ffbeac"
ROOT = Path(__file__).resolve().parent


def load_reference(reference_root: Path) -> None:
    head = subprocess.check_output(
        ["git", "-C", str(reference_root), "rev-parse", "HEAD"], text=True
    ).strip()
    if head != BASELINE:
        raise SystemExit(f"Reference HEAD is {head}; expected {BASELINE}")
    sys.path.insert(0, str(reference_root / "src"))


def plain(value):
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {key: plain(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {key: plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(item) for item in value]
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def vector(group: str, case: str, inputs: dict, expected) -> dict:
    return {"group": group, "case": case, "input": plain(inputs), "expected": plain(expected)}


def subjective_vectors():
    import math

    from probability_calibration_tool.core import compute_subjective_estimate
    from probability_calibration_tool.core.subjective import subjective_logit_half_width

    for raw in range(101):
        yield vector(
            "subjective", f"raw_{raw:03}", {"p_h_raw": raw}, compute_subjective_estimate(raw)
        )

    # Include both exact breakpoints and adjacent binary64 values. The 0.55
    # branch is deliberately asymmetric with the lower and upper segments.
    for breakpoint in (0.01, 0.45, 0.55, 0.85, 0.95, 0.99):
        for side, probability in (
            ("below", math.nextafter(breakpoint, 0.0)),
            ("at", breakpoint),
            ("above", math.nextafter(breakpoint, 1.0)),
        ):
            if 0.01 <= probability <= 0.99:
                yield vector(
                    "subjective_width",
                    f"{breakpoint}_{side}",
                    {"probability": probability},
                    subjective_logit_half_width(probability),
                )


def history_vectors():
    from probability_calibration_tool.core import compute_historical_estimate

    histories = (
        (0, 0),
        (1, 0),
        (0, 1),
        (19, 0),
        (18, 2),
        (19, 1),
        (20, 0),
        (50, 50),
        (10, 9),
        (10, 10),
        (11, 9),
        (17, 3),
        (18, 1),
    )
    for wins, losses in histories:
        history = compute_historical_estimate(wins, losses)
        yield vector("history", f"{wins}_{losses}", {"wins": wins, "losses": losses}, history)


def odds_validation_vectors():
    from probability_calibration_tool.core import parse_odds_text
    from probability_calibration_tool.core.errors import CoreValidationError
    from probability_calibration_tool.core.validation import validate_odds

    odds_texts = (
        "1",
        "16",
        "1.01",
        "2.500",
        "0002.50",
        "1e3",
        "1E3",
        "NaN",
        "inf",
        "-2",
        "+2",
        "1,5",
        "1..2",
        "1.",
        ".5",
        "",
        " ",
        " 2",
        "2 ",
        "１２",
        "0",
        "0.99",
    )
    for index, text in enumerate(odds_texts):
        try:
            expected = {"value": parse_odds_text(text)}
        except CoreValidationError as exc:
            expected = {"error": type(exc).__name__, "code": plain(exc.code)}
        yield vector("odds_parse", str(index), {"text": text}, expected)

    numeric_odds = (
        ("one", 1),
        ("decimal", 2.5),
        ("below_one", 0.99),
        ("boolean", True),
        ("text", "2"),
        ("null", None),
        ("nan", float("nan")),
        ("infinity", float("inf")),
    )
    for name, odds in numeric_odds:
        try:
            expected = {"value": validate_odds(odds)}
        except CoreValidationError as exc:
            expected = {"error": type(exc).__name__, "code": plain(exc.code)}
        # JSON has no NaN or infinity: the tag is a lossless description of
        # the constructed input, while validation still runs on the float.
        input_value = name if name in ("nan", "infinity") else odds
        yield vector("odds_numeric", name, {"odds": input_value}, expected)


def classification_vectors():
    from probability_calibration_tool.core import classify_ev_state, classify_odds_combination
    from probability_calibration_tool.core.model_specs import FLOAT_EPSILON

    odds_pairs = (
        (1.0, 1.0),
        (2.0, 2.0),
        (1.8, 1.8),
        (2.2, 2.2),
        (2.0, 1.0 / (0.5 + 0.5 * FLOAT_EPSILON)),
        (2.0, 1.0 / (0.5 + 2.0 * FLOAT_EPSILON)),
        (2.0, 1.0 / (0.5 - 2.0 * FLOAT_EPSILON)),
    )
    for index, (win_odds, lose_odds) in enumerate(odds_pairs):
        yield vector(
            "odds_combination",
            str(index),
            {"win_odds": win_odds, "lose_odds": lose_odds},
            classify_odds_combination(win_odds, lose_odds),
        )

    for index, (ev_min, ev_max) in enumerate(
        (
            (0.0, 0.1),
            (0.5 * FLOAT_EPSILON, 0.1),
            (FLOAT_EPSILON, 0.1),
            (2 * FLOAT_EPSILON, 0.1),
            (-0.1, 0.0),
            (-0.1, -0.5 * FLOAT_EPSILON),
            (-0.1, -FLOAT_EPSILON),
            (-0.1, -2 * FLOAT_EPSILON),
        )
    ):
        yield vector(
            "ev_state",
            str(index),
            {"ev_min": ev_min, "ev_max": ev_max},
            classify_ev_state(ev_min, ev_max),
        )


def analysis_vectors():
    from probability_calibration_tool.core import (
        analyze_historical_odds,
        analyze_subjective_odds,
        compute_historical_estimate,
        compute_subjective_estimate,
    )

    subject = compute_subjective_estimate(60)
    margin_pairs = (
        ("win_lower", 1.0 / subject.p_min, 2.0),
        ("win_upper", 1.0 / subject.p_max, 2.0),
        ("lose_lower", 2.0, 1.0 / (1.0 - subject.p_max)),
        ("lose_upper", 2.0, 1.0 / (1.0 - subject.p_min)),
        ("odds_one", 1.0, 1.0),
        ("ordinary", 2.0, 3.0),
    )
    for name, win_odds, lose_odds in margin_pairs:
        yield vector(
            "subjective_odds",
            name,
            {"p_h_raw": 60, "win_odds": win_odds, "lose_odds": lose_odds},
            analyze_subjective_odds(subject, win_odds, lose_odds),
        )

    for wins, losses in ((0, 0), (1, 0), (18, 2), (19, 1), (20, 0), (50, 50)):
        history = compute_historical_estimate(wins, losses)
        for name, win_odds, lose_odds in (
            ("one", 1.0, 1.0),
            ("critical", 2.0, 2.0),
            ("unequal", 1.5, 4.0),
        ):
            yield vector(
                "historical_odds",
                f"{wins}_{losses}_{name}",
                {"wins": wins, "losses": losses, "win_odds": win_odds, "lose_odds": lose_odds},
                analyze_historical_odds(history, win_odds, lose_odds),
            )


def model_relation_vectors():
    from probability_calibration_tool.core import classify_model_relation
    from probability_calibration_tool.domain.enums import EvState

    states = list(EvState)
    for subjective in states:
        for historical in (None, *states):
            yield vector(
                "model_relation",
                f"{subjective.value}_{historical.value if historical else 'none'}",
                {"subjective": subjective, "historical": historical},
                classify_model_relation(subjective, historical),
            )


class FixedClock:
    def __init__(self):
        self.value = datetime(2026, 9, 1, 10, 0, tzinfo=UTC)

    def now(self):
        return self.value

    def advance(self):
        self.value += timedelta(minutes=1)


class SequentialIds:
    def __init__(self):
        self.next_value = 0

    def new_id(self):
        self.next_value += 1
        return f"{self.next_value:032x}"


def transition_vectors():
    """Exercise the actual application service with deterministic clock and IDs."""
    from probability_calibration_tool.application import CalculateCommand, RoundService
    from probability_calibration_tool.persistence.database import create_connection
    from probability_calibration_tool.persistence.migrations import ensure_schema
    from probability_calibration_tool.persistence.unit_of_work import create_uow_factory

    with TemporaryDirectory() as directory:
        database = Path(directory) / "oracle.sqlite"
        connection = create_connection(database)
        try:
            ensure_schema(connection)
        finally:
            connection.close()
        clock = FixedClock()
        service = RoundService(create_uow_factory(database), clock, SequentialIds())
        seed = CalculateCommand(1, False, 60, "2", "2")
        for result in (True,) * 19 + (False,):
            view = service.calculate(seed)
            clock.advance()
            service.complete_pending(view.round_id, result, True)
            clock.advance()

        def capture(name, view, command):
            return vector(
                "revision",
                name,
                {"command": command, "at": clock.now()},
                {
                    "revision_count": view.revision_count,
                    "history_exposed": view.history_exposed,
                    "history_exposed_at": view.history_exposed_at,
                    "subjective_independence_compromised": view.subjective_independence_compromised,
                    "history_display_state": view.history.state,
                },
            )

        command = CalculateCommand(1, False, 0, "2", "2")
        view = service.calculate(command)
        yield capture("initial_hidden", view, command)
        cases = (
            ("first_exposure_and_raw_change", replace(command, reference_history=True, p_h_raw=1)),
            ("odds_only", replace(command, reference_history=True, p_h_raw=1, win_odds_raw="4")),
            ("reference_off", replace(command, reference_history=False, p_h_raw=1)),
            ("raw_change_after_exposure", replace(command, reference_history=True, p_h_raw=2)),
            ("restore_raw", replace(command, reference_history=True, p_h_raw=0)),
            ("character_change", replace(command, character_id=2, reference_history=True)),
            ("restore_character", replace(command, reference_history=True)),
        )
        for name, command in cases:
            clock.advance()
            view = service.recalculate(view.round_id, command)
            yield capture(name, view, command)

        clock.advance()
        service.complete_pending(view.round_id, True, False)
        clock.advance()
        command = CalculateCommand(1, True, 70, "2", "3")
        view = service.calculate(command)
        yield capture("initial_visible", view, command)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-root", type=Path, required=True)
    parser.add_argument(
        "--check", action="store_true", help="Compare generated bytes with committed vectors"
    )
    args = parser.parse_args()
    load_reference(args.reference_root.resolve())
    rows = [vector("metadata", "baseline", {}, {"commit": BASELINE})]
    for cases in (
        subjective_vectors(),
        history_vectors(),
        odds_validation_vectors(),
        classification_vectors(),
        analysis_vectors(),
        model_relation_vectors(),
    ):
        rows.extend(cases)
    rows.extend(transition_vectors())
    payload = "".join(
        json.dumps(row, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
        for row in rows
    )
    target = ROOT / "v1_vectors.jsonl"
    if args.check:
        if target.read_text(encoding="utf-8") != payload:
            raise SystemExit("Committed oracle differs from frozen reference output")
        print(f"Verified {len(rows)} reference vectors")
    else:
        target.write_text(payload, encoding="utf-8", newline="\n")
        print(f"Wrote {len(rows)} reference vectors to {target}")


if __name__ == "__main__":
    main()
