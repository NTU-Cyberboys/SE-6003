def gcd(a: int, b: int) -> int:
    """Return the greatest common divisor using Euclid's algorithm."""
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Return (g, x, y) such that a*x + b*y == g == gcd(a, b)."""
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    if old_r < 0:
        return -old_r, -old_s, -old_t
    return old_r, old_s, old_t


def mod_inverse(value: int, modulus: int) -> int:
    """Return the multiplicative inverse of value modulo modulus."""
    if modulus <= 1:
        raise ValueError("modulus must be greater than one")
    divisor, coefficient, _ = extended_gcd(value, modulus)
    if divisor != 1:
        raise ValueError("modular inverse does not exist")
    return coefficient % modulus


def int_to_bytes(value: int, length: int) -> bytes:
    if value < 0:
        raise ValueError("integer must be non-negative")
    if length < 0:
        raise ValueError("length must be non-negative")
    try:
        return value.to_bytes(length, "big")
    except OverflowError as exc:
        raise ValueError("integer does not fit in requested length") from exc


def bytes_to_int(value: bytes) -> int:
    return int.from_bytes(value, "big")
