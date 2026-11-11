# Interfaces

The public Python interface is exported from `rsaoaep`:

- `generate_keypair(bits=2048)` returns an `RSAKeyPair`.
- `encrypt(message, public_key, label=b"")` returns a fixed-width ciphertext.
- `decrypt(ciphertext, private_key, label=b"")` returns plaintext bytes.
- `PublicKey`, `PrivateKey`, and `RSAKeyPair` are immutable dataclasses.
- Key JSON can be read or written with the helpers in `rsaoaep.serialization`.

Messages and labels are byte strings. Text callers should encode/decode UTF-8
explicitly. OAEP requires a modulus at least 66 bytes wide for SHA-256; the
usable message size is the modulus width minus 66 bytes. Key generation
requires at least 528 bits, matching that minimum OAEP width.

The CLI accepts UTF-8 text or a binary input file for encryption. Ciphertext
is base64-encoded for transport. Decryption writes raw bytes to standard
output. CLI labels are UTF-8 strings. The installed CLI is available after
installation on Windows, macOS, and Linux. Module invocation is
`python3 -m rsaoaep` on macOS/Linux and `python -m rsaoaep` in an activated
Windows virtual environment.

Private-key files are restricted to owner read/write permissions on POSIX
systems. On Windows they inherit the destination directory's access-control
list (ACL); store them in a directory with appropriate access controls.

`ValueError` subclasses in `rsaoaep.exceptions` communicate invalid input.
Malformed ciphertext and OAEP failures use `DecryptionError` to avoid
revealing which OAEP check failed.
