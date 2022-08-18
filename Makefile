install:
	poetry install

test: install
	poetry run pytest -v -s tests
