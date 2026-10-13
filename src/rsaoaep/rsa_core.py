from .exceptions import DecryptionError
from .math_utils import gcd, mod_inverse
from .oaep import oaep_decode, oaep_encode
from .primality import generate_prime
from .types import PrivateKey, PublicKey, RSAKeyPair

DEFAULT_PUBLIC_EXPONENT = 65537


def generate_keypair(
    bits: int = 2048,
    public_exponent: int = DEFAULT_PUBLIC_EXPONENT,
    rounds: int = 40,
) -> RSAKeyPair:
    if public_exponent <= 1 or public_exponent % 2 == 0:
        raise ValueError("public exponent must be an odd integer greater than one")
    if bits < max(16, public_exponent.bit_length() + 1):
        raise ValueError("RSA key size is too small for the selected public exponent")
    p_bits = bits // 2
    q_bits = bits - p_bits
    while True:
        p = generate_prime(p_bits, rounds)
        q = generate_prime(q_bits, rounds)
        if p == q:
            continue
        modulus = p * q
        if modulus.bit_length() != bits:
            continue
        # RSA requires e*d == 1 mod phi(n).
        totient = (p - 1) * (q - 1)
        if gcd(public_exponent, totient) != 1:
            continue
        private_exponent = mod_inverse(public_exponent, totient)
        return RSAKeyPair(
            PublicKey(modulus, public_exponent),
            PrivateKey(modulus, private_exponent, public_exponent),
        )


def encrypt(message: bytes, public_key: PublicKey, label: bytes = b"") -> bytes:
    if not isinstance(message, bytes) or not isinstance(label, bytes):
        raise TypeError("message and label must be bytes")
    encoded = oaep_encode(message, public_key.size_bytes, label)
    message_number = int.from_bytes(encoded, "big")
    if message_number >= public_key.n:
        raise ValueError("encoded message is outside the RSA modulus")
    # RSAEP: c = m**e mod n.
    ciphertext_number = pow(message_number, public_key.e, public_key.n)
    return ciphertext_number.to_bytes(public_key.size_bytes, "big")


def decrypt(ciphertext: bytes, private_key: PrivateKey, label: bytes = b"") -> bytes:
    if not isinstance(ciphertext, bytes) or not isinstance(label, bytes):
        raise TypeError("ciphertext and label must be bytes")
    if len(ciphertext) != private_key.size_bytes:
        raise DecryptionError("decryption failed")
    ciphertext_number = int.from_bytes(ciphertext, "big")
    if ciphertext_number >= private_key.n:
        raise DecryptionError("decryption failed")
    # RSADP: recover the OAEP-encoded message representative.
    encoded_number = pow(ciphertext_number, private_key.d, private_key.n)
    encoded = encoded_number.to_bytes(private_key.size_bytes, "big")
    return oaep_decode(encoded, label)
