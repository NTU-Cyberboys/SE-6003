from pathlib import Path

import pytest

from rsaoaep.rsa_core import generate_keypair
from scripts import run_demo


@pytest.fixture
def fast_keygen(monkeypatch):
    monkeypatch.setattr(
        run_demo,
        "generate_keypair",
        lambda bits: generate_keypair(bits, rounds=12),
    )


def test_demo_round_trips_sample_files(tmp_path, fast_keygen):
    output = tmp_path / "artifacts"

    run_demo.main(["--bits", "1024", "--output-dir", str(output)])

    for name in ("hello.txt", "settings.json", "values.csv"):
        sample = run_demo.SAMPLE_DIRECTORY / name
        recovered = output / f"{Path(name).stem}.recovered{Path(name).suffix}"
        assert recovered.read_bytes() == sample.read_bytes()
        assert (output / f"{Path(name).stem}.ciphertext.b64").is_file()
    assert (output / "public.json").is_file()
    assert (output / "private.json").is_file()


def test_demo_accepts_custom_text(tmp_path, fast_keygen):
    output = tmp_path / "artifacts"

    run_demo.main(
        ["--bits", "1024", "--output-dir", str(output), "--text", "a short custom message"]
    )

    assert (output / "custom_text.recovered.txt").read_bytes() == b"a short custom message"


def test_demo_accepts_custom_file(tmp_path, fast_keygen):
    source = tmp_path / "input.txt"
    source.write_bytes(b"custom file input\x00")
    output = tmp_path / "artifacts"

    run_demo.main(
        ["--bits", "1024", "--file", str(source), "--output-dir", str(output)]
    )

    assert (output / "input.recovered.txt").read_bytes() == source.read_bytes()


def test_demo_explains_oversized_input_before_key_generation(tmp_path, monkeypatch, capsys):
    source = tmp_path / "too-large.txt"
    source.write_bytes(b"x" * 63)

    def unexpected_key_generation(bits):
        raise AssertionError("key generation should not run for oversized input")

    monkeypatch.setattr(run_demo, "generate_keypair", unexpected_key_generation)
    with pytest.raises(SystemExit) as exc_info:
        run_demo.main(["--bits", "1024", "--file", str(source)])

    assert exc_info.value.code == 2
    assert "can encrypt at most 62 bytes" in capsys.readouterr().err
