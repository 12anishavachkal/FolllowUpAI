# Demonstration

Agent: Project Meeting Follow-up Agent (PydanticAI + Gemini)
Model used: `gemini-3.5-flash-lite` (pydantic-ai 2.54.0, Python 3.12.5)
Meeting date used for all runs: `2026-10-06` (passed with `--date`)
Recorded: 2026-10-08 and 2026-10-09
Setup: see the README. All meeting notes are synthetic and live in `samples/`.
Paths in the recordings are shortened to `<project>\`.

| # | Case | Notes file | Assignment requirement it covers |
| --- | --- | --- | --- |
| A | Clear notes, full approval and save | `clear_notes.md` | One successful interaction |
| B | Ambiguous notes, human completes an item | `example_pdf.md` | One ambiguous or incomplete interaction |
| C | Contradictory notes | `contradictory_notes.md` | Contradictory information |
| D | Missing, empty and wrong-type file, bad model name | several | One failure scenario |
| E | Busy service (simulated with tests) | `tests\test_retry.py` | Technical failure with automatic retry |
| F | Approving over an open question | `example_pdf.md` | Human approval with a recorded reason |

---

## A. Successful interaction (clear notes)

Command: `python -m src.main samples\clear_notes.md --date 2026-10-06`

What happened: All 5 reviewable items were approved. The 3 confirmed actions were saved with owners and exact dates. The 2 approved decisions were not saved, because only actions are saved. A mistyped (empty) key at item 3 was rejected with a prompt and the item was shown again.

```
PS> python -m src.main samples\clear_notes.md --date 2026-10-06
MEETING FOLLOW-UP (DRAFT - nothing has been saved)
============================================================
Meeting: Weekly Project Sync - Reporting Module

SUMMARY
The team held a weekly project sync for the reporting module on October 6, 2026, confirming plans to launch the reporting view to internal users on November 2, 2026, while excluding external users in this release. Tasks were assigned to Tom Becker, Priya Nair, and Arjun Rao with specific deadlines.
Topics: Reporting Module; Launch Planning; Bug Fixing; Project Data; Testing Invitations

CONFIRMED DECISIONS (2)
  [item-1] Launch reporting view to internal users
      The reporting view will be launched to internal users on November 2, 2026.
      Owner: NOT ASSIGNED
      Deadline: 2026-11-02 (notes say '2026-11-02')
      Source: "We decided to launch the reporting view to internal users on 2026-11-02."
  [item-2] Exclude external users from initial release
      External users will not receive access to the reporting view in this release.
      Source: "The team agreed that external users will not get access in this release."

CONFIRMED ACTIONS (3)
  [item-3] Fix the export bug
      Tom Becker is responsible for fixing the export bug by October 16, 2026.
      Owner: Tom Becker
      Deadline: 2026-10-16 (notes say '2026-10-16')
      Source: "Tom Becker will fix the export bug by 2026-10-16."
  [item-4] Prepare example project data
      Priya Nair will prepare the example project data by October 13, 2026.
      Owner: Priya Nair
      Deadline: 2026-10-13 (notes say '2026-10-13')
      Source: "Priya Nair will prepare the example project data by 2026-10-13."
  [item-5] Send test invitation to project managers
      Arjun Rao will send the test invitation to project managers by October 20, 2026.
      Owner: Arjun Rao
      Deadline: 2026-10-20 (notes say '2026-10-20')
      Source: "Arjun Rao will send the test invitation to the project managers by 2026-10-20."

BACKGROUND (1)
  [item-6] Reporting view context
      The new reporting view replaces the older spreadsheet reports.
      Source: "The reporting view replaces the old spreadsheet reports."

0 of 6 items need clarification.

REVIEW: 5 items to review (1 background item(s) not reviewed).
Nothing is saved until you confirm at the end.

--- Item 1 of 5 (confirmed_decision) ---
  [item-1] Launch reporting view to internal users
      The reporting view will be launched to internal users on November 2, 2026.
      Owner: NOT ASSIGNED
      Deadline: 2026-11-02 (notes say '2026-11-02')
      Source: "We decided to launch the reporting view to internal users on 2026-11-02."
[a] approve  [r] reject  [m] modify  [c] complete owner/deadline  [s] skip  [q] finish review
> a
  -> approved

