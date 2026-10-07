"""Generate Step 3 additions by running the exact frozen decision core."""

import argparse
import json
import math
from pathlib import Path

from generate import BASELINE, ROOT, load_reference, observed_call, vector

OUTPUT = ROOT / "analysis_vectors.jsonl"
ODDS_PAIRS = ((1.0, 1.0), (2.0, 2.0), (1.8, 1.8), (2.2, 2.2), (1.5, 4.0), (4.0, 1.5), (10.0, 25.0))
HISTORIES = (
    (0, 0),
    (1, 0),
    (0, 1),
    (18, 2),
    (19, 1),
    (20, 0),
    (50, 50),
    (0, 20),
    (1, 19),
    (2, 18),
    (100, 25),
    (25, 100),
)


def generate() -> list[dict]:
    from probability_calibration_tool.core import (
        analyze_historical_odds,
        analyze_subjective_odds,
        classify_ev_state,
        classify_odds_combination,
        compute_historical_estimate,
        compute_subjective_estimate,
    )
    from probability_calibration_tool.core.model_specs import FLOAT_EPSILON

    rows = [vector("metadata", "step3", {}, {"commit": BASELINE})]
    for raw in range(101):
        subject = compute_subjective_estimate(raw)
        for index, (event, complement) in enumerate(ODDS_PAIRS):
            rows.append(
                vector(
                    "subjective_odds",
                    f"matrix_{raw}_{index}",
                    {"p_h_raw": raw, "win_odds": event, "lose_odds": complement},
                    analyze_subjective_odds(subject, event, complement),
                )
            )
    for raw in (1, 25, 50, 60, 85, 99):
        subject = compute_subjective_estimate(raw)
        boundaries = (
            (1 / subject.p_min, 2.0),
            (1 / subject.p_max, 2.0),
            (2.0, 1 / (1 - subject.p_max)),
            (2.0, 1 / (1 - subject.p_min)),
        )
        for index, (event, complement) in enumerate(boundaries):
            rows.append(
                vector(
                    "subjective_odds",
                    f"boundary_{raw}_{index}",
                    {"p_h_raw": raw, "win_odds": event, "lose_odds": complement},
                    analyze_subjective_odds(subject, event, complement),
                )
            )
    for events, complements in HISTORIES:
        history = compute_historical_estimate(events, complements)
        for index, (event, complement) in enumerate(ODDS_PAIRS):
            rows.append(
                vector(
                    "historical_odds",
                    f"matrix_{events}_{complements}_{index}",
                    {
                        "wins": events,
                        "losses": complements,
                        "win_odds": event,
                        "lose_odds": complement,
                    },
                    analyze_historical_odds(history, event, complement),
                )
            )
    invalid_pairs = (
        (float("nan"), 0.5),
        (0.5, float("nan")),
        (float("inf"), 2.0),
        (2.0, float("inf")),
        (2.0, 0.5),
    )
    for index, (event, complement) in enumerate(invalid_pairs):
        encoded = {"win_odds": tagged(event), "lose_odds": tagged(complement)}
        subject = compute_subjective_estimate(50)
        rows.append(
            vector(
                "subjective_odds_validation",
                str(index),
                {"p_h_raw": 50, **encoded},
                observed_call(
                    lambda subject=subject, event=event, complement=complement: (
                        analyze_subjective_odds(subject, event, complement)
                    )
                ),
            )
        )
        rows.append(
            vector(
                "odds_combination_validation",
                str(index),
                encoded,
                observed_call(
                    lambda event=event, complement=complement: classify_odds_combination(
                        event, complement
                    )
                ),
            )
        )
        for events, complements in HISTORIES:
            history = compute_historical_estimate(events, complements)
            rows.append(
                vector(
                    "historical_odds_control_flow",
                    f"matrix_{events}_{complements}_{index}",
                    {"wins": events, "losses": complements, **encoded},
                    observed_call(
                        lambda history=history, event=event, complement=complement: (
                            analyze_historical_odds(history, event, complement)
                        )
                    ),
                )
            )
    for index, factor in enumerate((-2, -1, -0.5, 0, 0.5, 1, 2)):
        point = factor * FLOAT_EPSILON
        for side, (minimum, maximum) in enumerate(((point, 0.1), (-0.1, point))):
            rows.append(
                vector(
                    "ev_state",
                    f"boundary_{index}_{side}",
                    {"ev_min": minimum, "ev_max": maximum},
                    classify_ev_state(minimum, maximum),
                )
            )
        complement = 1.0 / (0.5 + point)
        for side, odds in enumerate(
            (math.nextafter(complement, 0.0), complement, math.nextafter(complement, math.inf))
        ):
            rows.append(
                vector(
                    "odds_combination",
                    f"boundary_{index}_{side}",
                    {"win_odds": 2.0, "lose_odds": odds},
                    classify_odds_combination(2.0, odds),
                )
            )
    return rows


def tagged(value: float) -> float | str:
    return "nan" if math.isnan(value) else "infinity" if math.isinf(value) else value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-root", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    load_reference(args.reference_root.resolve())
    rows = generate()
    payload = "".join(
        json.dumps(row, sort_keys=True, allow_nan=False) + "\n" for row in rows
    ).encode("ascii")
    if args.check:
        if OUTPUT.read_bytes() != payload:
            raise SystemExit("Step 3 oracle differs from frozen reference")
        print(f"Verified {len(rows) - 1} Step 3 reference additions")
    else:
        OUTPUT.write_bytes(payload)
        print(f"Wrote {len(rows) - 1} Step 3 reference additions")


if __name__ == "__main__":
    main()
