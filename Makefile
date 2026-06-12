.PHONY: install test lint docker-build docker-run clean

install:
	pip install -r requirements.txt

test:
	pytest -v

lint:
	ruff check .
	black --check .

docker-build:
	docker build -t ids-project .

docker-run:
	docker-compose up

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov


