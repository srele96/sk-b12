# Match .python-version
FROM python:3.14-slim

# Store dependencies
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY . .

CMD ["/bin/bash"]
