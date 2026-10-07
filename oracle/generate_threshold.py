"""Generate focused Step 3 thresholds under the accepted large-numerics exception.

Use the frozen source environment with --with mpmath==1.3.0. Its EV/state
code runs unchanged; only inconsistent SciPy intervals/CDFs are replaced by
the already accepted independent 80-digit Beta integral computation.
"""

import argparse
import json
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import mpmath as mp
from generate import BASELINE, ROOT, load_reference, plain
from generate_large import DIGITS, MAX_COUNT, BetaIntegral

OUTPUT = ROOT / "threshold_reference.json"
HISTORIES = (
    (10**12, 10**12),
    (10**18, 10**18),
    (MAX_COUNT, MAX_COUNT),
    (MAX_COUNT // 1000, MAX_COUNT),
    (0, MAX_COUNT),
    (MAX_COUNT, MAX_COUNT // 1000),
)


def generate() -> dict:
    from probability_calibration_tool.core import (
        analyze_historical_odds,
        compute_historical_estimate,
    )

    rows = []
    with mp.workdps(DIGITS):
        for events, complements in HISTORIES:
            print(f"Threshold reference: {events}/{complements}", flush=True)
            exact = BetaIntegral(
                mp.mpf(events) + mp.mpf("0.5"), mp.mpf(complements) + mp.mpf("0.5")
            )
            lower, upper = exact.quantile(mp.mpf("0.025")), exact.quantile(mp.mpf("0.975"))
            # Run the frozen gate itself with corrected quantiles. SciPy can
            # return NaN at these shapes, which otherwise corrupts readiness.
            # Changing just the numerical evaluator preserves gate semantics.
            with patch(
                "probability_calibration_tool.core.historical.beta.ppf",
                lambda p, a, b, lower=lower, upper=upper: float(lower if p < 0.5 else upper),
            ):
                history = compute_historical_estimate(events, complements)
            history = replace(history, probability=float(exact.center))
            assert history.statistically_ready and upper - lower <= mp.mpf("0.25")
            represented = BetaIntegral(
                mp.mpf(float(events) + 0.5), mp.mpf(float(complements) + 0.5)
            )

            def high_precision_cdf(
                x: float, alpha: float, beta: float, integral: BetaIntegral = represented
            ) -> float:
                assert mp.mpf(alpha) == integral.alpha and mp.mpf(beta) == integral.beta
                value = integral.cdf(mp.mpf(x))
                assert 0 <= value <= 1
                reflected = BetaIntegral(integral.beta, integral.alpha).cdf(1 - mp.mpf(x))
                assert abs(value + reflected - 1) < mp.mpf("1e-40")
                return float(value)

            sigma = mp.sqrt(exact.center * (1 - exact.center) / (exact.total + 1))
            for offset in (-1, 0, 1):
                target = exact.center + offset * sigma
                if target <= 0:
                    target = exact.center / 2
                if target >= 1:
                    target = (1 + exact.center) / 2
                event_odds = float(1 / target)
                complement_odds = float(1 / (1 - target))
                # Reference threshold expressions evaluate in binary64, so
                # high-precision CDFs must use those exact represented inputs,
                # not the unrounded ideal target used to construct the odds.
                with patch("probability_calibration_tool.core.ev.beta.cdf", high_precision_cdf):
                    analysis = analyze_historical_odds(history, event_odds, complement_odds)
                rows.append(
                    {
                        "events": events,
                        "complements": complements,
                        "event_odds": event_odds,
                        "complement_odds": complement_odds,
                        "event_threshold": 1.0 / event_odds,
                        "complement_threshold_as_event": 1.0 - 1.0 / complement_odds,
                        "expected": plain(analysis),
                    }
                )
    return {
        "metadata": {
            "policy": "Accepted Step 2 large-parameter numerical reference exception only",
            "commit": BASELINE,
            "tool": "mpmath",
            "tool_version": mp.__version__,
            "decimal_precision": DIGITS,
            "method": "Accepted exact Beta integral with tanh-sinh quadrature and log-gamma normalization",
            "cdf_inputs": "Exact represented binary64 thresholds and shapes; exact integer-count model for intervals",
            "event_formula": "1-BetaCDF(1/event_odds; events+0.5, complements+0.5)",
            "complement_formula": "BetaCDF(1-1/complement_odds; events+0.5, complements+0.5)",
            "absolute_tolerance": 1e-10,
            "relative_tolerance": 1e-10,
        },
        "cases": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-root", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    load_reference(args.reference_root.resolve())
    if mp.__version__ != "1.3.0":
        raise SystemExit("Reference requires mpmath 1.3.0")
    data = generate()
    payload = (json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("ascii")
    if args.check:
        if OUTPUT.read_bytes() != payload:
            raise SystemExit("Step 3 corrected threshold reference is stale")
        print(f"Verified {len(data['cases'])} corrected threshold cases")
    else:
        OUTPUT.write_bytes(payload)
        print(f"Wrote {len(data['cases'])} corrected threshold cases")


if __name__ == "__main__":
    main()
