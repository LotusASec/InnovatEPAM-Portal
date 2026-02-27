# Quickstart: InnovatEPAM Portal MVP

## Prerequisites

- Python 3.11+

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

## Test

```bash
pytest -q
```

## Coverage

```bash
pytest --cov=app --cov-report=term-missing
```

## Optional Mutation Testing

```bash
mutmut run
```

## Environment Variables

- JWT_SECRET: secret used to sign tokens
- JWT_ALGORITHM: HS256
- JWT_EXPIRES_MINUTES: 30
- DATABASE_URL: sqlite:///./app.db
- STORAGE_DIR: ./storage/attachments

