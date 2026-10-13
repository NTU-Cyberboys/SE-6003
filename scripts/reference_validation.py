"""Optional interoperability check; requires separately installed PyCryptodome."""

from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

from rsaoaep import decrypt, encrypt, generate_keypair


def main() -> None:
    message = b"independent interoperability check"
    pair = generate_keypair(1024)
    reference_private = RSA.construct(
        (pair.private_key.n, pair.private_key.e, pair.private_key.d)
    )
    reference_public = reference_private.publickey()
    own_cipher = encrypt(message, pair.public_key)
    reference_cipher = PKCS1_OAEP.new(reference_public, hashAlgo=SHA256).encrypt(message)
    if PKCS1_OAEP.new(reference_private, hashAlgo=SHA256).decrypt(own_cipher) != message:
        raise RuntimeError("reference implementation could not decrypt our ciphertext")
    if decrypt(reference_cipher, pair.private_key) != message:
        raise RuntimeError("our implementation could not decrypt reference ciphertext")
    print("Independent RSA-OAEP interoperability check passed.")


if __name__ == "__main__":
    main()
