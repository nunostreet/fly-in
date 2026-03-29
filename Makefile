PYTHON ?= python3
MAP ?= maps/easy/01_linear_path.txt
LINT_TARGETS = main.py parser.py models routing simulation visualization
MYPY_TARGETS = main.py parser.py models/*.py routing/*.py simulation/*.py visualization/*.py

.PHONY: install run viz debug clean lint lint-strict

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) main.py $(MAP)

viz:
	$(PYTHON) main.py $(MAP) --run-viz

debug:
	$(PYTHON) -m pdb main.py $(MAP)

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -prune -exec rm -rf {} +
	find . -type d -name "htmlcov" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	find . -type f -name ".coverage.*" -delete

lint:
	flake8 $(LINT_TARGETS)
	mypy $(MYPY_TARGETS) --explicit-package-bases --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 $(LINT_TARGETS)
	mypy $(MYPY_TARGETS) --explicit-package-bases --strict
