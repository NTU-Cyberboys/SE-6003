from dataclasses import dataclass


@dataclass(frozen=True)
class PublicKey:
    n: int
    e: int

    def __post_init__(self) -> None:
        if self.n <= 0 or self.e <= 1 or self.e >= self.n:
            raise ValueError("invalid RSA public key parameters")

    @property
    def size_bytes(self) -> int:
        return (self.n.bit_length() + 7) // 8


@dataclass(frozen=True)
class PrivateKey:
    n: int
    d: int
    e: int

    def __post_init__(self) -> None:
        if self.n <= 0 or self.d <= 0 or self.e <= 1 or self.e >= self.n:
            raise ValueError("invalid RSA private key parameters")

    @property
    def size_bytes(self) -> int:
        return (self.n.bit_length() + 7) // 8


@dataclass(frozen=True)
class RSAKeyPair:
    public_key: PublicKey
    private_key: PrivateKey
