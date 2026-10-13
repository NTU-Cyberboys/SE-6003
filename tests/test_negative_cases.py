import pytest

from rsaoaep.exceptions import DecryptionError, SerializationError
from rsaoaep.rsa_core import decrypt, encrypt, generate_keypair
from rsaoaep.serialization import load_public_key


def test_tampered_ciphertext_and_wrong_label():
    pair = generate_keypair(1024, rounds=12)
    ciphertext = encrypt(b"secret message", pair.public_key, b"label")
    altered = bytearray(ciphertext)
    altered[-1] ^= 1
    with pytest.raises(DecryptionError):
        decrypt(bytes(altered), pair.private_key, b"label")
    with pytest.raises(DecryptionError):
        decrypt(ciphertext, pair.private_key, b"other")


def test_malformed_serialized_key_rejected(tmp_path):
    key_path = tmp_path / "bad.json"
    key_path.write_text('{"type":"RSA-PUBLIC","n":42,"e":"3"}', encoding="utf-8")
    with pytest.raises(SerializationError):
        load_public_key(key_path)
