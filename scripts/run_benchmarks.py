import argparse

from rsaoaep.benchmark import run_benchmarks


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark RSA-OAEP operations")
    parser.add_argument("--bits", nargs="+", type=int, default=[1024, 2048, 3072])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", default="data/benchmark_results.csv")
    args = parser.parse_args()
    rows = run_benchmarks(args.bits, args.repeats, args.output)
    print(f"Wrote {len(rows)} measurements to {args.output}")


if __name__ == "__main__":
    main()
