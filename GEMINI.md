# Antigravity Project Instructions

## Permanent Project Rules
1. Implement one milestone at a time.
2. Preserve previously working functionality.
3. Prefer official Google ADK APIs.
4. Use type hints and Pydantic.
5. Use Python for deterministic calculations.
6. Keep components modular and testable.
7. Never hardcode credentials.
8. Run all quality checks after each milestone.
9. Update README when behavior changes.
10. Do not prematurely implement future milestones.
11. Every completed milestone document must contain: Objective and scope, Full Antigravity instructions, Files created or modified, Validation commands, Actual test results, Git commit hash, Git tag, and Known limitations.
12. Follow the Mandatory Step-by-Step Testing Policy on all milestones:
    - Test after every implementation step (run relevant unit tests immediately, fix broken code before continuing).
    - Test each agent independently (creation, imports, tools, structured outputs, offline fixtures, live Gemini request).
    - Test agent delegation (root_agent routing, ADK execution trace, tool execution, Pydantic validation).
    - Perform regression testing across all prior milestones (M1, M2, etc.).
    - Test failure scenarios (invalid input, unknown topics, missing data, tool errors, credential issues).
    - Pass all quality gates (`ruff check`, `ruff format --check`, `mypy`, `pytest -q`).
    - Verify live demos with real ADK Runner and ADK Web when API credentials are provided.
    - Document actual testing results with component, command, expected, actual, pass/fail, fixes, and limitations.
    - Enforce release gate: no commits, tags, or pushes until all verifications pass.
