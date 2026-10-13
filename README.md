# RSA-OAEP

An educational Python package that implements RSA key generation and
RSAES-OAEP encryption using SHA-256 and MGF1. The project implements its own
RSA arithmetic, Miller–Rabin probable-prime test, and OAEP encoding/decoding.
The cryptographic package uses only the Python standard library; optional
development tools are used for tests, linting, and plots.

> **Security notice:** This project is for learning and coursework, not
> production. Python big-integer operations are not constant-time, and this
> implementation has no side-channel protections, blinding, CRT acceleration,
> or formal security review. Key JSON is unencrypted. Use a maintained
> cryptographic library for real secrets and production systems.

## Clone and install on Windows, macOS, or Linux

Python 3.9 or newer is required. The package itself has no third-party runtime
dependencies. The optional development install adds `pytest` and `ruff` for
testing/linting and `matplotlib` for benchmark plots. Use a virtual
environment so these tools and the package remain isolated from other Python
projects.

Clone the repository and change into its root:

```text
git clone <repository-url>
cd Crypto
```

Replace `<repository-url>` with the URL for your Git remote. Create and
install the environment using the instructions for your platform:

### Windows (PowerShell)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\ruff.exe check src tests scripts
```

The Windows Python Launcher (`py`) selects an installed Python 3 version.
Alternatively, replace `py -3` with `python` if that command points to Python
3.9 or newer. For Command Prompt, the virtual-environment executable is also
`.venv\Scripts\python.exe`; activation, if desired, is
`.venv\Scripts\activate.bat`.

### macOS or Linux

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m pytest
.venv/bin/ruff check src tests scripts
```

If your system provides versioned interpreters (for example `python3.15`),
use that command in place of `python3`. You can activate the environment with
`. .venv/bin/activate`; activation is optional when invoking the environment's
Python and Ruff paths directly as above.

The project does not require GNU Make. `Makefile` shortcuts are optional and
require `make` plus a compatible shell; the Python commands in this README
work without them. The implementation is pure Python and uses only
cross-platform standard-library features. It is intended for supported
mainstream Windows, macOS, and Linux systems with Python 3.9+; unusual Python
builds or platforms without compatible Python wheels for the optional
matplotlib dependency may omit chart generation.

To install only the runtime package instead of the development tools, replace
`".[dev]"` with `"."` in the pip install command.

For the remaining examples, activate the environment first if you want to use
the short `python`, `pytest`, `ruff`, and `rsaoaep` commands:

- PowerShell: `.\.venv\Scripts\Activate.ps1`
- Command Prompt: `.\.venv\Scripts\activate.bat`
- macOS/Linux: `. .venv/bin/activate`

Activation is optional. Without it, invoke the environment's Python directly:
`.venv\Scripts\python.exe` on Windows or `.venv/bin/python` on macOS/Linux.
This also avoids shell activation-policy configuration on Windows.

## Features and behavior

- Generates an RSA key pair from independently sampled, exact-width probable
  primes, using `secrets` for cryptographically appropriate randomness.
- Uses Miller–Rabin with 40 rounds by default and small-prime trial division.
- Computes the RSA modulus, public/private exponents, greatest common divisor,
  and modular inverse in project code; modular exponentiation uses Python's
  built-in big-integer `pow`.
- Implements RSAES-OAEP with SHA-256, MGF1, a random OAEP seed, and an optional
  application label.
- Encrypts/decrypts one short byte string per RSA operation. The package does
  not implement chunking, streaming, or a hybrid-encryption format.
- Rejects oversized messages, malformed or wrong-size ciphertexts, ciphertext
  integers outside the modulus, tampering, incorrect labels, and malformed
  OAEP encodings. Ciphertext/OAEP decoding failures share a generic
  `DecryptionError`.

For modulus width `k` bytes and SHA-256 digest length `hLen = 32`, the maximum
message size is `k - 2*hLen - 2`, or `k - 66` bytes. A modulus must be at least
66 bytes wide to encode even an empty message. The benchmark's fixed sample is
longer, so its key-size validation requires enough room for that full sample.

Public/private key objects are immutable dataclasses. Public keys are JSON
objects with type `RSA-PUBLIC` and decimal-string fields `n` and `e`; private
keys use type `RSA-PRIVATE` and fields `n`, `e`, and `d`. On POSIX systems,
private-key files are set to owner read/write permissions. On Windows, the
private-key file inherits the destination directory's access-control list
(ACL), so store it in a directory with appropriate access controls. Keys are
**not encrypted** on any platform.

## Command-line interface

The package installs an `rsaoaep` command and supports `python -m rsaoaep`.
The module form works in all shells and platforms and does not depend on the
installed script directory being on `PATH`. `--help` and each subcommand's
`--help` show the full argument list.

### Generate keys

```sh
python -m rsaoaep keygen --bits 2048 --public-key public.json --private-key private.json
```

The default key size is 2048 bits. Public and private key paths must differ.
For this SHA-256 OAEP CLI, key generation rejects sizes below 528 bits; that
minimum only permits an empty message and is not a security recommendation.

### Encrypt text or a binary file

```sh
python -m rsaoaep encrypt --key public.json --text "hello" > ciphertext.b64
python -m rsaoaep encrypt --key public.json --input message.bin --label "context" > ciphertext.b64
```

Specify exactly one of `--text` and `--input`. Text and labels are UTF-8
encoded; input files are read as raw bytes. Encryption writes base64 ciphertext
and a newline to standard output.

### Decrypt ciphertext

