"""Generate the Step 2 C parity fixture from the committed JSONL oracle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORACLE = ROOT / "oracle" / "v1_vectors.jsonl"
POLICY = ROOT / "oracle" / "numerical_policy.json"
OUTPUT = ROOT / "tests" / "oracle_fixtures.h"

HISTORY_STATES = {
    "no_history": "PROBSPAN_NO_HISTORY",
    "insufficient": "PROBSPAN_INSUFFICIENT",
    "valid": "PROBSPAN_VALID",
}
VALIDATION_CODES = {
    "raw_probability": "PROBSPAN_RAW_PROBABILITY",
    "odds_syntax": "PROBSPAN_ODDS_SYNTAX",
    "odds_range": "PROBSPAN_ODDS_RANGE",
    "unknown": None,
}


def c_float(value: float) -> str:
    result = repr(float(value))
    return result if "." in result or "e" in result else result + ".0"


def c_string(value: str) -> str:
    # Hex bytes keep the fixture source ASCII even for rejected Unicode inputs.
    return '"' + "".join(f"\\x{byte:02x}" for byte in value.encode("utf-8")) + '"'


def status(row: dict) -> str:
    expected = row["expected"]
    if "error" not in expected:
        return "PROBSPAN_OK"
    code = VALIDATION_CODES[expected["code"]]
    if code is not None:
        return code
    if row["group"] == "subjective_width_validation":
        return "PROBSPAN_SUBJECTIVE_DOMAIN"
    if row["group"] == "history_validation":
        return "PROBSPAN_HISTORY_COUNTS"
    raise ValueError(f"Unmapped oracle error: {row['group']} {row['case']}")


def rows_by_group(rows: list[dict], group: str) -> list[dict]:
    selected = [row for row in rows if row["group"] == group]
    if not selected:
        raise ValueError(f"Missing oracle group: {group}")
    return selected


def emit_constants(rows: list[dict], lines: list[str]) -> None:
    constants = rows_by_group(rows, "constants")
    if len(constants) != 1:
        raise ValueError("Expected one frozen constants record")
    for name, value in sorted(constants[0]["expected"].items()):
        lines.append(f"#define ORACLE_{name} {c_float(value)}")


def emit_subjective(rows: list[dict], lines: list[str]) -> None:
    lines.append(
        "typedef struct { int raw, used; double probability, lower, upper, width; int version; } subjective_case;"
    )
    lines.append("static const subjective_case subjective_cases[] = {")
    for row in rows_by_group(rows, "subjective"):
        item = row["expected"]
        lines.append(
            "    {"
            + ", ".join(
                (
                    str(item["p_h_raw"]),
                    str(item["p_h_used"]),
                    c_float(item["probability"]),
                    c_float(item["p_min"]),
                    c_float(item["p_max"]),
                    c_float(item["logit_half_width"]),
                    str(item["model_version"]),
                )
            )
            + "},"
        )
    lines.append("};")

    lines.append("typedef struct { double probability, width; } width_case;")
    lines.append("static const width_case width_cases[] = {")
    for row in rows_by_group(rows, "subjective_width"):
        lines.append(f"    {{{c_float(row['input']['probability'])}, {c_float(row['expected'])}}},")
    lines.append("};")

    lines.append("typedef struct { int raw; probspan_status status; } raw_validation_case;")
    lines.append("static const raw_validation_case raw_validation_cases[] = {")
    for row in rows_by_group(rows, "subjective_validation"):
        lines.append(f"    {{{row['input']['p_h_raw']}, {status(row)}}},")
    lines.append("};")

    lines.append(
        "typedef struct { double probability; probspan_status status; } width_validation_case;"
    )
    lines.append("static const width_validation_case width_validation_cases[] = {")
    for row in rows_by_group(rows, "subjective_width_validation"):
        lines.append(f"    {{{c_float(row['input']['probability'])}, {status(row)}}},")
    lines.append("};")


def emit_history(rows: list[dict], lines: list[str]) -> None:
    lines.append(
        "typedef struct { int64_t events, complements; uint64_t size; probspan_history_state state; bool ready, available; double probability, lower, upper; int model_version, gate_version; } history_case;"
    )
    lines.append("static const history_case history_cases[] = {")
    for row in rows_by_group(rows, "history"):
        item = row["expected"]
        available = item["probability"] is not None
        fields = (
            str(item["wins"]),
            str(item["losses"]),
            str(item["sample_size"]),
            HISTORY_STATES[item["status"]],
            "true" if item["statistically_ready"] else "false",
            "true" if available else "false",
            c_float(item["probability"] if available else 0.0),
            c_float(item["lower"] if available else 0.0),
            c_float(item["upper"] if available else 0.0),
            str(item["model_version"]),
            str(item["gate_version"]),
        )
        lines.append("    {" + ", ".join(fields) + "},")
    lines.append("};")

    lines.append(
        "typedef struct { int64_t events, complements; probspan_status status; } history_validation_case;"
    )
    lines.append("static const history_validation_case history_validation_cases[] = {")
    for row in rows_by_group(rows, "history_validation"):
        lines.append(f"    {{{row['input']['wins']}, {row['input']['losses']}, {status(row)}}},")
    lines.append("};")


def emit_odds(rows: list[dict], lines: list[str]) -> None:
    lines.append(
        "typedef struct { const char *text; probspan_status status; double value; } odds_text_case;"
    )
    lines.append("static const odds_text_case odds_text_cases[] = {")
    for row in rows_by_group(rows, "odds_parse"):
        value = row["expected"].get("value", 0.0)
        lines.append(f"    {{{c_string(row['input']['text'])}, {status(row)}, {c_float(value)}}},")
    lines.append("};")

    lines.append(
        "typedef struct { double input; probspan_status status; double value; } odds_numeric_case;"
    )
    lines.append("static const odds_numeric_case odds_numeric_cases[] = {")
    for row in rows_by_group(rows, "odds_numeric"):
        value = row["input"]["odds"]
        # Python-only dynamic types do not correspond to the C double API.
        if (
            value is None
            or isinstance(value, bool)
            or (isinstance(value, str) and value not in ("nan", "infinity"))
        ):
            continue
        input_literal = {"nan": "NAN", "infinity": "INFINITY"}.get(value)
        if input_literal is None:
            input_literal = c_float(value)
        expected_value = row["expected"].get("value", 0.0)
        lines.append(f"    {{{input_literal}, {status(row)}, {c_float(expected_value)}}},")
    lines.append("};")


def render() -> bytes:
    rows = [json.loads(line) for line in ORACLE.read_text(encoding="utf-8").splitlines()]
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    lines = [
        "/* GENERATED from oracle/v1_vectors.jsonl by tests/generate_fixtures.py. Do not edit. */",
        "#ifndef PROBSPAN_ORACLE_FIXTURES_H",
        "#define PROBSPAN_ORACLE_FIXTURES_H",
        "#include <math.h>",
        "#include <stdbool.h>",
        "#include <stdint.h>",
        '#include "probspan/probspan.h"',
        f"#define ORACLE_ELEMENTARY_ABS_TOL {c_float(policy['elementary_binary64']['absolute_tolerance'])}",
        f"#define ORACLE_ELEMENTARY_REL_TOL {c_float(policy['elementary_binary64']['relative_tolerance'])}",
        f"#define ORACLE_BETA_ABS_TOL {c_float(policy['scipy_beta_cdf_ppf']['absolute_tolerance'])}",
        f"#define ORACLE_BETA_REL_TOL {c_float(policy['scipy_beta_cdf_ppf']['relative_tolerance'])}",
    ]
    emit_constants(rows, lines)
    emit_subjective(rows, lines)
    emit_history(rows, lines)
    emit_odds(rows, lines)
    lines.append("#endif")
    return ("\n".join(lines) + "\n").encode("ascii")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = render()
    if args.check:
        if OUTPUT.read_bytes() != generated:
            raise SystemExit("Generated C fixture is stale")
        print("Generated C fixture is current")
    else:
        OUTPUT.write_bytes(generated)
        print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
