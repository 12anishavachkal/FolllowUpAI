# Demo results

Meeting date used for all runs: 2026-10-06
Model used (LLM_MODEL): <fill in>

| # | Scenario | Command | Pass / fail | What I observed | Screenshot |
|---|---|---|---|---|---|
| A | Clear notes | python -m src.main samples\clear_notes.md --date 2026-10-06 | | | docs/demo/A_clear.png |
| B | Ambiguous notes | python -m src.main samples\example_pdf.md --date 2026-10-06 | | | docs/demo/B_ambiguous.png |
| C | Contradictory notes | python -m src.main samples\contradictory_notes.md --date 2026-10-06 --no-review | | | docs/demo/C_contradictory.png |
| D1 | Missing file | python -m src.main samples\does_not_exist.md --date 2026-10-06 | | | docs/demo/D1_missing.png |
| D2 | Empty file | python -m src.main samples\empty_notes.md --date 2026-10-06 | | | docs/demo/D2_empty.png |
| D3 | Wrong file type | python -m src.main samples\wrong_type.docx --date 2026-10-06 | | | docs/demo/D3_wrongtype.png |
| D4 | Model failure (bad model name) | same as A with a wrong LLM_MODEL | | | docs/demo/D4_model.png |
| D5 | Busy model retry (503) | already captured earlier | | | docs/demo/D5_busy.png |