```sh
python -m rsaoaep decrypt --key private.json --input ciphertext.b64 --label "context" > recovered.bin
```

Specify exactly one of `--ciphertext` (base64 text) and `--input` (a file
containing base64 ciphertext). Decryption writes the original plaintext bytes
to standard output without adding a newline; redirect output for binary data.
The label must match the one used during encryption. Expected input/key errors
are printed to standard error and return exit status 2.

For ciphertext already copied as base64 text, pass it as
`--ciphertext BASE64_VALUE` in place of `--input ciphertext.b64`. The file
form is generally more convenient across shells.

## Python API

```python
from rsaoaep import decrypt, encrypt, generate_keypair

pair = generate_keypair(bits=2048)
ciphertext = encrypt(b"hello", pair.public_key, label=b"context")
plaintext = decrypt(ciphertext, pair.private_key, label=b"context")
assert plaintext == b"hello"
```

`generate_keypair(bits=2048)` returns an `RSAKeyPair` with `public_key` and
`private_key`. `encrypt(message, public_key, label=b"")` returns fixed-width
ciphertext bytes; `decrypt(ciphertext, private_key, label=b"")` returns
plaintext bytes. Messages, ciphertexts, and labels must be `bytes`. Key JSON
helpers are in `rsaoaep.serialization`. Expected validation exceptions are
defined in `rsaoaep.exceptions`; `MessageTooLongError`,
`DecryptionError`, and `SerializationError` are `ValueError` subclasses.

## Tests and lint

Run the complete suite and linter from the project root:

```sh
python -m pytest
ruff check src tests scripts
```

The tests cover integer arithmetic, modular inverses, probable primes and
composites, key generation, MGF1, OAEP round trips and size limits, binary
integration and serialization, CLI use, malformed keys, invalid ciphertext
length/range, tampering, and wrong labels.

The `Makefile` provides optional shortcuts: `make test`, `make lint`,
`make demo`, `make benchmark`, and `make plots`. These require `make` and use
`python`, `pytest`, and `ruff` from the active environment. On Windows without
Make, run the equivalent Python commands from this README.

## Demo

Run:

```sh
python scripts/run_demo.py
```

The demo creates a 1024-bit key pair, verifies a labeled in-memory round trip,
and writes key JSON and base64 ciphertext under `output/demo_artifacts/`.
The output directory is git-ignored because it contains a private key.

## Benchmarks and report outputs

The runner defaults to 1024-, 2048-, and 3072-bit keys, three repeats per
size, and `data/benchmark_results.csv`:

```sh
python scripts/run_benchmarks.py --bits 1024 2048 3072 --repeats 3
python scripts/plot_benchmarks.py
```

Each repeat generates a fresh key pair, then times one key generation, one
encryption, and one decryption of the same short sample. Measurements are
wall-clock milliseconds; CSV rows also record the Python and platform
versions. Plotting reads the measurements, writes median operation timings to
`output/charts/operation_timings.png`, and writes mean, median, and sample
standard deviation to `report/tables/benchmark_summary.csv`. The plotting
script requires the optional `matplotlib` development dependency.

The checked-in data currently has **one repeat per key size**, measured with
Python 3.15.0 on macOS 27.0.1 arm64. Those values are a smoke-test/example,
not a reliable performance comparison: one sample cannot characterize
variance, and key-generation time varies substantially with random prime
search. Run more repeats on the same machine before drawing conclusions.
1024-bit keys are included only for assignment-scale comparisons and are not
recommended for security. See [the experiment plan](docs/experiment_plan.md)
for reproducibility guidance.

Current outputs: [measurements](data/benchmark_results.csv),
[summary table](report/tables/benchmark_summary.csv), and
[timing chart](output/charts/operation_timings.png).

## Optional reference validation

`scripts/reference_validation.py` is an optional interoperability cross-check,
not part of the implementation or automated test suite. It requires
PyCryptodome to be installed separately and tests both directions of
RSA-OAEP/SHA-256 encryption against that independent library. The package,
tests, and benchmark scripts do not import or depend on PyCryptodome.

## Project map

```text
src/rsaoaep/       Package implementation and CLI
  types.py         Immutable public/private key dataclasses
  math_utils.py    GCD, extended GCD, modular inverse, integer/byte conversion
  primality.py     Miller–Rabin testing and probable-prime generation
  rsa_core.py      RSA key generation, encryption, and decryption
  mgf1.py          Mask Generation Function 1
  oaep.py          SHA-256 OAEP encoding/decoding and message-size limit
  serialization.py JSON key loading and saving
  exceptions.py    Package validation and decryption exceptions
  cli.py           argparse commands; __main__.py enables python -m rsaoaep
  benchmark.py     Benchmark collection and summary statistics
tests/             Unit, integration, CLI, and malformed-input tests
scripts/           Demo, benchmark, chart, and optional reference scripts
docs/              Architecture, interfaces, experiment plan, report outline
data/               Benchmark CSV and test-vector notes
output/              Generated charts and ignored demo artifacts
report/              Bibliography, draft/figure locations, generated tables
```

Additional project files: `pyproject.toml` defines packaging and the
`rsaoaep` entry point; `requirements.txt` lists developer tools;
`Makefile` provides common commands; `.gitignore` excludes environments,
caches, build products, and demo secrets; `LICENSE` contains the MIT license.
The RFC 8017 reference is recorded in [report/references.bib](report/references.bib).

Further design detail: [architecture](docs/architecture.md),
[interfaces](docs/interfaces.md), [experiment plan](docs/experiment_plan.md),
and [report outline](docs/report_outline.md).
