import pytest

from rsaoaep.exceptions import DecryptionError, MessageTooLongError
from rsaoaep.rsa_core import decrypt, encrypt, generate_keypair


def test_keypair_and_round_trip():
    pair = generate_keypair(1024, rounds=12)
    message = b"test message"
    ciphertext = encrypt(message, pair.public_key, b"context")
    assert len(ciphertext) == pair.public_key.size_bytes
    assert decrypt(ciphertext, pair.private_key, b"context") == message


def test_oversized_message_rejected():
    pair = generate_keypair(1024, rounds=12)
    with pytest.raises(MessageTooLongError):
        encrypt(b"x" * 63, pair.public_key)


def test_invalid_ciphertext_length_and_range_rejected():
    pair = generate_keypair(1024, rounds=12)
    with pytest.raises(DecryptionError):
        decrypt(b"\x00", pair.private_key)
    with pytest.raises(DecryptionError):
        decrypt(pair.private_key.n.to_bytes(pair.private_key.size_bytes, "big"), pair.private_key)


def test_invalid_keygen_parameters():
    with pytest.raises(ValueError):
        generate_keypair(15)
    with pytest.raises(ValueError):
        generate_keypair(16)
    with pytest.raises(ValueError):
        generate_keypair(1024, public_exponent=2)
