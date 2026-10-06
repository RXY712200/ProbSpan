"""Deterministic development-only differential comparison with frozen Python."""

import argparse
import random
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "oracle"))
from generate import load_reference, observed_call
from generate_decimal import bits, cases, dyadic_decimal

SEED = 20261006
RANDOM_CASES = 6000


def corpus() -> list[str]:
    rng = random.Random(SEED)
    texts = [text for _, text in cases()]
    for _ in range(RANDOM_CASES):
        integer_length = rng.choice((1, 2, 9, 16, 17, 50, 100, 308, 309, 310, 500))
        fraction_length = rng.choice((0, 1, 2, 17, 53, 300, 1200, 4000))
        integer = "".join(str(rng.randrange(10)) for _ in range(integer_length))
        fraction = "".join(str(rng.randrange(10)) for _ in range(fraction_length))
        texts.append(
            "0" * rng.choice((0, 0, 1, 32, 500)) + integer + ("." + fraction if fraction else "")
        )
    # Construct exact and remotely perturbed dyadic boundary patterns across
    # normal/subnormal magnitudes, including midpoints. Expectations always
    # execute the frozen parser.
    for exponent in (-1074, -1022, -53, -1, 0, 10, 53, 500, 970):
        for significand in (1, 3, 2**53 - 1):
            value = Fraction(significand) * Fraction(2) ** (exponent - 1)
            midpoint = dyadic_decimal(value)
            if "." not in midpoint:
                midpoint += ".0"
            texts += [midpoint, midpoint + "0" * 5000 + "1"]
    texts += [
        "0" * 100000 + "1.25",
        "1.25" + "0" * 100000 + "1",
        "0." + "0" * 100000 + "1",
        "9" * 100000,
    ]
    return texts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-root", type=Path, required=True)
    parser.add_argument("--executable", type=Path, required=True)
    args = parser.parse_args()
    load_reference(args.reference_root.resolve())
    from probability_calibration_tool.core.validation import parse_odds_text

    texts = corpus()
    output = subprocess.run(
        [str(args.executable.resolve()), "--stdin"],
        input="\n".join(texts) + "\n",
        text=True,
        capture_output=True,
        check=True,
    ).stdout.splitlines()
    success = rejected = 0
    for text, result in zip(texts, output, strict=True):
        observed = observed_call(lambda text=text: parse_odds_text(text))
        status, converted, parsed = result.split()
        assert converted == bits(float(text)), f"Conversion mismatch: {text[:120]}"
        if "value" in observed:
            assert status == "ok" and parsed == bits(observed["value"]), text[:120]
            success += 1
        else:
            assert observed["code"] == "odds_range"
            assert status == "odds_range" and parsed == bits(7.0), text[:120]
            rejected += 1
    print(
        f"Bit-exact differential: {len(texts)} cases, {success} successful, "
        f"{rejected} range rejections; seed {SEED}; zero mismatches"
    )


if __name__ == "__main__":
    main()