--- Item 2 of 5 (confirmed_decision) ---
  [item-2] Exclude external users from initial release
      External users will not receive access to the reporting view in this release.
      Source: "The team agreed that external users will not get access in this release."
[a] approve  [r] reject  [m] modify  [c] complete owner/deadline  [s] skip  [q] finish review
> a
  -> approved

--- Item 3 of 5 (confirmed_action) ---
  [item-3] Fix the export bug
      Tom Becker is responsible for fixing the export bug by October 16, 2026.
      Owner: Tom Becker
      Deadline: 2026-10-16 (notes say '2026-10-16')
      Source: "Tom Becker will fix the export bug by 2026-10-16."
[a] approve  [r] reject  [m] modify  [c] complete owner/deadline  [s] skip  [q] finish review
> 
  Please type a, r, m, c, s or q.

--- Item 3 of 5 (confirmed_action) ---
  [item-3] Fix the export bug
      Tom Becker is responsible for fixing the export bug by October 16, 2026.
      Owner: Tom Becker
      Deadline: 2026-10-16 (notes say '2026-10-16')
      Source: "Tom Becker will fix the export bug by 2026-10-16."
[a] approve  [r] reject  [m] modify  [c] complete owner/deadline  [s] skip  [q] finish review
> a
  -> approved

--- Item 4 of 5 (confirmed_action) ---
  [item-4] Prepare example project data
      Priya Nair will prepare the example project data by October 13, 2026.
      Owner: Priya Nair
      Deadline: 2026-10-13 (notes say '2026-10-13')
      Source: "Priya Nair will prepare the example project data by 2026-10-13."
[a] approve  [r] reject  [m] modify  [c] complete owner/deadline  [s] skip  [q] finish review
> a
  -> approved

--- Item 5 of 5 (confirmed_action) ---
  [item-5] Send test invitation to project managers
      Arjun Rao will send the test invitation to project managers by October 20, 2026.
      Owner: Arjun Rao
      Deadline: 2026-10-20 (notes say '2026-10-20')
      Source: "Arjun Rao will send the test invitation to the project managers by 2026-10-20."
[a] approve  [r] reject  [m] modify  [c] complete owner/deadline  [s] skip  [q] finish review
> a
  -> approved

