.PHONY: install-dev
install-dev:
	pip install -r ../test-requirements.txt
	pip install -r ../code-requirements.txt
	cd .. && pip install -r nucliadb_utils/requirements-sources.txt
	pip install -r requirements.txt
	pip install -r requirements-test.txt
	pip install -e .

.PHONY: format
format:
	isort --profile black .
	black --verbose .

.PHONY: lint
lint:
	flake8 nucliadb --config=setup.cfg
	isort -c --profile black .
	black --check --verbose .
	MYPYPATH=./mypy_stubs mypy --config-file=../mypy.ini .

.PHONY: test
test-ingest:
	pytest -s --tb=native -v nucliadb/ingest

.PHONY: test-cov
test-ingest-cov:
	pytest -rfE --cov=nucliadb.ingest --cov-config=../.coveragerc -s --tb=native -v --cov-report term-missing:skip-covered --cov-report xml nucliadb/ingest