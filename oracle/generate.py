"""Generate reviewable v1 vectors by executing the frozen Python implementation.

Run with a Python environment containing the reference project's SciPy dependency.
The source checkout must be at the exact baseline commit. No expected result is
calculated independently here; case construction is kept separate from serialization.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from contextlib import contextmanager
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
    dirty = subprocess.check_output(
        ["git", "-C", str(reference_root), "status", "--porcelain", "--untracked-files=no"],
        text=True,
    ).strip()
    if dirty:
        raise SystemExit("Reference checkout has tracked changes; oracle source is not frozen")
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


def observed_call(call):
    """Capture the actual result or the reference core's validation failure."""
    from probability_calibration_tool.core.errors import CoreValidationError

    try:
        return {"value": call()}
    except CoreValidationError as exc:
        return {"error": type(exc).__name__, "code": exc.code}


def constant_vectors():
    from probability_calibration_tool.core import model_specs

    names = (
        "SUBJECTIVE_MODEL_VERSION",
        "HISTORY_MODEL_VERSION",
        "HISTORY_GATE_VERSION",
        "ODDS_ANALYSIS_VERSION",
        "STATS_VERSION",
        "FLOAT_EPSILON",
        "JEFFREYS_ALPHA",
        "JEFFREYS_BETA",
        "HISTORY_CREDIBLE_LEVEL",
        "HISTORY_MIN_SAMPLE_SIZE",
        "HISTORY_MAX_INTERVAL_WIDTH",
        "SUBJECTIVE_MIN_PROBABILITY",
        "SUBJECTIVE_LOW_BREAKPOINT",
        "SUBJECTIVE_MID_HIGH_BREAKPOINT",
        "SUBJECTIVE_HIGH_BREAKPOINT",
        "SUBJECTIVE_VERY_HIGH_BREAKPOINT",
        "SUBJECTIVE_MAX_PROBABILITY",
        "SUBJECTIVE_FACTOR_LOW",
        "SUBJECTIVE_FACTOR_MID",
        "SUBJECTIVE_FACTOR_HIGH",
        "SUBJECTIVE_FACTOR_MAX",
        "LOG_FACTOR_LOW",
        "LOG_FACTOR_MID",
        "LOG_FACTOR_HIGH",
        "LOG_FACTOR_MAX",
    )
    yield vector(
        "constants", "model_specs_v1", {}, {name: getattr(model_specs, name) for name in names}
    )


def subjective_vectors():
    from probability_calibration_tool.core import compute_subjective_estimate, model_specs
    from probability_calibration_tool.core.subjective import subjective_logit_half_width

    for raw in range(101):
        yield vector(
            "subjective", f"raw_{raw:03}", {"p_h_raw": raw}, compute_subjective_estimate(raw)
        )

    # Include both exact breakpoints and adjacent binary64 values. The 0.55
    # branch is deliberately asymmetric with the lower and upper segments.
    for breakpoint in (
        model_specs.SUBJECTIVE_MIN_PROBABILITY,
        model_specs.SUBJECTIVE_LOW_BREAKPOINT,
        model_specs.SUBJECTIVE_MID_HIGH_BREAKPOINT,
        model_specs.SUBJECTIVE_HIGH_BREAKPOINT,
        model_specs.SUBJECTIVE_VERY_HIGH_BREAKPOINT,
        model_specs.SUBJECTIVE_MAX_PROBABILITY,
    ):
        for side, probability in (
            ("below", math.nextafter(breakpoint, 0.0)),
            ("at", breakpoint),
            ("above", math.nextafter(breakpoint, 1.0)),
        ):
            if (
                model_specs.SUBJECTIVE_MIN_PROBABILITY
                <= probability
                <= model_specs.SUBJECTIVE_MAX_PROBABILITY
            ):
                yield vector(
                    "subjective_width",
                    f"{breakpoint}_{side}",
                    {"probability": probability},
                    subjective_logit_half_width(probability),
                )

    for raw in (-1, 101):
        yield vector(
            "subjective_validation",
            f"raw_{raw}",
            {"p_h_raw": raw},
            observed_call(lambda raw=raw: compute_subjective_estimate(raw)),
        )

    for name, probability in (
        ("below_minimum", math.nextafter(model_specs.SUBJECTIVE_MIN_PROBABILITY, 0.0)),
        ("above_maximum", math.nextafter(model_specs.SUBJECTIVE_MAX_PROBABILITY, 1.0)),
    ):
        yield vector(
            "subjective_width_validation",
            name,
            {"probability": probability},
            observed_call(lambda probability=probability: subjective_logit_half_width(probability)),
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

    for wins, losses in ((-1, 0), (0, -1)):
        yield vector(
            "history_validation",
            f"{wins}_{losses}",
            {"wins": wins, "losses": losses},
            observed_call(
                lambda wins=wins, losses=losses: compute_historical_estimate(wins, losses)
            ),
        )


def odds_validation_vectors():
    from probability_calibration_tool.core import parse_odds_text
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
        yield vector(
            "odds_parse",
            str(index),
            {"text": text},
            observed_call(lambda text=text: parse_odds_text(text)),
        )

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
        # JSON has no NaN or infinity: the tag is a lossless description of
        # the constructed input, while validation still runs on the float.
        input_value = name if name in ("nan", "infinity") else odds
        yield vector(
            "odds_numeric",
            name,
            {"odds": input_value},
            observed_call(lambda odds=odds: validate_odds(odds)),
        )


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

    # Frozen order: a non-valid history returns None before odds validation.
    # A valid history reaches validation and reports its actual failure code.
    for name, wins, losses, win_odds, lose_odds in (
        ("no_history_nan", 0, 0, float("nan"), 0.5),
        ("insufficient_nan", 1, 0, float("nan"), 0.5),
        ("valid_nan", 19, 1, float("nan"), 2.0),
        ("valid_below_one", 19, 1, 0.5, 2.0),
    ):
        history = compute_historical_estimate(wins, losses)
        yield vector(
            "historical_odds_control_flow",
            name,
            {
                "wins": wins,
                "losses": losses,
                "win_odds": "nan" if math.isnan(win_odds) else win_odds,
                "lose_odds": lose_odds,
            },
            observed_call(
                lambda history=history, win_odds=win_odds, lose_odds=lose_odds: (
                    analyze_historical_odds(history, win_odds, lose_odds)
                )
            ),
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


class RoundFixture:
    def __init__(self, service, clock):
        self.service = service
        self.clock = clock

    def seed_history(self, wins, losses, character_id):
        from probability_calibration_tool.application import CalculateCommand

        command = CalculateCommand(character_id, False, 60, "2", "2")
        for result in (True,) * wins + (False,) * losses:
            view = self.service.calculate(command)
            self.clock.advance()
            self.service.complete_pending(view.round_id, result, True)
            self.clock.advance()

    def recalculate(self, view, command):
        self.clock.advance()
        return self.service.recalculate(view.round_id, command)

    def record(self, case, command, view):
        return vector(
            "revision",
            case,
            {"command": command, "at": self.clock.now()},
            {
                "revision_count": view.revision_count,
                "history_exposed": view.history_exposed,
                "history_exposed_at": view.history_exposed_at,
                "subjective_independence_compromised": view.subjective_independence_compromised,
                "history_display_state": view.history.state,
                "subjective_probability": view.subjective.probability,
                "p_h_used": view.subjective.p_h_used,
            },
        )


@contextmanager
def round_fixture(histories=()):
    """Create one isolated frozen RoundService run with repeatable provenance."""
    from probability_calibration_tool.application import RoundService
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
        fixture = RoundFixture(service, clock)
        for character_id, wins, losses in histories:
            fixture.seed_history(wins, losses, character_id)
        yield fixture


def transition_vectors():
    """Freeze independent causal transitions through the actual RoundService."""
    from probability_calibration_tool.application import CalculateCommand

    hidden = CalculateCommand(1, False, 60, "2", "2")
    visible = replace(hidden, reference_history=True)
    ready = ((1, 19, 1),)

    with round_fixture() as fixture:
        view = fixture.service.calculate(visible)
        yield fixture.record("no_history_initial", visible, view)

    with round_fixture(((1, 1, 0),)) as fixture:
        view = fixture.service.calculate(visible)
        yield fixture.record("insufficient_initial", visible, view)

    with round_fixture(ready) as fixture:
        command = replace(hidden, p_h_raw=0)
        view = fixture.service.calculate(command)
        yield fixture.record("first_exposure_raw_before", command, view)
        command = replace(command, reference_history=True, p_h_raw=1)
        view = fixture.recalculate(view, command)
        # The old exposure flag controls compromise: exposure acquired by this
        # revision does not retroactively compromise the same revision.
        yield fixture.record("first_exposure_raw_after", command, view)

    with round_fixture(((2, 19, 1),)) as fixture:
        view = fixture.service.calculate(hidden)
        yield fixture.record("first_exposure_identity_before", hidden, view)
        command = replace(visible, character_id=2)
        view = fixture.recalculate(view, command)
        yield fixture.record("first_exposure_identity_after", command, view)

    with round_fixture(ready) as fixture:
        view = fixture.service.calculate(visible)
        yield fixture.record("exposed_identity_before", visible, view)
        command = replace(visible, character_id=2)
        view = fixture.recalculate(view, command)
        yield fixture.record("exposed_identity_after", command, view)

    with round_fixture(ready) as fixture:
        command = replace(visible, p_h_raw=0)
        view = fixture.service.calculate(command)
        yield fixture.record("raw_zero_to_one_before", command, view)
        command = replace(command, p_h_raw=1)
        view = fixture.recalculate(view, command)
        # Both raw values clamp to 1%, but the raw input itself determines
        # whether independence was compromised after exposure.
        yield fixture.record("raw_zero_to_one_after", command, view)

    with round_fixture(((1, 19, 1), (3, 1, 0))) as fixture:
        view = fixture.service.calculate(visible)
        yield fixture.record("sticky_exposure_initial", visible, view)
        command = replace(visible, reference_history=False)
        view = fixture.recalculate(view, command)
        yield fixture.record("sticky_exposure_hidden", command, view)
        command = replace(visible, character_id=2)
        view = fixture.recalculate(view, command)
        yield fixture.record("sticky_exposure_no_history", command, view)
        command = replace(visible, character_id=3)
        view = fixture.recalculate(view, command)
        yield fixture.record("sticky_exposure_insufficient", command, view)

    with round_fixture(ready) as fixture:
        view = fixture.service.calculate(visible)
        yield fixture.record("noncompromising_initial", visible, view)
        odds_changed = replace(visible, win_odds_raw="4")
        for case, command in (
            ("noncompromising_odds_only", odds_changed),
            ("noncompromising_reference_off", replace(odds_changed, reference_history=False)),
            ("noncompromising_reference_on", odds_changed),
        ):
            view = fixture.recalculate(view, command)
            yield fixture.record(case, command, view)

    with round_fixture(ready) as fixture:
        view = fixture.service.calculate(visible)
        yield fixture.record("sticky_compromise_initial", visible, view)
        command = replace(visible, p_h_raw=70)
        view = fixture.recalculate(view, command)
        yield fixture.record("sticky_compromise_changed", command, view)
        view = fixture.recalculate(view, visible)
        yield fixture.record("sticky_compromise_restored", visible, view)


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
        constant_vectors(),
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
    expected_bytes = payload.encode("utf-8")
    if args.check:
        if target.read_bytes() != expected_bytes:
            raise SystemExit("Committed oracle differs from frozen reference output")
        print(f"Verified {len(rows)} reference vectors")
    else:
        target.write_bytes(expected_bytes)
        print(f"Wrote {len(rows)} reference vectors to {target}")


if __name__ == "__main__":
    main()
