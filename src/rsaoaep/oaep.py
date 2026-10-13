import hashlib
import hmac
import secrets

from .exceptions import DecryptionError, MessageTooLongError
from .mgf1 import mgf1

HASH_NAME = "sha256"
HASH_LENGTH = hashlib.new(HASH_NAME).digest_size


def maximum_message_length(modulus_bytes: int) -> int:
    return modulus_bytes - 2 * HASH_LENGTH - 2


def oaep_encode(message: bytes, modulus_bytes: int, label: bytes = b"") -> bytes:
    max_length = maximum_message_length(modulus_bytes)
    if max_length < 0:
        raise ValueError("RSA modulus is too small for SHA-256 OAEP")
    if len(message) > max_length:
        raise MessageTooLongError(
            f"message is {len(message)} bytes; maximum is {max_length}"
        )
    # DB = lHash || zero padding || 0x01 || message, as specified by OAEP.
    label_hash = hashlib.new(HASH_NAME, label).digest()
    padding = b"\x00" * (max_length - len(message)) + b"\x01" + message
    seed = secrets.token_bytes(HASH_LENGTH)
    # Mask DB first, then mask the random seed using the masked DB.
    db_mask = mgf1(seed, modulus_bytes - HASH_LENGTH - 1, HASH_NAME)
    masked_db = bytes(a ^ b for a, b in zip(label_hash + padding, db_mask))
    seed_mask = mgf1(masked_db, HASH_LENGTH, HASH_NAME)
    masked_seed = bytes(a ^ b for a, b in zip(seed, seed_mask))
    return b"\x00" + masked_seed + masked_db


def oaep_decode(encoded: bytes, label: bytes = b"") -> bytes:
    if len(encoded) < 2 * HASH_LENGTH + 2:
        raise DecryptionError("decryption failed")
    if encoded[0] != 0:
        raise DecryptionError("decryption failed")
    masked_seed = encoded[1 : HASH_LENGTH + 1]
    masked_db = encoded[HASH_LENGTH + 1 :]
    seed_mask = mgf1(masked_db, HASH_LENGTH, HASH_NAME)
    seed = bytes(a ^ b for a, b in zip(masked_seed, seed_mask))
    db_mask = mgf1(seed, len(masked_db), HASH_NAME)
    data_block = bytes(a ^ b for a, b in zip(masked_db, db_mask))

    expected_label_hash = hashlib.new(HASH_NAME, label).digest()
    # Constant-time label-hash comparison; all decode failures share one error.
    label_matches = hmac.compare_digest(data_block[:HASH_LENGTH], expected_label_hash)
    padding = data_block[HASH_LENGTH:]
    delimiter = padding.find(b"\x01")
    if not label_matches or delimiter < 0 or any(byte != 0 for byte in padding[:delimiter]):
        raise DecryptionError("decryption failed")
    return padding[delimiter + 1 :]
