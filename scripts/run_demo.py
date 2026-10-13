import base64
from pathlib import Path

from rsaoaep import decrypt, encrypt, generate_keypair
from rsaoaep.serialization import save_private_key, save_public_key


def main() -> None:
    output = Path("output/demo_artifacts")
    output.mkdir(parents=True, exist_ok=True)
    pair = generate_keypair(1024)
    message = b"RSA-OAEP project demonstration"
    label = b"demo"
    ciphertext = encrypt(message, pair.public_key, label)
    recovered = decrypt(ciphertext, pair.private_key, label)
    if recovered != message:
        raise RuntimeError("demo round-trip verification failed")
    save_public_key(pair.public_key, output / "public.json")
    save_private_key(pair.private_key, output / "private.json")
    (output / "ciphertext.b64").write_text(
        base64.b64encode(ciphertext).decode("ascii") + "\n",
        encoding="ascii",
    )
    print(f"RSA-OAEP round trip succeeded; artifacts written to {output}")


if __name__ == "__main__":
    main()
