# Test material

## How to run

    python -m pytest                      # fast tests, no API calls, no cost
    $env:RUN_LLM_TESTS = "1"              # PowerShell: enable the live-model tests
    python -m pytest tests\test_llm_live.py
    Remove-Item Env:RUN_LLM_TESTS         # switch them off again

The older `tests/check_*.py` scripts are manual smoke checks (run with `python -m tests.<name>`).

## Test data

All data is synthetic: `samples/clear_notes.md`, `samples/example_pdf.md` (the assignment's own
fictional example), `samples/contradictory_notes.md`, `samples/empty_notes.md`,
`samples/wrong_type.docx`, `config/team.json` (fictional team with two people named Laura),
plus small inline notes and temporary files created inside the tests.

## Test cases and rationale

| # | Case | Expected behaviour | Why this test |
|---|------|--------------------|---------------|
| 1 | Clear notes (live) | Actions have owners and exact dates; nothing is invented | Baseline: the agent must not add noise to good input |
| 2 | Assignment example (live) | Test = proposed; "next month" needs clarification; data action has no owner; Laura not assigned; external access = open question | The assignment's own expected interpretation |
| 3 | Missing owners and deadlines | Guardrails clear ambiguous or unknown owners, flag vague dates, ask who owns an ownerless action | The core "never invent" rule, tested without the model |
| 4 | Contradictory notes (live) | Contradictions listed, items flagged, no side chosen | Explicit demo case in the assignment |
| 5 | File failures | Missing, empty, wrong-type, oversized and non-UTF-8 files give a clear message; the CLI exits with code 1 | Required technical-failure demonstration |
| 6 | Unknown person | Flagged, never silently trusted | Validator and guardrails agree |
| 7 | Human approval | Pending, rejected and skipped items are never written; end of input approves nothing | The main safety promise |
| 8 | Date validator | Only exact dates resolve; vague wording never does | Dates are the most error-prone part |
| 9 | Two Lauras | Notes say only "Laura" but the model writes "Laura Meyer": the owner is removed and the user is asked which Laura is meant. A full name that is really in the notes is still accepted | The assignment's central trap: the model must not silently pick one of two people with the same first name |

Deterministic parts (dates, people, guardrails, review, writer, files) are tested with ordinary
unit tests. Model output varies, so live tests check rules and structure, not exact wording.