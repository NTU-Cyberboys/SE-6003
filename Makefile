.PHONY: test lint demo benchmark plots

PYTHON ?= python3

test:
	$(PYTHON) -m pytest

lint:
	ruff check src tests scripts

demo:
	$(PYTHON) scripts/run_demo.py

benchmark:
	$(PYTHON) scripts/run_benchmarks.py

plots:
	$(PYTHON) scripts/plot_benchmarks.py
