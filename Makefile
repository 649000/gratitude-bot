ENV ?= dev

.PHONY: dev test lint format format-check migrate seed check lock

dev:
	APP_ENV=$(ENV) uvicorn app.main:app --reload --port 8000

test:
	APP_ENV=test pytest -v --cov=app --cov=scheduler --cov=shared

lint:
	ruff check .

format:
	ruff format .

format-check:
	ruff format --check .

migrate:
	APP_ENV=$(ENV) alembic upgrade head

makemigrations:
	APP_ENV=$(ENV) alembic revision --autogenerate -m "$(message)"

seed:
	APP_ENV=$(ENV) uv run python src/app/seed.py

lock:
	uv pip compile pyproject.toml -o requirements.txt

check: lint format-check test
