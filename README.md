# Design reflection

## What needed to be learned?
How to build an agent with PydanticAI: a typed output model, tools that the model calls, and retries. How the
Gemini API and its model names work. Above all, how to make a model's answer trustworthy by validating it,
rather than only asking it nicely in a prompt. I also learned to test code that depends on user input by
scripting the answers.

## What was the most difficult design decision?
How much to trust the model. I decided that the model proposes, code verifies and a human decides. This led to
smaller decisions: an owner who matches two people ("Laura") is cleared and a question is asked; an unknown
person is kept but flagged; a vague deadline is never converted into a date; and only approved actions are
saved, not every approved item.

## What assumptions were made?
The meeting date is known and passed in. The team list is complete (and fictional). Notes are plain English
text, one meeting per file. "Next month" can only become a date with a human's help. Approved decisions and
open questions are reviewed, but only actions are written to the output file.

## What is most likely to fail?
- The model treating the person who suggested something as the owner. A guardrail now removes an owner when the
  quote shows they only suggested or asked, but it is a word pattern, so unusual phrasing can slip through.
  Human review remains the safety net.
- The model putting text that is not a time into the deadline field. This happened once (it wrote "no owner was
  selected" as a deadline). I added a prompt rule, and the human review catches the rest.
- Model names being retired (I hit a 404) and an overloaded service (I hit repeated 503 errors). Both are handled,
  but they will happen again.
- Very long notes or subtle wording such as "we'll probably".

## How was behaviour verified?
- 61 automatic tests without the model: dates, people, guardrails (fed deliberately wrong "model output"),
  the review loop with scripted answers, saving, and file failures including the command-line exit code.
  Contradiction handling is also tested without the model, using a fake model answer.
- 3 live tests with the real model that check rules, not exact wording. They passed.
- Manual demonstrations with recorded terminal output (docs/DEMO.md): clear notes, the assignment's ambiguous example, contradictory notes,
  and several failures (missing, empty and wrong-type files, a wrong model name, a busy service).

## What should change before production?
Authentication and access control; a privacy review, because notes are sent to a cloud model; logging and an
audit trail of who approved what; a fallback model and monitoring of cost and rate limits; pinned dependency
versions; a larger evaluation set with real, anonymised notes; a proper interface instead of the terminal; and
output that connects to a task tool.

## When should a human be involved?
Always before anything is saved. Especially for ambiguous or unknown owners, vague deadlines and contradictions.
In the tool, items with open questions need an extra confirmation, end of input approves nothing, and typed
owners and dates are validated.

## Would a non-agent solution have been sufficient?
Partly. If notes followed a fixed template ("Action: X, Owner: Y, Due: Z"), a form or rule-based parser would be
cheaper, faster and fully deterministic. The model adds real value for free-form notes with hedging language
("should probably", "Laura suggested"). Even so, most of the safety here is ordinary code (validators, guardrails,
writer), and the agent is only one component. A simpler design could use the model only to classify statements,
and keep everything else rule-based.