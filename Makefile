.PHONY: dev test lint format migrate check

dev:
	uvicorn app.main:app --reload --port 8000

test:
	pytest -v --cov=app

lint:
	ruff check .

format:
	ruff format .

migrate:
	alembic upgrade head

makemigrations:
	alembic revision --autogenerate -m "$(message)"

check: lint format --check test
