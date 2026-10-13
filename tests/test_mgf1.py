import hashlib

import pytest

from rsaoaep.mgf1 import mgf1


def test_mgf1_sha256_known_prefix_and_length():
    expected = b"".join(
        hashlib.sha256(b"seed" + counter.to_bytes(4, "big")).digest()
        for counter in range(2)
    )
    assert mgf1(b"seed", 40) == expected[:40]
    assert mgf1(b"seed", 0) == b""


def test_mgf1_invalid_lengths():
    with pytest.raises(ValueError):
        mgf1(b"seed", -1)
    with pytest.raises(ValueError):
        mgf1(b"seed", 1, "not-a-real-hash")
