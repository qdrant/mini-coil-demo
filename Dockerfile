FROM node:current as builder

COPY frontend /frontend
WORKDIR /frontend

RUN npm install; npm run build

FROM python:3.11-slim

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.8.5

RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

# Install pre-trained models here
# Example:
RUN python -c 'from fastembed.late_interaction.token_embeddings import TokenEmbeddingsModel; TokenEmbeddingsModel(model_name="jinaai/jina-embeddings-v2-small-en-tokens")'

# Creating folders, and files for a project:
COPY . /code

COPY data/minicoil.model.npy /code/data/minicoil.model.npy
COPY data/minicoil.model.vocab /code/data/minicoil.model.vocab

COPY --from=builder /frontend/dist /code/frontend/dist

CMD uvicorn minicoil_demo.service:app --host 0.0.0.0 --port 8000 --workers ${WORKERS:-1}