Review finished: 5 approved, 0 rejected, 0 left pending.
2 approved item(s) are not actions and will not be saved (saved types: confirmed_action, possible_action).
Save 3 approved item(s) to <project>\output\approved_actions.json? [Y/n]: 
Saved 3 approved item(s) to <project>\output\approved_actions.json.
PS> Get-Content output\approved_actions.json
[
  {
    "id": "item-3",
    "type": "confirmed_action",
    "title": "Fix the export bug",
    "description": "Tom Becker is responsible for fixing the export bug by October 16, 2026.",
    "owner": "Tom Becker",
    "deadline_raw": "2026-10-16",
    "deadline_date": "2026-10-16",
    "deadline_status": "resolved",
    "supporting_text": "Tom Becker will fix the export bug by 2026-10-16.",
    "needs_clarification": false,
    "clarification_question": null,
    "status": "approved",
    "was_modified": false,
    "source_file": "clear_notes.md",
    "saved_at": "2026-10-08T05:35:58.027403+00:00"
  },
  {
    "id": "item-4",
    "type": "confirmed_action",
    "title": "Prepare example project data",
    "description": "Priya Nair will prepare the example project data by October 13, 2026.",
    "owner": "Priya Nair",
    "deadline_raw": "2026-10-13",
    "deadline_date": "2026-10-13",
    "deadline_status": "resolved",
    "supporting_text": "Priya Nair will prepare the example project data by 2026-10-13.",
    "needs_clarification": false,
    "clarification_question": null,
    "status": "approved",
    "was_modified": false,
    "source_file": "clear_notes.md",
    "saved_at": "2026-10-08T05:35:58.027403+00:00"
  },
  {
    "id": "item-5",
    "type": "confirmed_action",
    "title": "Send test invitation to project managers",
    "description": "Arjun Rao will send the test invitation to project managers by October 20, 2026.",
    "owner": "Arjun Rao",
    "deadline_raw": "2026-10-20",
    "deadline_date": "2026-10-20",
    "deadline_status": "resolved",
    "supporting_text": "Arjun Rao will send the test invitation to the project managers by 2026-10-20.",
    "needs_clarification": false,
    "clarification_question": null,
    "status": "approved",
    "was_modified": false,
    "source_file": "clear_notes.md",
    "saved_at": "2026-10-08T05:35:58.027403+00:00"
  }
]
```

---

## B. Ambiguous or incomplete interaction

Command: `python -m src.main samples\example_pdf.md --date 2026-10-06 --json`

What happened: The agent did not guess any owner and did not convert "next month" into a date. It flagged "Laura" as unclear and only offered the possible window 2026-11-01 to 2026-11-30, and 3 of the 4 items were marked as needing clarification. Approving the timing item (item 2) while its question was open needed an extra confirmation ("Approve anyway?"), which the reviewer declined, then skipped the item. For the confirmed action "Prepare example project data" (no owner in the notes), the reviewer edited the item and typed "Laura" as the owner. The tool refused and listed both people (Laura Meyer, Laura Schmidt), so the reviewer entered the full name "Priya Nair" and the exact date 2026-10-20, marked the open question resolved, and approved the item. 1 action was saved. The other 3 items stayed pending and were not saved.

How this recording was made: the review answers were piped into the program from a list, so the run is repeatable. Because of this, the answers are not echoed on screen, and each prompt is followed directly by its result. The answers, in order, were:

| Item | Answers |
| --- | --- |
| 1. Test with project managers | `s` (skip) |
| 2. Timing of the first test | `a` (approve), `n` (decline "Approve anyway?"), `s` (skip) |
| 3. Prepare example project data | `m` (modify), Enter (keep title), new description, `Laura` (refused), `Priya Nair`, `2026-10-20`, `y` (question resolved), `a` (approve) |
| 4. External user access | `s` (skip) |
| Save prompt | Enter (yes) |

The saved record at the end comes from an identical repeat of the same scripted review. Only its `saved_at` timestamp differs.

```
PS> "s","a","n","s","m","","Prepare the example project data.","Laura","Priya Nair","2026-10-20","y","a","s","" | python -m src.main samples\example_pdf.md --date 2026-10-06 --json
MEETING FOLLOW-UP (DRAFT - nothing has been saved)
============================================================
Meeting: Reporting View Meeting

SUMMARY
The team discussed testing the new reporting view with project managers and agreed to prepare example project data without assigning an owner. A suggestion was made to test next month, and a decision on external user access remains open.
Topics: Reporting view; Testing; Project data; External access

PROPOSED DECISIONS (not yet agreed) (2)
  [item-1] Test new reporting view with project managers
      The new reporting view should probably be tested with the project managers.
      Source: "The new reporting view should probably be tested with the project managers."
  [item-2] Timing of the first test
      Laura suggested that the first test could happen next month.
      Owner: NOT ASSIGNED
      Deadline: UNCLEAR (notes say 'next month')
      Source: "Laura suggested that the first test could happen next month."
      [!] Clarify: Which Laura should be associated with this suggestion? What is the exact deadline for 'next month'? It could fall between 2026-11-01 and 2026-11-30.

CONFIRMED ACTIONS (1)
  [item-3] Prepare example project data
      The team agreed to prepare example project data, but no owner was selected.
      Owner: NOT ASSIGNED
      Deadline: none mentioned
      Source: "The team agreed to prepare example project data, but no owner was selected."
      [!] Clarify: Who is responsible for preparing the example project data? Who should own this action?

OPEN QUESTIONS (1)
  [item-4] External user access decision
      The team must still decide whether external users should have access.
      Source: "We must still decide whether external users should have access."
      [!] Clarify: Should external users have access to the reporting view?

3 of 4 items need clarification.

