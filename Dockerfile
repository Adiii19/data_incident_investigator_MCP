FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./

COPY src ./src

RUN pip install uv

RUN uv sync --frozen

EXPOSE 8000

CMD ["uv","run","mcp","run","src/incident_investigator/server.py","--transport","streamable-http"]
