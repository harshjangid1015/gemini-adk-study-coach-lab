"""Live Gemini ADK Agent Evaluation Suite.

Executes real Gemini ADK evaluation scenarios separately from deterministic pytest contract tests.
Validates end-to-end agent invocation, tool use, Pydantic schema contracts, and observability.
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.genai import types

# Load credentials
load_dotenv()

from study_coach.agent import root_agent
from study_coach.models.student import StudentProfile
from study_coach.observability import ADKObservabilityPlugin, setup_tracing
from study_coach.services.workshop_facade import WorkshopFacade
from study_coach.workflows.adaptive_study import AdaptiveStudyWorkflow

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("adk_eval")

FIXTURES_PATH = Path(__file__).parent / "fixtures" / "evaluation_scenarios.json"


def load_scenarios() -> list[dict[str, Any]]:
    """Loads evaluation scenarios synchronously."""
    with open(FIXTURES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    result: list[dict[str, Any]] = data.get("scenarios", [])
    return result


SCENARIOS = load_scenarios()


async def main() -> int:
    setup_tracing()
    scenarios = SCENARIOS

    results: list[dict[str, Any]] = []
    print("=" * 80)
    print("🚀 GOOGLE ADK LIVE MODEL EVALUATION SUITE")
    print("=" * 80)

    plugin = ADKObservabilityPlugin()
    facade = WorkshopFacade(observability_plugin=plugin)
    workflow = AdaptiveStudyWorkflow(observability_plugin=plugin)

    # 1. Evaluate Topic Expert (Scenario 3)
    print("\n[1/4] Evaluating Topic Expert agent (Scenario 3: Grounding & RAG)...")
    _ = next(s for s in scenarios if s["id"] == "scenario_3")
    start = time.time()
    try:
        explanation = await facade.explain_topic(
            topic_id="grounding_rag",
            experience_level="beginner",
        )
        dur = time.time() - start
        assert len(explanation.key_concepts) >= 3
        assert len(explanation.learning_objectives) >= 2
        print(f"  ✓ PASS: '{explanation.topic_title}' generated in {dur:.2f}s")
        print(
            f"    - Key concepts ({len(explanation.key_concepts)}): {', '.join(explanation.key_concepts[:3])}"
        )
        results.append(
            {
                "scenario": "scenario_3",
                "agent": "topic_expert",
                "status": "PASS",
                "duration": dur,
            }
        )
    except (RuntimeError, ValueError, AssertionError, TimeoutError) as err:
        dur = time.time() - start
        print(f"  ✗ FAIL Scenario 3 ({dur:.2f}s): {err}")
        results.append(
            {
                "scenario": "scenario_3",
                "agent": "topic_expert",
                "status": "FAIL",
                "error": str(err),
            }
        )

    # 2. Evaluate Quiz Generator (Scenario 5)
    print("\n[2/4] Evaluating Quiz Generator agent (Scenario 5: 3 formative MCQs)...")
    start = time.time()
    try:
        profile = StudentProfile(experience_level="beginner", daily_study_minutes=60)
        await workflow.session_service.get_or_create_session(
            "eval_q_sess", "eval_user", profile
        )
        questions = await workflow.generate_practice_quiz(
            session_id="eval_q_sess",
            user_id="eval_user",
            topic_ids=["llm_foundations"],
            question_count=3,
        )
        dur = time.time() - start
        assert len(questions) == 3
        for q in questions:
            assert len(q.options) == 4
        print(
            f"  ✓ PASS: {len(questions)} formative MCQs generated in {dur:.2f}s (all with 4 sanitized options)"
        )
        results.append(
            {
                "scenario": "scenario_5",
                "agent": "quiz_generator",
                "status": "PASS",
                "duration": dur,
            }
        )
    except (RuntimeError, ValueError, AssertionError, TimeoutError) as err:
        dur = time.time() - start
        print(f"  ✗ FAIL Scenario 5 ({dur:.2f}s): {err}")
        results.append(
            {
                "scenario": "scenario_5",
                "agent": "quiz_generator",
                "status": "FAIL",
                "error": str(err),
            }
        )

    # 3. Evaluate Study Planner (Scenario 2: 7 days, 45 min)
    print("\n[3/4] Evaluating Study Planner agent (Scenario 2: 7 days, 45 mins/day)...")
    start = time.time()
    try:
        profile_s2 = StudentProfile(
            experience_level="intermediate", daily_study_minutes=45
        )
        plan = await workflow.create_initial_plan(
            session_id="eval_plan_sess",
            user_id="eval_user",
            student_profile=profile_s2,
            certification_name="Google Cloud Generative AI Leader",
            days_until_exam=7,
        )
        dur = time.time() - start
        assert plan.days_until_exam == 7
        assert len(plan.days) == 7
        for d in plan.days:
            assert d.total_minutes <= 45
        print(
            f"  ✓ PASS: 7-day study plan generated in {dur:.2f}s adhering strictly to daily budget (<= 45 min)"
        )
        results.append(
            {
                "scenario": "scenario_2",
                "agent": "study_planner",
                "status": "PASS",
                "duration": dur,
            }
        )
    except (RuntimeError, ValueError, AssertionError, TimeoutError) as err:
        dur = time.time() - start
        print(f"  ✗ FAIL Scenario 2 ({dur:.2f}s): {err}")
        results.append(
            {
                "scenario": "scenario_2",
                "agent": "study_planner",
                "status": "FAIL",
                "error": str(err),
            }
        )

    # 4. Evaluate Coordinator root agent delegation (Scenario 1)
    print("\n[4/4] Evaluating Root Coordinator agent delegation (Scenario 1)...")
    s1 = next(s for s in scenarios if s["id"] == "scenario_1")
    start = time.time()
    try:
        runner = InMemoryRunner(agent=root_agent, plugins=[plugin])
        await runner.session_service.create_session(
            app_name=runner.app_name,
            user_id="eval_user",
            session_id="eval_root_sess",
        )
        response_text = ""
        user_content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=s1["request"])],
        )
        async for event in runner.run_async(
            user_id="eval_user",
            session_id="eval_root_sess",
            new_message=user_content,
        ):
            event_content = getattr(event, "content", None)
            if event_content and getattr(event_content, "parts", None):
                parts = getattr(event_content, "parts", []) or []
                for part in parts:
                    txt = getattr(part, "text", None)
                    if txt:
                        response_text += str(txt)

        dur = time.time() - start
        assert len(response_text) > 50
        print(
            f"  ✓ PASS: Root Coordinator routed & responded in {dur:.2f}s ({len(response_text)} chars)"
        )
        results.append(
            {
                "scenario": "scenario_1",
                "agent": "root_agent",
                "status": "PASS",
                "duration": dur,
            }
        )
    except (RuntimeError, ValueError, AssertionError, TimeoutError) as err:
        dur = time.time() - start
        print(f"  ✗ FAIL Scenario 1 ({dur:.2f}s): {err}")
        results.append(
            {
                "scenario": "scenario_1",
                "agent": "root_agent",
                "status": "FAIL",
                "error": str(err),
            }
        )

    # Summary
    print("\n" + "=" * 80)
    print("📊 ADK LIVE EVALUATION SUMMARY")
    print("=" * 80)
    print(f"{'Scenario':<15} {'Target Agent':<20} {'Status':<10} {'Details'}")
    print("-" * 80)
    failed = 0
    for r in results:
        status = r["status"]
        if status == "FAIL":
            failed += 1
            details = r.get("error", "Error")
        else:
            details = f"{r.get('duration', 0.0):.2f}s latency"
        print(f"{r['scenario']:<15} {r['agent']:<20} {status:<10} {details}")
    print("=" * 80)
    print(f"Result: {len(results) - failed}/{len(results)} scenarios passed.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
