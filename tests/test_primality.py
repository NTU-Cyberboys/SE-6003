import pytest

from rsaoaep.primality import generate_prime, is_probable_prime


@pytest.mark.parametrize("prime", [2, 3, 5, 97, 65537])
def test_primes(prime):
    assert is_probable_prime(prime, rounds=8)


@pytest.mark.parametrize("composite", [-1, 0, 1, 4, 9, 25, 341, 561])
def test_composites(composite):
    assert not is_probable_prime(composite, rounds=8)


def test_prime_generation_has_requested_width():
    prime = generate_prime(32, rounds=8)
    assert prime.bit_length() == 32
    assert prime % 2 == 1
    assert is_probable_prime(prime, rounds=8)


def test_invalid_rounds():
    with pytest.raises(ValueError):
        is_probable_prime(7, rounds=0)
