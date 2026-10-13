import hashlib


def mgf1(seed: bytes, mask_length: int, hash_name: str = "sha256") -> bytes:
    """Generate a mask using MGF1 and the named hashlib digest."""
    if mask_length < 0:
        raise ValueError("mask length must be non-negative")
    digest_size = hashlib.new(hash_name).digest_size
    if mask_length > (1 << 32) * digest_size:
        raise ValueError("mask length exceeds MGF1 counter limit")
    blocks = []
    # MGF1 hashes seed || counter, with a four-byte big-endian counter.
    for counter in range((mask_length + digest_size - 1) // digest_size):
        digest = hashlib.new(hash_name, seed + counter.to_bytes(4, "big")).digest()
        blocks.append(digest)
    return b"".join(blocks)[:mask_length]
