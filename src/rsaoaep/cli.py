from __future__ import annotations

import argparse
import base64
import binascii
import sys
from pathlib import Path

from .exceptions import RSAOAEPError
from .rsa_core import MINIMUM_KEY_BITS, decrypt, encrypt, generate_keypair
from .serialization import (
    load_private_key,
    load_public_key,
    save_private_key,
    save_public_key,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rsaoaep", description="Educational RSA-OAEP tool")
    commands = parser.add_subparsers(dest="command", required=True)

    keygen_parser = commands.add_parser("keygen", help="generate an RSA key pair")
    keygen_parser.add_argument("--bits", type=int, default=2048)
    keygen_parser.add_argument("--public-key", type=Path, required=True)
    keygen_parser.add_argument("--private-key", type=Path, required=True)

    encrypt_parser = commands.add_parser("encrypt", help="encrypt bytes using RSA-OAEP")
    encrypt_parser.add_argument("--key", type=Path, required=True)
    source = encrypt_parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--text")
    source.add_argument("--input", type=Path)
    encrypt_parser.add_argument("--label", default="")

    decrypt_parser = commands.add_parser("decrypt", help="decrypt base64 RSA-OAEP ciphertext")
    decrypt_parser.add_argument("--key", type=Path, required=True)
    ciphertext = decrypt_parser.add_mutually_exclusive_group(required=True)
    ciphertext.add_argument("--ciphertext")
    ciphertext.add_argument("--input", type=Path)
    decrypt_parser.add_argument("--label", default="")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "keygen":
            if args.public_key.resolve() == args.private_key.resolve():
                raise ValueError("public and private key paths must be different")
            if args.bits < MINIMUM_KEY_BITS:
                raise ValueError("RSA-OAEP with SHA-256 requires at least 528 key bits")
            pair = generate_keypair(args.bits)
            save_public_key(pair.public_key, args.public_key)
            save_private_key(pair.private_key, args.private_key)
            return 0
        if args.command == "encrypt":
            key = load_public_key(args.key)
            message = args.text.encode("utf-8") if args.text is not None else args.input.read_bytes()
            result = encrypt(message, key, args.label.encode("utf-8"))
            sys.stdout.write(base64.b64encode(result).decode("ascii") + "\n")
            return 0
        key = load_private_key(args.key)
        encoded = (
            args.ciphertext.encode("ascii")
            if args.ciphertext is not None
            else args.input.read_bytes().strip()
        )
        try:
            raw_ciphertext = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError("ciphertext must be valid base64") from exc
        plaintext = decrypt(raw_ciphertext, key, args.label.encode("utf-8"))
        sys.stdout.buffer.write(plaintext)
        return 0
    except (RSAOAEPError, OSError, ValueError, TypeError) as exc:
        print(f"rsaoaep: {exc}", file=sys.stderr)
        return 2
