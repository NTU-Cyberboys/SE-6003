import pytest

from rsaoaep.exceptions import DecryptionError, MessageTooLongError
from rsaoaep.oaep import HASH_LENGTH, maximum_message_length, oaep_decode, oaep_encode


def test_oaep_encode_decode():
    message = b"hello oaep"
    encoded = oaep_encode(message, 128, b"label")
    assert len(encoded) == 128
    assert oaep_decode(encoded, b"label") == message


def test_oaep_maximum_message_and_small_modulus():
    assert maximum_message_length(128) == 128 - 2 * HASH_LENGTH - 2
    max_message = b"x" * maximum_message_length(128)
    assert oaep_decode(oaep_encode(max_message, 128)) == max_message
    with pytest.raises(MessageTooLongError):
        oaep_encode(max_message + b"x", 128)
    with pytest.raises(ValueError):
        oaep_encode(b"", 65)


def test_oaep_wrong_label_and_malformed_padding():
    encoded = oaep_encode(b"message", 128, b"correct")
    with pytest.raises(DecryptionError):
        oaep_decode(encoded, b"wrong")
    with pytest.raises(DecryptionError):
        oaep_decode(b"\x00" * 128)
    with pytest.raises(DecryptionError):
        oaep_decode(b"\x01" + encoded[1:])
