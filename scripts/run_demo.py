from __future__ import annotations

import argparse
import base64
from pathlib import Path

from rsaoaep import decrypt, encrypt, generate_keypair
from rsaoaep.oaep import maximum_message_length
from rsaoaep.serialization import save_private_key, save_public_key

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DIRECTORY = PROJECT_ROOT / "data" / "demo_inputs"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Encrypt and decrypt a small text or file with RSA-OAEP."
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--file", type=Path, help="file to encrypt instead of the examples")
    source.add_argument("--text", help="text to encrypt instead of the examples")
    parser.add_argument(
        "--bits",
        type=int,
        default=2048,
        help="RSA key size in bits (default: 2048)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "output" / "demo_artifacts",
        help="where to write keys, ciphertext, and recovered files",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = _parser()
    args = parser.parse_args(argv)
    if args.bits < 528:
        parser.error("RSA-OAEP with SHA-256 requires at least 528 key bits")

    if args.file is not None:
        try:
            inputs = [(args.file.name, args.file.read_bytes())]
        except OSError as exc:
            parser.error(f"could not read input file {args.file}: {exc}")
    elif args.text is not None:
        inputs = [("custom_text.txt", args.text.encode("utf-8"))]
    else:
        inputs = [
            (sample.name, sample.read_bytes())
            for sample in sorted(SAMPLE_DIRECTORY.iterdir())
            if sample.is_file()
        ]
        if not inputs:
            parser.error(f"no sample files found in {SAMPLE_DIRECTORY}")

    max_message_length = maximum_message_length((args.bits + 7) // 8)
    for name, message in inputs:
        if len(message) > max_message_length:
            parser.error(
                f"{name} is {len(message)} bytes; a {args.bits}-bit key can encrypt at most "
                f"{max_message_length} bytes in one RSA-OAEP operation. Try a larger --bits "
                "value or use a short test file."
            )

    # Fail on oversized input before the comparatively slow key-generation step.
    pair = generate_keypair(args.bits)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    save_public_key(pair.public_key, args.output_dir / "public.json")
    save_private_key(pair.private_key, args.output_dir / "private.json")

    for name, message in inputs:
        source = Path(name)
        # Keep the original file type on recovered output so it is easy to inspect.
        suffix = source.suffix or ".bin"
        stem = source.stem if source.suffix else source.name
        ciphertext = encrypt(message, pair.public_key)
        recovered = decrypt(ciphertext, pair.private_key)
        if recovered != message:
            raise RuntimeError(f"demo round-trip verification failed for {name}")

        (args.output_dir / f"{stem}.ciphertext.b64").write_text(
            base64.b64encode(ciphertext).decode("ascii") + "\n",
            encoding="ascii",
        )
        (args.output_dir / f"{stem}.recovered{suffix}").write_bytes(recovered)
        print(f"Round trip succeeded: {name} ({len(message)} bytes)")

    print(f"Keys and demo artifacts written to {args.output_dir}")
    print("The private key is for this demonstration only; do not use it for real secrets.")


if __name__ == "__main__":
    main()
