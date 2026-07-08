from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

from app.analyzer import analyze_repository_bundle
from app.config import database_path, github_token
from app.database import Database
from app.demo_data import DEMO_BUNDLE
from app.github_client import GitHubClient

mcp = FastMCP("Quorum Git Agent", json_response=True)
database = Database(database_path())
database.initialize()
if database.count_analyses() == 0:
    database.save_analysis(analyze_repository_bundle(DEMO_BUNDLE))


@mcp.tool()
async def analyze_repository(repository: str) -> dict:
    """Analyze a public GitHub repository and persist its engineering health report."""
    bundle = await GitHubClient(github_token()).fetch_repository_bundle(repository)
    return database.save_analysis(analyze_repository_bundle(bundle))


@mcp.tool()
def list_recent_analyses(limit: int = 10) -> list[dict]:
    """List recently created repository health reports."""
    return database.list_analyses(limit=max(1, min(limit, 50)))


@mcp.tool()
def get_repository_brief(analysis_id: str) -> dict:
    """Return a stored repository analysis by its identifier."""
    analysis = database.get_analysis(analysis_id)
    return analysis or {"error": "Analysis not found", "analysis_id": analysis_id}


@mcp.tool()
def create_action_item(repository: str, title: str, priority: str = "medium") -> dict:
    """Save a follow-up engineering action in the local Quorum database."""
    allowed = {"low", "medium", "high", "critical"}
    normalized_priority = priority if priority in allowed else "medium"
    return database.save_action_item(repository, title, normalized_priority)


if __name__ == "__main__":
    mcp.run(transport=os.getenv("MCP_TRANSPORT", "stdio"))