STRUCTURED JSON
{
  "meeting_title": "Reporting View Meeting",
  "topics": [
    "Reporting view",
    "Testing",
    "Project data",
    "External access"
  ],
  "summary": "The team discussed testing the new reporting view with project managers and agreed to prepare example project data without assigning an owner. A suggestion was made to test next month, and a decision on external user access remains open.",
  "items": [
    {
      "id": "item-1",
      "type": "proposed_decision",
      "title": "Test new reporting view with project managers",
      "description": "The new reporting view should probably be tested with the project managers.",
      "owner": null,
      "deadline_raw": null,
      "deadline_date": null,
      "deadline_status": "none",
      "supporting_text": "The new reporting view should probably be tested with the project managers.",
      "needs_clarification": false,
      "clarification_question": null,
      "status": "pending",
      "was_modified": false
    },
    {
      "id": "item-2",
      "type": "proposed_decision",
      "title": "Timing of the first test",
      "description": "Laura suggested that the first test could happen next month.",
      "owner": null,
      "deadline_raw": "next month",
      "deadline_date": null,
      "deadline_status": "needs_clarification",
      "supporting_text": "Laura suggested that the first test could happen next month.",
      "needs_clarification": true,
      "clarification_question": "Which Laura should be associated with this suggestion? What is the exact deadline for 'next month'? It could fall between 2026-11-01 and 2026-11-30.",
      "status": "pending",
      "was_modified": false
    },
    {
      "id": "item-3",
      "type": "confirmed_action",
      "title": "Prepare example project data",
      "description": "The team agreed to prepare example project data, but no owner was selected.",
      "owner": null,
      "deadline_raw": null,
      "deadline_date": null,
      "deadline_status": "none",
      "supporting_text": "The team agreed to prepare example project data, but no owner was selected.",
      "needs_clarification": true,
      "clarification_question": "Who is responsible for preparing the example project data? Who should own this action?",
      "status": "pending",
      "was_modified": false
    },
    {
      "id": "item-4",
      "type": "open_question",
      "title": "External user access decision",
      "description": "The team must still decide whether external users should have access.",
      "owner": null,
      "deadline_raw": null,
      "deadline_date": null,
      "deadline_status": "none",
      "supporting_text": "We must still decide whether external users should have access.",
      "needs_clarification": true,
      "clarification_question": "Should external users have access to the reporting view?",
      "status": "pending",
      "was_modified": false
    }
  ],
  "contradictions": []
}

REVIEW: 4 items to review.
Nothing is saved until you confirm at the end.

--- Item 1 of 4 (proposed_decision) ---
  [item-1] Test new reporting view with project managers
      The new reporting view should probably be tested with the project managers.
      Source: "The new reporting view should probably be tested with the project managers."
[a] approve  [r] reject  [m] modify  [c] complete owner/deadline  [s] skip  [q] finish review
>   -> skipped (stays pending and will not be saved)

--- Item 2 of 4 (proposed_decision) ---
  [item-2] Timing of the first test
      Laura suggested that the first test could happen next month.
      Owner: NOT ASSIGNED
      Deadline: UNCLEAR (notes say 'next month')
      Source: "Laura suggested that the first test could happen next month."
      [!] Clarify: Which Laura should be associated with this suggestion? What is the exact deadline for 'next month'? It could fall between 2026-11-01 and 2026-11-30.
[a] approve  [r] reject  [m] modify  [c] complete owner/deadline  [s] skip  [q] finish review
>   This item still has an open question. Approve anyway? [y/N]: 
--- Item 2 of 4 (proposed_decision) ---
  [item-2] Timing of the first test
      Laura suggested that the first test could happen next month.
      Owner: NOT ASSIGNED
      Deadline: UNCLEAR (notes say 'next month')
      Source: "Laura suggested that the first test could happen next month."
      [!] Clarify: Which Laura should be associated with this suggestion? What is the exact deadline for 'next month'? It could fall between 2026-11-01 and 2026-11-30.
[a] approve  [r] reject  [m] modify  [c] complete owner/deadline  [s] skip  [q] finish review
>   -> skipped (stays pending and will not be saved)

--- Item 3 of 4 (confirmed_action) ---
  [item-3] Prepare example project data
      The team agreed to prepare example project data, but no owner was selected.
      Owner: NOT ASSIGNED
      Deadline: none mentioned
      Source: "The team agreed to prepare example project data, but no owner was selected."
      [!] Clarify: Who is responsible for preparing the example project data? Who should own this action?
