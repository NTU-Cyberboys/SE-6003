.PHONY: test lint demo benchmark plots

test:
	python -m pytest

lint:
	ruff check src tests scripts

demo:
	python scripts/run_demo.py

benchmark:
	python scripts/run_benchmarks.py

plots:
	python scripts/plot_benchmarks.py
