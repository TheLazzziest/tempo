FROM python:3.13-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONPATH="/code/broker:"

# Allows docker to cache installed dependencies between builds
RUN apt-get update && \
    apt-get -y --no-install-recommends install libpq-dev=15.13-0+deb12u1 gcc=4:12.2.0-3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Security Context
RUN useradd -m nonroot
USER nonroot

# Setup a workdir
WORKDIR /code

COPY uv.lock pyproject.toml ./

RUN uv sync --locked

COPY . ./

RUN rm uv.lock pyproject.toml

EXPOSE 8000
# Run the production server
ENTRYPOINT [ "/code/entrypoint.sh" ]
