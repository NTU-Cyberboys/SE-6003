import pytest

from rsaoaep.benchmark import run_benchmarks, summarize


def test_benchmark_rejects_keys_too_small_for_sample():
    with pytest.raises(ValueError, match="fit a"):
        run_benchmarks([528])


def test_benchmark_summary_statistics():
    rows = [
        {"key_bits": 1024, "keygen_ms": "2", "encrypt_ms": "1", "decrypt_ms": "3"},
        {"key_bits": 1024, "keygen_ms": "4", "encrypt_ms": "3", "decrypt_ms": "5"},
    ]
    summary = summarize(rows)
    encryption = next(row for row in summary if row["operation"] == "encrypt")
    assert encryption["mean_ms"] == 2
    assert encryption["median_ms"] == 2
    assert encryption["stdev_ms"] > 0
