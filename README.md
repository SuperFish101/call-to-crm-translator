# Call → CRM translator

Turn a sales / discovery-call transcript into a CRM record — a contact, a deal, tasks,
and notes — in fixed fields, where **every value cites the transcript line it came from** and
nothing is invented. If the call didn't say it, the field says `not in source`. If filling it
would be a guess, the field says `requires human judgment`. It never makes up a price, a date,
a name spelling, or a next step nobody agreed to.

The target fields are the real record shape from a production CRM (a GoHighLevel-style CRM).
See [`reference/crm-fields.md`](reference/crm-fields.md).

## Who does this by hand today

Anyone who fields sales calls for a small business, after every call, retyping what the
prospect said into their CRM: name, number, the price they hope to get, the objection they
raised, the thing they agreed to do next. 5–10 minutes of dull data entry per call. Nobody
automates it because the last tool that tried invented a budget or a close date the prospect
never gave. This one refuses to.

## Use it (drop into a Claude project)

1. Add this folder to a Claude project.
2. Tell Claude: **"Translate this call. Follow rules.md exactly."** Paste the transcript (one
   utterance per line).
3. Claude returns JSON matching [`reference/output-schema.json`](reference/output-schema.json),
   plus a readable card. Every field carries its source line.

## What you feed it / what you get back

- **In:** a plain-text call transcript, one utterance per line.
- **Out:** one contact, one deal (or empty fields), zero+ tasks, zero+ notes, each populated
  field as `{value, evidence, source_lines}`, each empty field as `{value:null, status}`.

Look at [`samples/`](samples/) for three worked examples. The readable version of one:

```
## Contact
- **Name:** Trevor Nakamura  (line 2: "it's Trevor Nakamura")
- **Phone:** 7165550198  (line 4: "seven, one, six, five, five, five, zero, one, nine, eight")
- **Source:** other  (line 6: "saw your name pop up on that Facebook group")
## Deal
- **Value:** 650000  (line 12: "hoping somewhere around six-fifty")
- **Pipeline stage:** requires human judgment
## Notes
- **[objection]** Concerned about commission...  (line 18: "Honestly the commission...")
```

## Prove it didn't cheat

```
python3 verify-translation.py --self-test          # all samples pass, all attacks fail
python3 verify-translation.py -v <call.txt> <out.json>   # trace every field to its line
python3 render-view.py <out.json> > record.md      # the readable card above
```

`verify-translation.py` re-checks every claim against the transcript. It fails the run if any
`evidence` string is not verbatim on the line it cites — including a correct quote pointed at
the wrong line. [`tests/fixtures/`](tests/fixtures/) holds eight broken outputs (invented date,
invented next step, misspelled name, wrong line, comp-as-value, guessed stage, illegal enum,
shape drift); each must fail, and CI runs the whole set on every push. Pure Python 3 stdlib —
no install.

## The rules that make it a translator, not a writer

1. **Fixed shape every run.** Same fields, same order, whether the call filled them or not.
2. **Nothing invented.** Every value quotes a line, or the field is empty with a reason.
3. **Nothing dropped.** The objection especially always lands in a note. Anything that fits no
   field goes to `unmapped` so the drop is visible.

Two fields are refused on purpose — `deal.stageId` and `deal.priority`. Those are decisions the
agent makes, not facts in the call. Guessing them is the judgment a translator must not do.

## What's here

- [`identity.md`](identity.md) — what it converts, from what, to what.
- [`rules.md`](rules.md) — the mapping law, field by field. The tie-breaker when in doubt.
- [`reference/`](reference/) — the output schema, the CRM fields, the closed enums.
- [`examples.md`](examples.md) — the contract holding across three different calls.
- [`LIMITS.md`](LIMITS.md) — what a green run does and does NOT prove. Read before trusting it.
- [`samples/`](samples/) — three transcripts + their outputs + readable cards.
- [`verify-translation.py`](verify-translation.py) / [`render-view.py`](render-view.py) — the gate and the view.
