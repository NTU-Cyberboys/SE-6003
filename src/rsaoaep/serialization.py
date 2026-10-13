from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .exceptions import SerializationError
from .types import PrivateKey, PublicKey


def public_key_to_dict(key: PublicKey) -> dict[str, str]:
    return {"type": "RSA-PUBLIC", "n": str(key.n), "e": str(key.e)}


def private_key_to_dict(key: PrivateKey) -> dict[str, str]:
    return {"type": "RSA-PRIVATE", "n": str(key.n), "e": str(key.e), "d": str(key.d)}


def save_public_key(key: PublicKey, path: str | Path) -> None:
    Path(path).write_text(json.dumps(public_key_to_dict(key), indent=2) + "\n", encoding="utf-8")


def save_private_key(key: PrivateKey, path: str | Path) -> None:
    destination = Path(path)
    destination.write_text(json.dumps(private_key_to_dict(key), indent=2) + "\n", encoding="utf-8")
    if os.name == "posix":
        # Windows permissions come from the directory ACL; chmod is POSIX-only here.
        try:
            os.chmod(destination, 0o600)
        except OSError as exc:
            raise SerializationError(f"could not restrict private key permissions: {exc}") from exc


def _read_object(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SerializationError(f"could not read key file: {exc}") from exc
    if not isinstance(value, dict):
        raise SerializationError("key file must contain a JSON object")
    return value


def _integer(value: Any, field: str) -> int:
    if not isinstance(value, str) or not value.isdecimal():
        raise SerializationError(f"key field {field!r} must be a decimal string")
    return int(value)


def load_public_key(path: str | Path) -> PublicKey:
    value = _read_object(path)
    if value.get("type") != "RSA-PUBLIC":
        raise SerializationError("key file is not an RSA public key")
    try:
        return PublicKey(_integer(value["n"], "n"), _integer(value["e"], "e"))
    except (KeyError, ValueError) as exc:
        raise SerializationError(f"invalid public key: {exc}") from exc


def load_private_key(path: str | Path) -> PrivateKey:
    value = _read_object(path)
    if value.get("type") != "RSA-PRIVATE":
        raise SerializationError("key file is not an RSA private key")
    try:
        return PrivateKey(
            _integer(value["n"], "n"),
            _integer(value["d"], "d"),
            _integer(value["e"], "e"),
        )
    except (KeyError, ValueError) as exc:
        raise SerializationError(f"invalid private key: {exc}") from exc
