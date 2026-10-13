class RSAOAEPError(Exception):
    """Base class for expected RSA-OAEP errors."""


class MessageTooLongError(RSAOAEPError, ValueError):
    """The message cannot fit in one OAEP-encoded block."""


class DecryptionError(RSAOAEPError, ValueError):
    """Ciphertext or OAEP encoding is invalid; details are intentionally hidden."""


class SerializationError(RSAOAEPError, ValueError):
    """A key file is malformed or contains invalid values."""
