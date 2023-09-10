test# AI Document Search Backend

## How to run

### Server

#### Without Docker

- `poetry run uvicorn ai_document_search_backend.application:app --reload`

#### With Docker

- `docker compose up`

### Unit tests

- `poetry run pytest`

### Lint autoformat

- `poetry run black --config black.py.toml .`

### Lint check

- `poetry run black --config black.py.toml . --check`
