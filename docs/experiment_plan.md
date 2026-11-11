# Experiment plan

## Questions

- How does key-generation time change with modulus size?
- How do RSA-OAEP encryption and decryption times change with modulus size?

## Method

Run `scripts/run_benchmarks.py` on one machine with Python 3.9+, using
1024-, 2048-, and 3072-bit keys by default. Each repeat independently creates
a fresh key pair, then times one encryption and one decryption of a fixed
short message. The CSV includes each measured operation in milliseconds.
report mean, median, and sample standard deviation across repeats; key
generation samples are separate from the per-key encryption/decryption
samples.

For reproducibility, record the exact command, repeat count, machine, and
date. Record the interpreter version with `python3 --version` on macOS/Linux
or `python --version` in an activated Windows virtual environment, together
with `platform.platform()`. Do not compare absolute timings from different
hosts as if they were controlled experiments. Key generation is
probabilistic, and scheduling and thermal state also affect results.

## Outputs and limitations

The runner writes `data/benchmark_results.csv`; the plotting script produces
an operation timing chart and a summary-statistics CSV. Timing is wall-clock
and implementation-specific. Results are not a security or side-channel
measurement. The 1024-bit size is included only to study scaling and is not
recommended for security.
