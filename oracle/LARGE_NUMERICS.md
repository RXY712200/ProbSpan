# Step 2 large-parameter numerical reference exception

Ordinary v1 behavior remains frozen against Python commit
`a581f84ccd217ed45789b3566347255f56ffbeac`. Neither `v1_vectors.jsonl` nor its
tolerances have changed.

The separately authorized `large_reference.json` covers the extreme parameter
region where frozen SciPy becomes internally inconsistent, together with
boundary controls. For example, SciPy 1.18.1 at 10^18 counts per side returns
complementary CDF values summing to 1.4772498761078805 and evaluates its own
2.5% quantile to a CDF of 7.946485460111386e-51. At 10^12 counts per side,
complementary CDF values already disagree by about 3e-6. Finite output alone
does not establish a usable reference in this region.

The exception changes numerical evaluation only. The Jeffreys shapes remain
`events+0.5` and `complements+0.5`, the mean remains `alpha/(alpha+beta)`, and
the interval remains the central 95% Beta interval. Versions, state rules,
and the readiness gate are unchanged. It is not a new input-domain boundary.

## Reference generation

`generate_large.py` uses development-only mpmath 1.3.0 at 80 decimal digits.
It integrates the exact log-gamma-normalized Beta density using mpmath's
adaptive tanh-sinh quadrature, after a standardized logit substitution.
Safeguarded Newton iteration solves for both quantiles. The integration
limits +/-256 omit less than 1e-78 probability for the covered shapes.
The generator verifies normalization, inverse CDF residuals below 1e-40,
monotonicity, symmetry, and complementary probabilities. A separate 60-digit
run agrees with all stored expectations when rounded to binary64.

Public historical expectations use exact integer counts plus 0.5. Private CDF
probes use the exact real values represented by the C primitive's binary64
shape and x arguments: applying an invariant to different, rounded arguments
would otherwise introduce a misleading discrepancy for extremely narrow
distributions. Metadata records both conventions, formulas, tool, precision,
method, and unchanged 1e-10 absolute plus 1e-10 relative parity tolerance.

Reproduce from the repository root:

```text
uv run --with mpmath==1.3.0 python oracle/generate_large.py --check
uv run --with mpmath==1.3.0 python oracle/generate_large.py --verify-precision
uv run python tests/generate_large_fixtures.py --check
```

## Runtime strategy and tests

The ordinary continued fraction remains in `src/beta.c`. For shapes at least
0.5 and their sum above 10,000, `src/beta_logit.c` integrates the same Beta law
using adaptive 16-point Gauss-Legendre panels. This strategy threshold avoids
gamma-normalization cancellation and slow continued-fraction convergence;
it does not select a different model or reject counts. Stirling remainders
evaluate normalization without subtracting large log-gamma values. Quantile
iteration runs in the scaled logit coordinate; compensated arithmetic retains
the mean and conversion roundoff. The C library has no Python, SciPy, or
mpmath runtime dependency.

`large_numerics.c` checks 28 public histories and 140 independent CDF probes
against the corrected reference. It also checks 190 public histories,
570 private quantiles, and 950 primary CDF evaluations, plus their inverse and
complementary brackets, over magnitudes 10^4 through 10^18, adjacent to 2^53,
and INT64_MAX. Original ordinary parity tests remain unchanged.

For binary64 quantiles, CDF(q) can differ substantially from the target
probability when one representable x step spans substantial probability mass
or a skewed interval rounds to 1. Tests therefore require neighboring-double
CDFs to bracket the target, with probability tolerance 1e-10. Complementary
identities use the same bracket rule when subtraction from one rounds the
argument. High-precision generation checks the identities directly.

Full numerical and compatibility contracts are in [Numerical contract](../docs/NUMERICAL_CONTRACT.md)
and [Compatibility](../docs/COMPATIBILITY.md). The final reentrancy audit extracted
the shared Stirling remainder and removed hidden signgam effects from log-Gamma
evaluation; the accepted model, references, tolerances, and stress cases remain unchanged.

## Status in v1.0.0

The high-precision large-parameter reference is part of the **accepted v1.0 numerical contract**, not a future alternative probability model. Its derivation and limitations are specified in [Numerical contract](../docs/NUMERICAL_CONTRACT.md). Further stress coverage must be added as separate reproducible cases without changing the frozen Jeffreys, gate, or model-version behavior.
