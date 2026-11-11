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

## Setup on Windows, macOS, or Linux

Python 3.9 or newer is required, matching the minimum declared in
`pyproject.toml`. This does not guarantee compatibility with every past or
future Python 3 release; use a currently supported Python 3 version and run
the tests when changing interpreters. The project is intended for mainstream
Windows, macOS, and Linux systems, but unusual operating systems or Python
builds may need separate validation.

The package itself has no third-party runtime dependencies. The optional
development install adds `pytest` and `ruff` for testing/linting and
`matplotlib` for benchmark plots. Use a virtual environment so these tools
and the package remain isolated from other Python projects. Run the setup
commands in the same terminal; activation keeps the environment enabled for
the demo and the commands that follow.

Download the project from [GitHub](https://github.com/NTU-Cyberboys/SE-6003):

```sh
git clone https://github.com/NTU-Cyberboys/SE-6003.git
cd SE-6003
```

Or select **Code → Download ZIP** on the GitHub page and open a terminal in
the extracted `SE-6003` folder. Then run the setup commands for your platform:

### Windows (PowerShell)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

The Windows Python Launcher (`py -3`) selects an installed Python 3 version.
After activation, `python` refers to that Python 3 virtual environment. If
PowerShell blocks the activation script, use Command Prompt instead. Run all
three commands in the same Command Prompt window:

```bat
py -3 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -e ".[dev]"
```

### macOS or Linux

```sh
python3 -m venv .venv && . .venv/bin/activate && python3 -m pip install -e ".[dev]"
```

If your system provides versioned interpreters (for example `python3.15`),
use that command in place of `python3` when creating the environment.
The commands below use `python3` on macOS/Linux. Windows does not
consistently provide a `python3` command, so use `python` after activating
the venv; `py -3` selects Python 3 when creating it.

## Run the demo

From the activated environment, run the demo to encrypt and decrypt the
included text, JSON, and CSV examples:

```sh
python3 scripts/run_demo.py
```

On Windows, `python3` is not consistently available as a command. In
PowerShell, use `python scripts/run_demo.py`; after activation, this is the
Python 3 interpreter inside the virtual environment. To try your own content,
pass a short UTF-8 message or a file path:

```sh
python3 scripts/run_demo.py --text "Try encrypting my own text"
python3 scripts/run_demo.py --file /path/to/your/file.txt
```

In PowerShell, use `python` instead of `python3` for the custom-input
commands. The demo stores the generated keys, base64 ciphertext, and recovered
file in `output/demo_artifacts/` (or in a directory passed with `--output-dir`).
The default 2048-bit key accepts up to 190 bytes per input. The demo explains
the limit before generating keys; increase it with `--bits` for a larger
single-message limit. RSA-OAEP here handles one short message at a time; it
does not stream or encrypt arbitrarily large files. The generated private key
is unencrypted and is only for learning.

For a runtime-only install, replace `".[dev]"` with `"."` in the pip install
command. The project does not require GNU Make; its shortcuts are optional.
It uses Python's cross-platform standard library, while chart generation
needs the optional `matplotlib` dependency installed by the development setup.

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

The package installs an `rsaoaep` command and supports `python3 -m rsaoaep`.
The module form works in all shells and platforms and does not depend on the
installed script directory being on `PATH`. `--help` and each subcommand's
`--help` show the full argument list.

### Generate keys

```sh
python3 -m rsaoaep keygen --bits 2048 --public-key public.json --private-key private.json
```

The default key size is 2048 bits. Public and private key paths must differ.
For this SHA-256 OAEP CLI, key generation rejects sizes below 528 bits; that
minimum only permits an empty message and is not a security recommendation.

### Encrypt text or a binary file

```sh
python3 -m rsaoaep encrypt --key public.json --text "hello" > ciphertext.b64
python3 -m rsaoaep encrypt --key public.json --input message.bin --label "context" > ciphertext.b64
```

Specify exactly one of `--text` and `--input`. Text and labels are UTF-8
encoded; input files are read as raw bytes. Encryption writes base64 ciphertext
and a newline to standard output.

### Decrypt ciphertext

```sh
python3 -m rsaoaep decrypt --key private.json --input ciphertext.b64 --label "context" > recovered.bin
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
python3 -m pytest
ruff check src tests scripts
```

The tests cover integer arithmetic, modular inverses, probable primes and
composites, key generation, MGF1, OAEP round trips and size limits, binary
integration and serialization, CLI use, malformed keys, invalid ciphertext
length/range, tampering, and wrong labels.

The `Makefile` provides optional shortcuts: `make test`, `make lint`,
`make demo`, `make benchmark`, and `make plots`. These require `make` and use
`python3`, `pytest`, and `ruff` from the active environment. On Windows without
Make, run the equivalent Python commands from this README.

## Benchmarks and report outputs

The runner defaults to 1024-, 2048-, and 3072-bit keys, three repeats per
size, and `data/benchmark_results.csv`:

```sh
python3 scripts/run_benchmarks.py --bits 1024 2048 3072 --repeats 3
python3 scripts/plot_benchmarks.py
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
  cli.py           argparse commands; __main__.py enables python3 -m rsaoaep
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
The bibliography records the original OAEP paper by Bellare and Rogaway,
Pointcheval's RSA-encryption discussion, and the normative RFC 8017
specification in [report/references.bib](report/references.bib). The
implementation is original project code following the published OAEP
construction and standard; it does not copy source code from those works.

Further design detail: [architecture](docs/architecture.md),
[interfaces](docs/interfaces.md), [experiment plan](docs/experiment_plan.md),
and [report outline](docs/report_outline.md).
