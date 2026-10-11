"""Live Gemini ADK Agent Evaluation Suite.

Executes real Gemini ADK evaluation scenarios separately from deterministic pytest contract tests.
Validates end-to-end agent invocation, tool use, Pydantic schema contracts, and observability.
Preserves the standard CLI entrypoint while delegating to the reusable EvaluationRunner.
"""

import asyncio
import logging
import sys

from dotenv import load_dotenv

# Load credentials
load_dotenv()

from study_coach.evaluation.runner import EvaluationRunner

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("adk_eval")


async def main() -> int:
    """CLI entrypoint for running evaluation scenarios."""
    print("=" * 80)
    print("🚀 GOOGLE ADK LIVE MODEL EVALUATION SUITE")
    print("=" * 80)

    runner = EvaluationRunner()
    report, already_running = await runner.run_all(persist=True)

    if already_running:
        print("⚠️ An evaluation run is already currently in progress.")
        return 1

    for res in report.scenarios:
        if res.status == "PASS":
            print(
                f"\n  ✓ PASS [{res.scenario_id}] {res.target_agent} ({res.duration_seconds:.2f}s): {res.details}"
            )
        else:
            print(
                f"\n  ✗ FAIL [{res.scenario_id}] {res.target_agent} ({res.duration_seconds:.2f}s): {res.error}"
            )

    print("\n" + "=" * 80)
    print("📊 ADK LIVE EVALUATION SUMMARY")
    print("=" * 80)
    print(f"{'Scenario':<15} {'Target Agent':<20} {'Status':<10} {'Details'}")
    print("-" * 80)
    for res in report.scenarios:
        detail = (
            f"{res.duration_seconds:.2f}s latency"
            if res.status == "PASS"
            else (res.error or "Error")
        )
        print(f"{res.scenario_id:<15} {res.target_agent:<20} {res.status:<10} {detail}")
    print("=" * 80)
    print(
        f"Result: {report.passed_scenarios}/{report.total_scenarios} scenarios passed ({report.total_duration_seconds:.2f}s total)."
    )
    return 0 if report.failed_scenarios == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
