from datetime import UTC, datetime

from app.analyzer import analyze_repository_bundle, triage_issues
from app.demo_data import DEMO_BUNDLE

NOW = datetime(2026, 7, 8, tzinfo=UTC)


def test_analyzer_builds_repository_report() -> None:
    result = analyze_repository_bundle(DEMO_BUNDLE, now=NOW)

    assert result["repository"] == "northstar/atlas-api"
    assert result["score"] == 100
    assert result["metrics"]["ci_success_rate"] == 80.0
    assert result["metrics"]["language_mix"][0]["name"] == "Python"
    assert result["triaged_issues"][0]["number"] == 91


def test_issue_triage_prioritizes_security() -> None:
    issues = [
        {
            "number": 1,
            "title": "Security regression",
            "comments": 0,
            "created_at": "2026-07-07T00:00:00Z",
            "labels": [{"name": "security"}],
        },
        {
            "number": 2,
            "title": "Copy update",
            "comments": 0,
            "created_at": "2026-07-07T00:00:00Z",
            "labels": [],
        },
    ]

    result = triage_issues(issues, now=NOW)

    assert result[0]["number"] == 1
    assert result[0]["priority"] == "high"
