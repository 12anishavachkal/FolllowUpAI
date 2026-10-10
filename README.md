# FollowUpAI: Project Meeting Follow-up Agent (recruitment assignment)

A Python AI agent that turns messy meeting notes into a structured, reviewable follow-up package.
Nothing is saved until a human approves it.

This is my solution to the recruitment assignment "Project Meeting Follow-up Agent" (AI Agent, Assignment 1).

## 1. Problem definition

Meeting notes mix decisions, suggestions, tasks and open questions. A suggestion is easily mistaken for a
decision, owners and dates are often missing or vague ("next month"), and a language model may invent
missing details if the workflow is not designed carefully.

The agent reads fictional meeting notes and prepares a draft follow-up package:

- reads notes from a `.txt` or `.md` file
- classifies each statement as a confirmed decision, proposed decision, confirmed action, possible action,
  open question, risk, background or unclear
- attaches the exact supporting sentence from the notes to every item
- never invents owners, deadlines or project facts, and marks uncertain items with a clarification question
- produces a readable summary and structured JSON
- lets the user approve, reject, modify, complete or skip every item
- saves only approved actions to `output/approved_actions.json`

## 2. Solution and technology choices

| Choice | Why |
|---|---|
| Python 3.12 (developed on 3.12.5) | The assignment requires Python; 3.12 is the version I developed and tested on |
| PydanticAI | Typed structured output and simple tool registration; fits a small, verifiable design |
| Google Gemini (model set in `.env`) | Available with a free tier |
| Pydantic models | The output has a defined shape; owners and deadlines are optional so they are never forced |
| python-dotenv, PyYAML | Secrets in `.env`, settings in `config/settings.yaml`, rules in `config/system_prompt.md` |
| pytest | 62 fast tests without the model, plus 3 optional live tests |

Design principle: a small, well-tested solution. One agent, three agent tools (date, person, project-info search), three safety layers, two human approval points.
It is deliberately not a multi-agent system.
Only the deadline validator, the person validator and the project-info search are registered as agent tools. Reading the notes file and saving approved actions are plain Python on purpose, so the model can never read or write files by itself.

## 3. How it works

1. The note reader checks the file (exists, `.txt`/`.md`, size, UTF-8, not empty).
2. The agent (Gemini through PydanticAI) classifies the notes. It must call a date tool for every deadline
   and a person tool for every owner.
3. Guardrails re-check the answer in plain code: every item is reset to pending, quoted evidence must really
   appear in the notes, owners must pass the person validator, deadlines are re-validated.
4. The user reviews every item in the terminal (first human approval point).
5. A final "Save?" question is the second approval point. Only approved items of the saveable types are written.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the diagram and details.

## 4. Setup

Requirements: Python 3.12, Git, and a Gemini API key from Google AI Studio (aistudio.google.com).
Tested with Python 3.12.5.

Developed and tested with gemini-3.5-flash-lite

```
git clone https://github.com/12anishavachkal/FolllowUpAI.git
cd FolllowUpAI
python -m venv .venv
.venv\Scripts\Activate.ps1        # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
Copy-Item .env.example .env       # macOS/Linux: cp .env.example .env

```

Open `.env` and set your own values (never commit this file):

```
LLM_MODEL=<a Gemini model name available to you>
GEMINI_API_KEY=<your key>
```

Model names change over time. If you get a "model not found" error, check the current list at
ai.google.dev/gemini-api/docs/models and change `LLM_MODEL`.

## 5. Run

```
python -m src.main samples\example_pdf.md --date 2026-10-06
```

| Option | Meaning |
|---|---|
| `--date YYYY-MM-DD` | Meeting date, used to check deadlines (default: today) |
| `--no-review` | Print the draft only, nothing is reviewed or saved |
| `--json` | Also print the structured JSON |

Review keys: `a` approve, `r` reject, `m` modify, `c` complete owner or deadline, `s` skip, `q` finish.
Typed owners are checked against `config/team.json`. Typed deadlines must be exact dates (for example 2026-11-15).
Items that still have an open question need an extra confirmation and a typed reason to approve.

Sample notes are in `samples/`: `clear_notes.md`, `example_pdf.md` (the assignment's own example),
`contradictory_notes.md`, `risk_notes.md` (risks and concerns, see demo G), plus `empty_notes.md` and `wrong_type.docx` for failure cases.

## 6. Tests

```
python -m pytest                  # 62 tests, no API calls
$env:RUN_LLM_TESTS = "1"          # enable the 3 live-model tests (they call Gemini)
python -m pytest tests\test_llm_live.py
```

Details and the reasoning behind each test: [docs/TESTS.md](docs/TESTS.md).

## 7. Project structure

```
config/        settings.yaml, team.json (fictional team), project_info.json (fictional project facts), system_prompt.md
src/           main.py, analyze.py, agent.py, guardrails.py, review.py, models.py, llm.py, config.py
src/tools/     note_reader.py, date_validator.py, person_validator.py, project_search.py, action_writer.py, summary.py
samples/       synthetic meeting notes
tests/         test_*.py (pytest) and check_*.py (manual smoke scripts)
docs/          DEMO.md, TESTS.md
output/        approved_actions.json is created here (git-ignored)
```

## 8. Known limitations

- The model can still misread language. The guardrails flag a "confirmed" item whose quote sounds hedged
  ("probably", "could", "suggested") and remove an owner who only suggested or asked something. These are
  word-pattern checks, so they reduce but do not remove the risk of a wrong classification or owner. The human
  review is the final safeguard.
  - A reviewer can approve an item that still has an open question, but must type a reason. The reason is saved as
  `approval_note` and the record keeps `needs_clarification: true`.
- English text notes only, one file per run, JSON output only.
- The meeting date is not read from the notes. It comes from `--date` (default: today), so for an older meeting pass `--date`, otherwise relative wording such as "next month" is checked against the wrong date.
- The action writer skips records that were already saved (same source, type, title, owner, deadline and quote), so running the same notes twice does not create duplicates.
- Editing a deadline during review does not update a date mentioned in the description (owner edits do).
- The team list and the project-information file (`config/project_info.json`) are fictional and small.
- The review is a terminal interface.
- Model availability and load change: a model name can be retired and a busy service returns errors. Busy
  responses are retried automatically (4 attempts); a wrong model name fails immediately.
- Only approved actions are saved. Approved decisions and questions stay in the session and are not written.
- The live tests depend on the real model and check rules, not exact wording.

## 9. Security and privacy

- No credentials are in the repository. `.env` is git-ignored and `.env.example` holds placeholders only.
- Only fictional or synthetic data is used. Notes are sent to Google's Gemini API, so real confidential meeting
  notes must not be used. Free-tier inputs may be used by Google to improve its products (check the current terms).
- The notes are treated as data, not instructions, which reduces prompt-injection risk. Guardrails re-check the output.
- Nothing is saved without human approval. Saved output stays on the local machine.

## 10. Use of generative AI during development

- **Claude (Anthropic)** was used in a chat conversation to plan the project, design the architecture, write and
  debug the code, the tests and the documentation, and to walk through each setup step. I ran every command, checked
  the results myself and fixed problems that came up (for example a retired model name, an overloaded model service
  and empty files).
- Gemini is the model inside the product itself. It receives only synthetic notes.

## 11. Demonstration and further documents

- [docs/DEMO.md](docs/DEMO.md): successful, ambiguous and failure runs, decision flow, improvements
- [ARCHITECTURE.md](ARCHITECTURE.md): components, data flow and human approval points
- [REFLECTION.md](REFLECTION.md): design reflection