from __future__ import annotations

from fastapi import FastAPI


def create_app() -> FastAPI:
    application = FastAPI(
        title="Quorum Git Agent",
        version="0.1.0",
        description="Repository intelligence through REST and MCP.",
    )

    @application.get("/api/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "quorum-git-agent"}

    return application


app = create_app()

