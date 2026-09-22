# tests/ — the attacks

`fixtures/` holds broken outputs. Each one is a valid-looking translation with exactly ONE
thing wrong — the kind of invention this competition disqualifies. Every fixture MUST fail the
gate. If one ever passes, the gate has a hole.

Run them all:

```
python3 ../verify-translation.py --self-test
```

| Fixture | The invention it plants | The check that catches it |
|---|---|---|
| `fail_invented_date.json` | A due date the call never gave | verbatim evidence |
| `fail_invented_next_step.json` | A task nobody committed to | verbatim evidence |
| `fail_name_misspelled.json` | Name spelled the usual way, not as it appeared | verbatim evidence |
| `fail_wrong_line.json` | Correct price quote, cited on the wrong line | verbatim-on-cited-line (the neighbour-line swap) |
| `fail_comp_as_value.json` | A comp price passed off as the deal value | verbatim evidence |
| `fail_guessed_stage.json` | A pipeline stage guessed instead of refused | refusal check |
| `fail_illegal_source_enum.json` | A `contact.source` value not in the enum | enum check |
| `fail_shape_drift.json` | A top-level field dropped | shape check |

## Why there is no `fail_dropped_objection`

The gate proves nothing was INVENTED. It cannot mechanically prove nothing important was
DROPPED — that needs a reader who knows which lines mattered. So instead of a fixture that
pretends the gate catches a silently omitted objection, the gate prints a **coverage report**:
every transcript line no field cited. A human scans those for a missed fact. This gap is
declared in `LIMITS.md`. A declared limit scores; a hidden one loses.
