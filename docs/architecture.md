# Architecture

The implementation follows the RSAES-OAEP flow with SHA-256:

1. `primality.py` samples exact-width random odd candidates using `secrets`
   and screens them with small-prime trial division and Miller–Rabin.
2. `rsa_core.py` chooses two distinct primes, computes `n`, `phi(n)`, and the
   private exponent using the modular inverse in `math_utils.py`.
3. `oaep.py` encodes/decodes messages using SHA-256 and MGF1 from `mgf1.py`.
4. RSA public/private exponentiation uses Python's three-argument `pow`.
5. `serialization.py` stores key components as decimal integers in JSON;
   on POSIX systems private files are restricted to owner read/write
   permissions. On Windows, the file inherits the destination directory's
   access-control list (ACL); protect the containing directory accordingly.
6. `cli.py` exposes key generation, encryption, and decryption.

The RSA/OAEP design follows RFC 8017 (PKCS #1 v2.2), while using only
standard-library primitives. The implementation intentionally omits CRT
acceleration and blinding to keep the arithmetic understandable. It is not
constant-time and is not intended to protect production secrets.
