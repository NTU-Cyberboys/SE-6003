import argparse
import csv
from pathlib import Path

from rsaoaep.benchmark import summarize


def main() -> None:
    parser = argparse.ArgumentParser(description="Create report-ready benchmark outputs")
    parser.add_argument("--input", default="data/benchmark_results.csv")
    parser.add_argument("--output-dir", default="output/charts")
    parser.add_argument("--summary", default="report/tables/benchmark_summary.csv")
    args = parser.parse_args()

    import matplotlib.pyplot as plt

    with Path(args.input).open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise SystemExit("benchmark CSV has no measurements")
    summary = summarize(rows)
    summary_path = Path(args.summary)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with summary_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    operations = ("keygen", "encrypt", "decrypt")
    fig, axis = plt.subplots(figsize=(8, 5))
    for operation in operations:
        values = [row for row in summary if row["operation"] == operation]
        axis.plot(
            [int(row["key_bits"]) for row in values],
            [float(row["median_ms"]) for row in values],
            marker="o",
            label=operation.capitalize(),
        )
    axis.set_xlabel("RSA modulus size (bits)")
    axis.set_ylabel("Median time (ms)")
    axis.set_title("RSA-OAEP operation timings")
    axis.set_yscale("log")
    axis.grid(True, which="both", linestyle=":", alpha=0.5)
    axis.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "operation_timings.png", dpi=180)
    plt.close(fig)
    print(f"Wrote chart to {output_dir / 'operation_timings.png'} and summary to {summary_path}")


if __name__ == "__main__":
    main()
