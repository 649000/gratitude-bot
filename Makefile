ENV ?= dev

.PHONY: dev test lint format migrate check

dev:
	APP_ENV=$(ENV) uvicorn app.main:app --reload --port 8000

test:
	APP_ENV=test pytest -v --cov=app

lint:
	ruff check .

format:
	ruff format .

migrate:
	APP_ENV=$(ENV) alembic upgrade head

makemigrations:
	APP_ENV=$(ENV) alembic revision --autogenerate -m "$(message)"

seed:
	APP_ENV=$(ENV) uv run python scripts/seed.py

check: lint format --check test
