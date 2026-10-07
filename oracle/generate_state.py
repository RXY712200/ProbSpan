"""Observe frozen application provenance and project only portable facts."""

import argparse
import json
from dataclasses import replace
from pathlib import Path

from generate import BASELINE, ROOT, load_reference, round_fixture, transition_vectors


def generate():
    from probability_calibration_tool.application import CalculateCommand

    records = list(transition_vectors())
    hidden = CalculateCommand(1, False, 60, "2", "2")
    with round_fixture(((1, 19, 1),)) as fixture:
        view = fixture.service.calculate(hidden)
        records.append(fixture.record("initial_hidden", hidden, view))
        visible = replace(hidden, reference_history=True)
        view = fixture.recalculate(view, visible)
        records.append(fixture.record("first_exposure_unchanged", visible, view))
    rows = []
    previous = None
    for record in records:
        expected = record["expected"]
        command = record["input"]["command"]
        if expected["revision_count"] == 0:
            previous = None
        old = previous["expected"] if previous else None
        old_command = previous["input"]["command"] if previous else command
        # The development adapter translates actual visible evidence, never
        # just the application's request flag. No UI vocabulary enters C.
        exposed_now = expected["history_display_state"] == "visible"
        if old is None and exposed_now:
            assert expected["history_exposed_at"] == record["input"]["at"]
        rows.append(
            {
                "case": record["case"],
                "previous": {
                    "exposed": old["history_exposed"] if old else False,
                    "compromised": old["subjective_independence_compromised"] if old else False,
                },
                "previous_raw": old_command["p_h_raw"],
                "current_raw": command["p_h_raw"],
                "subject_changed": old_command["character_id"] != command["character_id"],
                "evidence_exposed_now": exposed_now,
                "expected": {
                    "exposed": expected["history_exposed"],
                    "compromised": expected["subjective_independence_compromised"],
                },
            }
        )
        previous = record
    return {"reference_commit": BASELINE, "cases": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-root", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    load_reference(args.reference_root.resolve())
    data = generate()
    payload = (json.dumps(data, indent=2, sort_keys=True) + "\n").encode()
    target = ROOT / "state_reference.json"
    if args.check:
        if target.read_bytes() != payload:
            raise SystemExit("State reference is stale")
    else:
        target.write_bytes(payload)
    print(f"Verified/generated {len(data['cases'])} provenance cases")


if __name__ == "__main__":
    main()
