import secrets

_SMALL_PRIMES = (
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37,
)


def is_probable_prime(candidate: int, rounds: int = 40) -> bool:
    """Miller–Rabin probable-prime test with cryptographically random bases."""
    if rounds < 1:
        raise ValueError("rounds must be positive")
    if candidate < 2:
        return False
    for prime in _SMALL_PRIMES:
        if candidate == prime:
            return True
        if candidate % prime == 0:
            return False
    if candidate % 2 == 0:
        return False

    # Write candidate - 1 as 2**powers_of_two * odd_part for Miller–Rabin.
    odd_part = candidate - 1
    powers_of_two = 0
    while odd_part % 2 == 0:
        powers_of_two += 1
        odd_part //= 2

    for _ in range(rounds):
        base = secrets.randbelow(candidate - 3) + 2
        witness = pow(base, odd_part, candidate)
        if witness in (1, candidate - 1):
            continue
        for _ in range(powers_of_two - 1):
            witness = pow(witness, 2, candidate)
            if witness == candidate - 1:
                break
        else:
            return False
    return True


def generate_prime(bits: int, rounds: int = 40) -> int:
    """Generate a probable prime with exactly `bits` bits."""
    if bits < 2:
        raise ValueError("prime size must be at least two bits")
    while True:
        # Force the top and bottom bits so the candidate has the requested width and is odd.
        candidate = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if is_probable_prime(candidate, rounds):
            return candidate