[a] approve  [r] reject  [m] modify  [c] complete owner/deadline  [s] skip  [q] finish review
>   Title [Prepare example project data] (Enter = keep):   Description [The team agreed to prepare example project data, but no owner was selected.] (Enter = keep):   Owner [none] (Enter = keep, - = clear):   Several people match: Laura Meyer, Laura Schmidt. Please type the full name.
  Owner [none] (Enter = keep, - = clear):   Owner set to Priya Nair.
  Deadline [none] (Enter = keep, - = clear, or an exact date such as 2026-11-15):   Deadline set to 2026-10-20.
  Mark the open question as resolved? [y/N]: 
--- Item 3 of 4 (confirmed_action) ---
  [item-3] Prepare example project data
      Prepare the example project data.
      Owner: Priya Nair
      Deadline: 2026-10-20 (notes say '2026-10-20')
      Source: "The team agreed to prepare example project data, but no owner was selected."
[a] approve  [r] reject  [m] modify  [c] complete owner/deadline  [s] skip  [q] finish review
>   -> approved

--- Item 4 of 4 (open_question) ---
  [item-4] External user access decision
      The team must still decide whether external users should have access.
      Source: "We must still decide whether external users should have access."
      [!] Clarify: Should external users have access to the reporting view?
[a] approve  [r] reject  [m] modify  [c] complete owner/deadline  [s] skip  [q] finish review
>   -> skipped (stays pending and will not be saved)

Review finished: 1 approved, 0 rejected, 3 left pending.
Save 1 approved item(s) to <project>\output\approved_actions.json? [Y/n]: Saved 1 approved item(s) to <project>\output\approved_actions.json.
PS> Get-Content output\approved_actions.json
[
  {
    "id": "item-3",
    "type": "confirmed_action",
    "title": "Prepare example project data",
    "description": "Prepare the example project data.",
    "owner": "Priya Nair",
    "deadline_raw": "2026-10-20",
    "deadline_date": "2026-10-20",
    "deadline_status": "resolved",
    "supporting_text": "The team agreed to prepare example project data, but no owner was selected.",
    "needs_clarification": false,
    "clarification_question": null,
    "status": "approved",
    "was_modified": true,
    "source_file": "example_pdf.md",
    "saved_at": "2026-10-08T15:22:06.370542+00:00"
  }
]
```

---

## C. Contradictory information

Command: `python -m src.main samples\contradictory_notes.md --date 2026-10-06 --no-review`

What happened: Three contradictions (launch date, example-data deadline, external access) were listed. No side was chosen, and all 6 items were flagged for clarification. Nothing was saved, because review was skipped.

```
PS> python -m src.main samples\contradictory_notes.md --date 2026-10-06 --no-review
MEETING FOLLOW-UP (DRAFT - nothing has been saved)
============================================================
Meeting: Planning Meeting - Reporting View Launch

SUMMARY
During the planning meeting for the reporting view launch, multiple contradictory statements were made regarding the launch date, the example project data deadline, and external user access. A launch date of 2026-11-02 was initially agreed upon, but a postponement to 2026-11-16 was proposed. Priya Nair was assigned to prepare example project data by 2026-10-13, with a suggestion to move it to 2026-10-20. Finally, a decision on external user access from day one conflicted with a later statement that they would not get access.
Topics: Launch Date; Project Data Preparation; External User Access; Testing Status

CONFIRMED DECISIONS (2)
  [item-1] Launch date agreed for 2026-11-02
      The team initially agreed that the launch will be on 2026-11-02.
      Owner: NOT ASSIGNED
      Deadline: 2026-11-02 (notes say '2026-11-02')
      Source: "At the start of the meeting the team agreed that the launch will be on 2026-11-02."
      [!] Clarify: Which launch date is correct: 2026-11-02 or 2026-11-16?
  [item-5] External user access from day one
      The team decided that external users will have access from day one.
      Source: "We decided that external users will have access from day one."
      [!] Clarify: Will external users have access from day one or not in this release?

