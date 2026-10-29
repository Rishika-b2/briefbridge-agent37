# BriefBridge - Meeting-to-Handoff Agent

Private working prototype. A separate project from LabMate. It turns notes into an evidence-linked action register with unresolved fields visible and no automatic messaging or scheduling.

## Status

Local validator and UI are built. The 13 local unit tests pass. The supplied synthetic validator fixture has four evidence-linked candidate actions and one rejected invented proposal. A genuine Agent37 run on 29 October 2026 created its own four-action proposal, passed all 13 tests and saved a handoff pack. See AGENT37_RUN.md and hosted_run/ for retrieved evidence. No public repository or challenge submission exists.

## Run locally

Python 3.10+, standard library only:

```
python app.py
```

Open http://127.0.0.1:8766. Click Load synthetic example, review the notes/proposal, then Validate and review handoff. This is a local review UI, not an AI extraction endpoint.

For a saved handoff pack:

```
python -m unittest discover -s tests -v
python briefbridge.py samples/notes.txt samples/proposal.json --out output
```

Outputs are report.html, handoff.json and review.md. Keep real notes local or upload only after permission to the intended service. Never commit private meeting notes.

## Agent37 integration

See agent37/WORKFLOW.md. The hosted agent reads the notes, extracts candidate actions with exact source lines, runs the validator and saves a handoff pack on its own computer. It must create its own proposal, rather than present the included validator fixture as an AI extraction. This workflow was executed on the approved Free instance on 29 October 2026.

## Guardrails and limits

- Source-line numbers and exact quotes are checked. Wrong references are rejected.
- Owners and due phrases must appear verbatim in the evidence, or they are cleared and flagged. Missing fields stay unresolved.
- Relative dates stay as written. No guessed calendar deadlines.
- Matching words does not establish intent, semantic correctness, authority or a commitment. Every accepted candidate still needs human review.
- A source quote may include discussion, conditional offers or requests rather than a firm assignment. Read context before relying on it.
- No email/calendar connection, external API key, paid dependency or autonomous side effect.
- The fixture is synthetic. No claim of real productivity results or completed tasks.

This is a localhost development server, not a production internet service. Keep HTML reports and notes private until reviewed.
