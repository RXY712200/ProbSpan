"""Generate bit-exact decimal odds vectors from the frozen Python parser."""

import argparse
import json
import math
import platform
import struct
from fractions import Fraction
from pathlib import Path

from generate import BASELINE, ROOT, load_reference, observed_call

OUTPUT = ROOT / "decimal_vectors.jsonl"


def dyadic_decimal(value: Fraction) -> str:
    """Construct exact halfway test inputs; expected outputs still come from Python."""
    power = value.denominator.bit_length() - 1
    assert value.denominator == 2**power
    digits = str(value.numerator * 5**power)
    if power == 0:
        return digits
    digits = digits.zfill(power + 1)
    return digits[:-power] + "." + digits[-power:]


def cases() -> list[tuple[str, str]]:
    items = [
        ("review_large", "894221282.4149349195"),
        ("review_fraction", "1.23456789012345678901234567890123456789"),
        ("long_fraction", "1." + "2345678901" * 200),
        ("leading_zeroes", "0" * 2000 + "894221282.4149349195"),
        ("long_insignificant_tail", "1.25" + "0" * 3000 + "1"),
        ("overflow", "9" * 400),
        ("overflow_fraction", "9" * 310 + "." + "1" * 2000),
        ("zero", "0." + "0" * 2000),
        ("tiny", "0." + "0" * 2000 + "1"),
    ]
    items += [(f"integer_2p53_{offset}", str(2**53 + offset)) for offset in range(-3, 5)]
    for index, lower in enumerate(
        (math.nextafter(1.0, 0.0), 1.0, math.nextafter(1.0, math.inf), 2.0, 2**53, 1e100)
    ):
        upper = math.nextafter(lower, math.inf)
        midpoint = (Fraction.from_float(lower) + Fraction.from_float(upper)) / 2
        text = dyadic_decimal(midpoint)
        items.append((f"halfway_{index}", text))
        power = max(0, len(text.split(".")[1]) if "." in text else 0) + 5
        # Denominators after decimal perturbation also contain powers of five.
        # Format using a common decimal scale, avoiding any floating conversion.
        coefficient = midpoint * 10**power
        assert coefficient.denominator == 1
        for offset in (-1, 1):
            digits = str(coefficient.numerator + offset).zfill(power + 1)
            items.append(
                (f"near_halfway_{index}_{offset}", digits[:-power] + "." + digits[-power:])
            )
        if lower == 1.0:
            items.append(("halfway_remote_nonzero_tail", text + "0" * 2000 + "1"))
    overflow_midpoint = Fraction(2**1024 - 2**970)
    for offset in (-1, 0, 1):
        items.append((f"overflow_boundary_{offset}", str(overflow_midpoint.numerator + offset)))
    items += [
        ("subnormal_halfway", dyadic_decimal(Fraction(1, 2**1075))),
        ("smallest_subnormal", dyadic_decimal(Fraction(1, 2**1074))),
    ]
    return items


def bits(value: float) -> str:
    return f"{struct.unpack('>Q', struct.pack('>d', value))[0]:016x}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-root", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    load_reference(args.reference_root.resolve())
    from probability_calibration_tool.core.validation import parse_odds_text

    rows = [
        {
            "metadata": {
                "commit": BASELINE,
                "python": platform.python_version(),
                "reference": "frozen parse_odds_text and Python float(text)",
                "rounding": "binary64 round-to-nearest, ties-to-even",
                "representation": "IEEE-754 uint64 hexadecimal encoding",
            }
        }
    ]
    for name, text in cases():
        observed = observed_call(lambda text=text: parse_odds_text(text))
        converted = float(text)
        rows.append(
            {
                "case": name,
                "input": text,
                "expected": {
                    "status": observed.get("code", "ok"),
                    "bits": bits(converted),
                    "hex": converted.hex(),
                },
            }
        )
        if "value" in observed:
            assert bits(observed["value"]) == bits(converted)
    payload = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows).encode("ascii")
    if args.check:
        if OUTPUT.read_bytes() != payload:
            raise SystemExit("Exact decimal oracle differs from frozen reference")
        print(f"Verified {len(rows) - 1} exact decimal vectors")
    else:
        OUTPUT.write_bytes(payload)
        print(f"Wrote {len(rows) - 1} exact decimal vectors")


if __name__ == "__main__":
    main()