PROPOSED DECISIONS (not yet agreed) (3)
  [item-2] Proposed launch date change to 2026-11-16
      Laura Schmidt suggested moving the launch to 2026-11-16 because testing is not finished, but the change was not confirmed.
      Owner: NOT ASSIGNED
      Deadline: 2026-11-16 (notes say '2026-11-16')
      Source: "Later, Laura Schmidt said the launch must move to 2026-11-16 because testing is not finished. Nobody confirmed the change."
      [!] Clarify: Should the launch date be moved to 2026-11-16 as suggested by Laura Schmidt?
  [item-4] Proposed deadline change for example project data
      Arjun Rao suggested Priya prepare the data by 2026-10-20 instead because managers are away.
      Owner: NOT ASSIGNED
      Deadline: 2026-10-20 (notes say '2026-10-20')
      Source: "Arjun Rao said Priya should prepare it by 2026-10-20 instead, because the managers are away."
      [!] Clarify: Should the deadline for Priya Nair to prepare the example project data be moved to 2026-10-20?
  [item-6] External user access exclusion proposed by Tom Becker
      Tom Becker stated that external users will not get access in this release.
      Source: "Later Tom Becker said that external users will not get access in this release."
      [!] Clarify: Will external users get access in this release or be excluded as Tom Becker stated?

CONFIRMED ACTIONS (1)
  [item-3] Prepare example project data
      Priya Nair will prepare the example project data by 2026-10-13.
      Owner: Priya Nair
      Deadline: 2026-10-13 (notes say '2026-10-13')
      Source: "Priya Nair will prepare the example project data by 2026-10-13."
      [!] Clarify: Which deadline should Priya Nair follow for preparing the example project data: 2026-10-13 or 2026-10-20?

CONTRADICTIONS FOUND
  - The meeting notes contradict each other regarding the launch date: the team initially agreed on 2026-11-02, but Laura Schmidt later proposed moving it to 2026-11-16.
  - The meeting notes contradict each other regarding the example project data preparation deadline: it was stated that Priya Nair will prepare it by 2026-10-13, but Arjun Rao suggested 2026-10-20.
  - The meeting notes contradict each other regarding external user access: the team decided external users will have access from day one, but Tom Becker later stated they will not get access in this release.

6 of 6 items need clarification.

Review skipped (--no-review). Nothing was saved.
```

---

## D. Failure scenarios

What happened: A missing file, an empty file and a wrong file type each gave a clear message and exit code 1, before any model call was made. A wrong model name (`not-a-real-model`, set for that one run only through the `LLM_MODEL` environment variable) gave an `Analysis failed` message with the 404 reason and exit code 1. Nothing was saved in any of these runs.

```
PS> python -m src.main samples\does_not_exist.md --date 2026-10-06
Cannot read notes: File not found: samples\does_not_exist.md
PS> $LASTEXITCODE
1
PS> python -m src.main samples\empty_notes.md --date 2026-10-06
Cannot read notes: The notes file is empty.
PS> $LASTEXITCODE
1
PS> python -m src.main samples\wrong_type.docx --date 2026-10-06
Cannot read notes: Unsupported file type '.docx'. Allowed: .txt, .md
PS> $LASTEXITCODE
1
PS> $env:LLM_MODEL = "not-a-real-model"
PS> python -m src.main samples\clear_notes.md --date 2026-10-06
Analysis failed: The model call failed (ModelHTTPError): status_code: 404, model_name: not-a-real-model, body: {'error': {'code': 404, 'message': 'models/not-a-real-model is not found for API version v1beta, or is not supported for generateContent. Call ModelService.ListModels to see the list of available models and their supported methods.', 'status': 'NOT_FOUND'}}
PS> $LASTEXITCODE
1
PS> Remove-Item Env:LLM_MODEL
```

---

## E. Busy service (simulated)

Command: `python -m pytest tests\test_retry.py`

What happened: The model service cannot be made busy on demand, so the busy-service behaviour is simulated with a fake agent. A busy response (HTTP 503) is retried automatically with increasing waits (5, 10 and 20 seconds, 4 attempts in total). After the last attempt the user gets a clear message. A wrong model name (HTTP 404) is not retried and fails immediately. The waiting time is switched off inside the tests, so they run in a few seconds.

```
========= test session starts ==========
platform win32 -- Python 3.12.5, pytest-9.1.1, pluggy-1.6.0
rootdir: <project>
configfile: pytest.ini
plugins: anyio-4.15.1, logfire-5.1.1, platformdirs-4.12.3
collected 3 items

