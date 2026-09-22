# Call → CRM translator

Turn a sales / discovery-call transcript into a CRM record — a contact, a deal, tasks,
and notes — in fixed fields, where **every value cites the transcript line it came from** and
nothing is invented. If the call didn't say it, the field says `not in source`. If filling it
would be a guess, the field says `requires human judgment`. It never makes up a price, a date,
a name spelling, or a next step nobody agreed to.

Anyone who fields sales calls does this by hand: after every call, retyping what the prospect
said into their CRM — name, number, the price they hope for, the objection they raised, the
thing they agreed to do next. 5–10 minutes of dull data entry per call. Nobody automates it
because the last tool that tried invented a budget or a close date the prospect never gave.
This one refuses to.

The target fields are the real record shape from a production CRM (a GoHighLevel-style CRM).
See [`reference/crm-fields.md`](reference/crm-fields.md).

## Use it (drop into a Claude project)

1. Add this folder to a Claude project.
2. Tell Claude: **"Translate this call. Follow rules.md exactly."** Paste the transcript (one
   utterance per line).
3. Claude returns JSON matching [`reference/output-schema.json`](reference/output-schema.json),
   plus a readable card. Every populated field carries its source line; every empty field
   carries a reason.

The readable version of one output:

```
## Contact
- **Name:** Angela Ruiz  (line 2: "It's Angela, Angela Ruiz.")
- **Phone:** 4152228765  (line 4: "four one five, two two two, eight seven six five")
- **Source:** other  (line 6: "found you through the review on that G2 comparison page")
## Deal
- **Value:** 30000  (line 12: "Thirty could work if the migration isn't a nightmare")
- **Pipeline stage:** requires human judgment
## Notes
- **[objection]** Migration risk is the real worry...  (line 12: "we can't lose data")
- **[financial]** Competitor quoted ~$80k/yr — NOT the deal value.  (line 10)
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
operator makes, not facts in the call. Guessing them is the judgment a translator must not do.

## What's here

New here? Read [`CONTEXT.md`](CONTEXT.md) — it maps every file and routes you by task. The
short version: [`rules.md`](rules.md) is the law the AI obeys, `verify-translation.py` is the
gate that re-checks it, `render-view.py` prints the readable card, [`samples/`](samples/) has
four worked calls across different industries, and [`LIMITS.md`](LIMITS.md) says what a green
run does NOT prove.
