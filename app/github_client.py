from __future__ import annotations

import re
from typing import Any

import httpx

REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


class GitHubClientError(RuntimeError):
    pass


class GitHubClient:
    def __init__(self, token: str | None = None) -> None:
        self.token = token

    async def fetch_repository_bundle(self, repository: str) -> dict[str, Any]:
        repository = repository.strip()
        if not REPOSITORY_PATTERN.fullmatch(repository):
            raise GitHubClientError("Repository must use the owner/name format.")

        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "quorum-git-agent",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        async with httpx.AsyncClient(
            base_url="https://api.github.com",
            headers=headers,
            timeout=15,
        ) as client:
            repo = await self._required_get(client, f"/repos/{repository}")
            languages = await self._optional_get(client, f"/repos/{repository}/languages", {})
            issues_payload = await self._optional_get(
                client,
                f"/repos/{repository}/issues",
                [],
                params={"state": "open", "per_page": 50, "sort": "updated"},
            )
            pulls = await self._optional_get(
                client,
                f"/repos/{repository}/pulls",
                [],
                params={"state": "open", "per_page": 30},
            )
            workflow_payload = await self._optional_get(
                client,
                f"/repos/{repository}/actions/runs",
                {"workflow_runs": []},
                params={"per_page": 20},
            )

        issues = [item for item in issues_payload if "pull_request" not in item]
        return {
            "repository": repo,
            "languages": languages,
            "issues": issues,
            "pulls": pulls,
            "workflow_runs": workflow_payload.get("workflow_runs", []),
        }

    @staticmethod
    async def _required_get(
        client: httpx.AsyncClient,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        try:
            response = await client.get(path, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            if error.response.status_code == 404:
                raise GitHubClientError("Repository was not found or is private.") from error
            if error.response.status_code == 403:
                raise GitHubClientError(
                    "GitHub API rate limit reached. Add GITHUB_TOKEN and retry."
                ) from error
            raise GitHubClientError(f"GitHub API returned {error.response.status_code}.") from error
        except httpx.HTTPError as error:
            raise GitHubClientError("Could not connect to the GitHub API.") from error
        return response.json()

    @staticmethod
    async def _optional_get(
        client: httpx.AsyncClient,
        path: str,
        fallback: Any,
        params: dict[str, Any] | None = None,
    ) -> Any:
        try:
            response = await client.get(path, params=params)
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError):
            return fallback
