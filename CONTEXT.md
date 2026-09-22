# Call → CRM translator: where do I go

Read [`identity.md`](identity.md) and [`rules.md`](rules.md) once, then you know the whole tool.
There are no stages to work through — one transcript goes in, one CRM record comes out. This file
is the map of what each piece is and where to go for a given task.

## Task routing

| I want to... | Go to |
|---|---|
| Understand what this is in one paragraph | [`identity.md`](identity.md) |
| **Translate a call** (drop into a Claude project, paste the transcript) | [`CLAUDE.md`](CLAUDE.md) tells the agent how; the law it follows is [`rules.md`](rules.md) |
| Know the mapping law, field by field (the tie-breaker when unsure) | [`rules.md`](rules.md) |
| See the exact output shape / fields / allowed values | [`reference/`](reference/) — `output-schema.json`, `crm-fields.md`, `enums.md` |
| Prove the output didn't invent anything | run `python3 verify-translation.py --self-test` |
| Check one specific call against its transcript | run `python3 verify-translation.py -v <call.txt> <out.json>` |
| Turn a raw JSON record into the readable card | run `python3 render-view.py <out.json>` |
| See worked examples across different industries | [`samples/`](samples/) — four calls, each as transcript + JSON + readable card |
| See what a bare model does without this folder | [`evidence/control-run.md`](evidence/control-run.md) |
| Know what a passing check does NOT prove | [`LIMITS.md`](LIMITS.md) |

## The three pieces, plainly

- **The brain — [`rules.md`](rules.md).** The law the AI obeys: which fact goes in which field,
  what to do when the call is silent, and the two fields it must refuse to guess.
- **The referee — [`verify-translation.py`](verify-translation.py).** Does NOT trust the AI. It
  re-checks every field against the transcript and fails the run if any quote is not verbatim on
  the line it cites. [`tests/fixtures/`](tests/fixtures/) holds eight deliberately-broken outputs
  it must catch; CI runs them on every push.
- **The display — [`render-view.py`](render-view.py).** Turns the machine-readable JSON into the
  human-readable card, with each value's source line printed beside it.

## The shape of the folder

```
identity.md      what it is          reference/       the exact output spec
rules.md         the mapping law     samples/         four worked calls
CLAUDE.md        the agent's job     tests/fixtures/  the eight traps the referee must catch
README.md        the human overview  evidence/        the bare-model control run
LIMITS.md        what green does NOT prove
verify-translation.py / render-view.py    the referee and the display
```