tests\test_retry.py ...           [100%]

========== 3 passed in 5.57s ===========
```

---

## F. Approving an item that still has an open question

Command: `python -m src.main samples\example_pdf.md --date 2026-10-06`

What happened: The reviewer approved "Prepare example project data" while its owner was still unknown. Approving
an item with an open question needs an extra confirmation and a typed reason. An empty reason was refused and the
item was shown again. After a reason was given, the item was approved and saved with `approval_note`. The record
kept `needs_clarification: true` and `owner: null`, so no owner was invented. The other items stayed pending and
were not saved.

How this recording was made: the review answers were piped into the program from a list, so the run is repeatable.
The answers are not echoed on screen. The on-screen draft is the same kind of output as in B, so only the result of the review (the saved record) is shown below. The answers, in order, were:

| Item | Answers |
| --- | --- |
| 1. Test with project managers | `s` (skip) |
| 2. Timing of the first test | `s` (skip) |
| 3. Prepare example project data | `a` (approve), `y` (approve anyway), Enter (empty reason, refused), `a`, `y`, then the reason `Owner will be chosen at the next meeting` |
| 4. External user access | `s` (skip) |
| Save prompt | Enter (yes) |

```
PS> "s","s","a","y","","a","y","Owner will be chosen at the next meeting","s","" | python -m src.main samples\example_pdf.md --date 2026-10-06
(draft summary and review prompts omitted here; the draft has the same structure as in B)
PS> Get-Content output\approved_actions.json
[
  {
    "id": "item-3",
    "type": "confirmed_action",
    "title": "Prepare example project data",
    "description": "The team agreed to prepare example project data, but no owner was selected.",
    "owner": null,
    "deadline_raw": null,
    "deadline_date": null,
    "deadline_status": "none",
    "supporting_text": "The team agreed to prepare example project data, but no owner was selected.",
    "needs_clarification": true,
    "clarification_question": "Who should be responsible for preparing example project data? Who should own this action?",
    "status": "approved",
    "was_modified": false,
    "approval_note": "Owner will be chosen at the next meeting",
    "source_file": "example_pdf.md",
    "saved_at": "2026-10-09T07:21:55.147303+00:00"
  }
]
```

---

## Agent decision flow

1. The note reader checks the file type, size, encoding and emptiness. A bad file stops the run with a clear message (case D).
2. The agent reads the notes and may call three tools: `check_deadline` (validates dates; vague wording such as "next month" is never turned into a date), `check_person` (checks the team list, including the two Lauras) and `search_project_info_tool` (looks up fictional project facts; if nothing is found, no fact is added).
3. The model returns a typed `MeetingAnalysis`: topics, risks, owners, deadlines, contradictions and 8 item types (confirmed and proposed decisions, confirmed and possible actions, open questions, background, unclear).
4. Guardrails re-check the model's answer in plain code: every quote must appear in the notes, an owner must appear in the notes and be unambiguous, dates are re-validated, and every item starts as pending. The model cannot approve anything.
5. The user approves, rejects, modifies or completes each item. Approving an item that still has an open question needs a second confirmation. Nothing is approved automatically.
6. Only approved actions are saved, after a final confirmation, to `output/approved_actions.json`.

## What the demonstrations show

- Decisions and actions are kept apart. Proposed decisions are labelled "not yet agreed" (B, C).
- Owners and deadlines are never invented: "NOT ASSIGNED", "UNCLEAR" and "none mentioned" are shown instead (B).
- Laura is not assigned automatically. The reviewer has to name a specific person (B).
- Every item shows its original supporting text from the notes (A, B, C).
- Contradictions are listed, not resolved (C).
- Only approved actions are saved (A, B). Decisions and open questions are never saved.
- File and model failures end with a clear message and exit code 1 (D).
- A busy model service is retried automatically, and a wrong model name fails at once (E).
- Approving an item that still has an open question needs a typed reason, which is saved as `approval_note` (F).

## Possible improvements

- A web or UI review screen instead of the terminal.
- CSV export and a merge across several meetings.
- A cleaner alert when the model's output keeps failing validation.
- A larger set of synthetic test notes in more formats.
- Editing a deadline during review does not update a date written in the description text. Owner edits already do.