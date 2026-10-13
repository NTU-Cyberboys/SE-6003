from __future__ import annotations

import csv
import platform
import statistics
import time
from pathlib import Path

from .rsa_core import decrypt, encrypt, generate_keypair


def run_benchmarks(
    key_sizes: list[int],
    repeats: int = 3,
    output: str | Path = "data/benchmark_results.csv",
) -> list[dict[str, object]]:
    if repeats < 1:
        raise ValueError("repeats must be positive")
    message = b"RSA-OAEP benchmark sample"
    minimum_bytes = len(message) + 2 * 32 + 2
    if not key_sizes or any((bits + 7) // 8 < minimum_bytes for bits in key_sizes):
        raise ValueError(
            f"key sizes must be non-empty and fit a {len(message)}-byte message with SHA-256 OAEP"
        )
    rows: list[dict[str, object]] = []
    for bits in key_sizes:
        for repeat in range(1, repeats + 1):
            start = time.perf_counter()
            pair = generate_keypair(bits)
            keygen_ms = (time.perf_counter() - start) * 1000
            start = time.perf_counter()
            ciphertext = encrypt(message, pair.public_key)
            encryption_ms = (time.perf_counter() - start) * 1000
            start = time.perf_counter()
            recovered = decrypt(ciphertext, pair.private_key)
            decryption_ms = (time.perf_counter() - start) * 1000
            if recovered != message:
                raise RuntimeError("benchmark round-trip verification failed")
            rows.append(
                {
                    "key_bits": bits,
                    "repeat": repeat,
                    "keygen_ms": f"{keygen_ms:.6f}",
                    "encrypt_ms": f"{encryption_ms:.6f}",
                    "decrypt_ms": f"{decryption_ms:.6f}",
                    "python": platform.python_version(),
                    "platform": platform.platform(),
                }
            )
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def summarize(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[int, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(int(row["key_bits"]), []).append(row)
    summary = []
    for bits, samples in sorted(grouped.items()):
        for operation in ("keygen_ms", "encrypt_ms", "decrypt_ms"):
            values = [float(sample[operation]) for sample in samples]
            summary.append(
                {
                    "key_bits": bits,
                    "operation": operation.removesuffix("_ms"),
                    "mean_ms": statistics.mean(values),
                    "median_ms": statistics.median(values),
                    "stdev_ms": statistics.stdev(values) if len(values) > 1 else 0.0,
                }
            )
    return summary
