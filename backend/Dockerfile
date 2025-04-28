FROM python:3.12-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update -y \
 && apt-get upgrade -y \
 && apt-get install -y \
    curl \
    ffmpeg \
    gcc \
    git \
    musl-dev \
    python3-dev \
 && apt-get clean

COPY pyproject.toml .
COPY poetry.lock .

RUN pip install --upgrade pip && \
    pip install poetry  && \
    poetry config virtualenvs.create false  && \
    poetry install --no-root --no-interaction --no-ansi

COPY . .

CMD ["poetry", "run", "python", "-m", "manage", "runserver"]
