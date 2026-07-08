# Quorum Git Agent

Quorum is a Python service for repository intelligence. It combines a FastAPI
application, SQLite persistence and an MCP server so the same GitHub analysis
can be used from a dashboard, REST clients or an AI host.

The project is being built in visible, reviewable stages. The first version
contains the service skeleton and health endpoint.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
.\start.ps1
```

Open `http://127.0.0.1:8010/docs`.

