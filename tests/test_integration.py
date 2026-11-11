import base64
import os
import stat

import pytest

from rsaoaep.cli import main
from rsaoaep.rsa_core import decrypt, encrypt, generate_keypair
from rsaoaep.serialization import (
    load_private_key,
    load_public_key,
    save_private_key,
    save_public_key,
)


def test_binary_round_trip_and_serialization(tmp_path):
    pair = generate_keypair(1024, rounds=12)
    public_path = tmp_path / "public.json"
    private_path = tmp_path / "private.json"
    save_public_key(pair.public_key, public_path)
    save_private_key(pair.private_key, private_path)
    public = load_public_key(public_path)
    private = load_private_key(private_path)
    message = b"\x00binary\xffpayload"
    assert decrypt(encrypt(message, public), private) == message


@pytest.mark.skipif(os.name != "posix", reason="POSIX private-key mode check")
def test_private_key_file_is_created_with_restrictive_permissions(tmp_path):
    pair = generate_keypair(1024, rounds=12)
    private_path = tmp_path / "private.json"

    save_private_key(pair.private_key, private_path)

    assert stat.S_IMODE(private_path.stat().st_mode) == 0o600


def test_cli_encrypt_decrypt(tmp_path, capsys):
    pair = generate_keypair(1024, rounds=12)
    public_path = tmp_path / "public.json"
    private_path = tmp_path / "private.json"
    save_public_key(pair.public_key, public_path)
    save_private_key(pair.private_key, private_path)
    assert main(["encrypt", "--key", str(public_path), "--text", "hello"]) == 0
    encoded = capsys.readouterr().out.strip()
    assert base64.b64decode(encoded)
    assert main(
        ["decrypt", "--key", str(private_path), "--ciphertext", encoded]
    ) == 0
    assert capsys.readouterr().out == "hello"
