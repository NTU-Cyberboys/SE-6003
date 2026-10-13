# Architecture

The implementation follows RSAES-OAEP, the standardized form of the OAEP
construction introduced by Bellare and Rogaway [@bellareRogaway1994; @rfc8017].
Pointcheval discusses security considerations for properly using RSA
encryption [@pointcheval2002]; this project is an educational implementation,
not a claim to reproduce that analysis.

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

The encoding and decoding steps follow RFC 8017, sections 7.1.1 and 7.1.2
[@rfc8017], while using only standard-library primitives. The implementation
intentionally omits CRT acceleration and blinding to keep the arithmetic
understandable. It is not constant-time and is not intended to protect
production secrets.
