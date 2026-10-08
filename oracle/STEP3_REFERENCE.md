# Step 3 reference additions

`analysis_vectors.jsonl` supplements the unchanged original oracle. Its 920
additional rows execute the frozen Python core at
`a581f84ccd217ed45789b3566347255f56ffbeac`: all 101 subjective inputs with seven
odds pairs, S boundary geometry, 12 ordinary histories, validation ordering,
and epsilon boundaries. The C fixture also consumes every original Step 3
oracle group, including the full 3-by-4 model-relation table.

`threshold_reference.json` contains 18 focused analyses from six large
histories, with thresholds at/near posterior centers. Generation uses the
accepted mpmath 1.3.0 80-digit methodology from Step 2. It executes frozen EV,
state, and gate code with independent high-precision quantiles and CDFs
substituted only for the inconsistent SciPy numerical evaluators. Metadata
records formulas, precision, tool, and the existing exception. Ordinary rows
and all numerical tolerances remain unchanged.

At 9,223,372,036,854,775 events and INT64_MAX complements, frozen SciPy 1.18.1
returns NaN interval endpoints. That makes the frozen gate report insufficient
history despite the mathematical posterior being narrow. Corrected quantiles
restore the intended finite interval; the gate formula itself is unchanged.
High-precision CDFs evaluate exact represented binary64 thresholds and shapes,
so rounding an odds-derived threshold is not mistaken for a numerical defect.

Run the following in the frozen reference environment (paths to ProbSpan
scripts may be absolute):

```text
python oracle/generate_analysis.py --reference-root <frozen-checkout> --check
uv run --with mpmath==1.3.0 python oracle/generate_threshold.py --reference-root <frozen-checkout> --check
python tests/generate_analysis_fixtures.py --check
```

Generation never uses C outputs as expected values. Committed C fixtures need
no Python to compile or run. Shared logit and Jeffreys-shape helpers preserve
Step 2's exact arithmetic while avoiding duplicate formulas in the new layer.
Full documentation is now in [Behavior specification](../docs/BEHAVIOR_SPEC.md),
[Numerical contract](../docs/NUMERICAL_CONTRACT.md), and [Testing](../docs/TESTING.md).

## Release status

These Step 3 reference additions are frozen in the v1.0.0 release. They confirm that subjective and historical EV decisions remain independent and that large-parameter threshold evaluations use only the explicitly authorized corrected numerical reference. See [Behavior specification](../docs/BEHAVIOR_SPEC.md), [Testing](../docs/TESTING.md), and [Numerical contract](../docs/NUMERICAL_CONTRACT.md).
