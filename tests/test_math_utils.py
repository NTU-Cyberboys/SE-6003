import pytest

from rsaoaep.math_utils import bytes_to_int, extended_gcd, gcd, int_to_bytes, mod_inverse


def test_gcd_and_extended_gcd():
    assert gcd(-54, 24) == 6
    divisor, x, y = extended_gcd(240, 46)
    assert divisor == 2
    assert 240 * x + 46 * y == divisor


def test_mod_inverse():
    assert mod_inverse(17, 3120) == 2753
    with pytest.raises(ValueError):
        mod_inverse(6, 15)
    with pytest.raises(ValueError):
        mod_inverse(2, 1)


def test_integer_byte_conversion():
    assert int_to_bytes(258, 2) == b"\x01\x02"
    assert bytes_to_int(b"\x01\x02") == 258
    with pytest.raises(ValueError):
        int_to_bytes(256, 1)
