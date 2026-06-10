FROM ghcr.io/astral-sh/uv:python3.13-bookworm

ARG PORT=5000
ARG WORKERS=2

RUN apt update && apt install -y --no-install-recommends ffmpeg curl ca-certificates \
    && curl -fsSL https://deno.land/install.sh | DENO_INSTALL=/usr/local sh \
    && deno --version \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./uv.lock ./uv.lock
COPY ./pyproject.toml ./pyproject.toml

RUN uv sync

COPY . .

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT [ "make" ]

CMD [ "server" ]
