"""Unit tests for EvaluationRunner and Agent Ops components."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from study_coach.evaluation import (
    EvaluationRunner,
    load_evaluation_report,
    save_evaluation_report,
)
from study_coach.models.evaluation import (
    EvaluationScenarioResult,
    EvaluationSummaryReport,
)
from ui.components.agent_ops import check_prometheus_health


def test_evaluation_summary_report_serialization(tmp_path: Path) -> None:
    """Verifies that EvaluationSummaryReport serializes cleanly to JSON without secrets."""
    scenario = EvaluationScenarioResult(
        scenario_id="scenario_3",
        scenario_description="Explain concepts",
        target_agent="topic_expert",
        status="PASS",
        duration_seconds=2.45,
        details="Generated 3 key concepts successfully.",
        metadata={"concept_count": 3},
    )
    report = EvaluationSummaryReport(
        run_id="eval_test_123",
        model="gemini-3.8-flash",
        total_scenarios=1,
        passed_scenarios=1,
        failed_scenarios=0,
        total_duration_seconds=2.45,
        scenarios=[scenario],
    )

    report_file = tmp_path / "test_report.json"
    save_evaluation_report(report, path=report_file)

    assert report_file.exists()
    loaded = load_evaluation_report(path=report_file)
    assert loaded is not None
    assert loaded.run_id == "eval_test_123"
    assert loaded.total_scenarios == 1
    assert loaded.scenarios[0].scenario_id == "scenario_3"
    assert loaded.scenarios[0].status == "PASS"

    # Verify no credentials or private answer keys
    raw_text = report_file.read_text(encoding="utf-8")
    assert "AIza" not in raw_text
    assert "API_KEY" not in raw_text
    assert "correct_answer" not in raw_text


def test_load_evaluation_report_nonexistent(tmp_path: Path) -> None:
    """Verifies that load_evaluation_report returns None when file does not exist."""
    missing = tmp_path / "does_not_exist.json"
    assert load_evaluation_report(path=missing) is None


def test_load_evaluation_report_corrupted(tmp_path: Path) -> None:
    """Verifies that corrupted JSON is handled safely without raising."""
    corrupted = tmp_path / "corrupted.json"
    corrupted.write_text("{bad json: 123", encoding="utf-8")
    assert load_evaluation_report(path=corrupted) is None


@pytest.mark.anyio
async def test_evaluation_runner_prevents_concurrent_runs() -> None:
    """Verifies that run_all prevents concurrent execution when lock is held."""
    runner = EvaluationRunner()
    # Acquire lock artificially
    async with runner._lock:
        _report, already_running = await runner.run_all(persist=False)
        assert already_running is True


@pytest.mark.anyio
async def test_evaluation_runner_missing_credentials(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Verifies that missing credentials gracefully produce failed scenarios with clear error."""
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    report_path = tmp_path / "no_creds_report.json"
    runner = EvaluationRunner()
    with patch("study_coach.evaluation.runner.EVALUATION_REPORT_PATH", report_path):
        report, already_running = await runner.run_all(persist=False)
        assert already_running is False
        assert report.failed_scenarios == 4
        assert report.passed_scenarios == 0
        for s in report.scenarios:
            assert s.status == "FAIL"
            assert "Missing Gemini credentials" in (s.error or "")


def test_check_prometheus_health_online() -> None:
    """Verifies that check_prometheus_health returns True when HTTP 200 response is received."""
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        assert check_prometheus_health() is True


def test_check_prometheus_health_offline() -> None:
    """Verifies that check_prometheus_health returns False when connection fails."""
    with patch("urllib.request.urlopen", side_effect=OSError("Connection refused")):
        assert check_prometheus_health() is False
