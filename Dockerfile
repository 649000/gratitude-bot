FROM python:3.13-slim AS builder

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir .

COPY . .

FROM builder AS production

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
