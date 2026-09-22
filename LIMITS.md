# LIMITS.md — what a PASS does and does not prove

Read this before trusting a green run. The gate (`verify-translation.py`) is strong on one
thing and silent on others, and saying so plainly is part of the contract.

## What a PASS proves

- **Every value traces to a cited line.** Each populated field's `evidence` string appears
  VERBATIM on the transcript line(s) it cites. A value with no source, or a value whose quote
  is not actually on the cited line, fails the run. This is the anti-invention guarantee.
- **The shape is fixed.** Every required field is present, in the schema's structure. A
  dropped or renamed field fails. All three sample outputs share one shape (checked by
  `check_shapes_match`).
- **Enums are legal.** `contact.source` is a real `ContactSource`; `deal.stageId` /
  `deal.priority`, if ever set, are legal members.
- **The refusals hold.** `deal.stageId` and `deal.priority` are `requires_judgment` every
  run. A guessed stage or priority fails.
- **A misquote on the right line fails.** A correct line number with words the speaker did not
  say fails, because the check is verbatim-substring, not line-number-only. This is the
  neighbour-line-swap defense that the comp #12 judges named as the single best thing in that
  entry.

## What a PASS does NOT prove

1. **That the value is the RIGHT reading of the evidence.** The gate checks that the quote is
   on the line. It cannot check that "six-fifty" should be 650000 and not 6.50 — that
   derivation is human-readable and declared, but not machine-verified against world
   knowledge. A wrong derivation with a real quote passes the gate. Mitigation: the
   `derivation` field is printed in the `-v` trace and the markdown view, so a human sees the
   reasoning and can reject it.

2. **That nothing was DROPPED.** The gate proves nothing was INVENTED, not that everything
   important was captured. "Nothing dropped" cannot be proven mechanically without the gate
   knowing which lines mattered. Mitigation: the `coverage` report lists every transcript line
   NO field cited, so a human scans those for a missed fact. On the samples, uncited lines are
   agent questions and filler; a real dropped objection would show up as an uncited
   content-bearing line.

3. **That a JUDGMENT-trap mapping is correct.** Example: mapping "a Facebook group" to source
   `other` (right) vs `facebook` (wrong — that means a Messenger DM in this CRM). Both are
   legal enum values and both quote a real line, so the gate passes either. rules.md and
   enums.md forbid the wrong one in writing, but the gate cannot enforce it. This is a
   deliberate, declared limit. A human or a second-model review is the check here.

4. **That the transcript itself is accurate.** Garbage in, faithfully-filed garbage out. If
   the transcript mis-hears a number, the translator faithfully carries the mis-heard number
   and cites it. The translator's job is fidelity to the transcript, not to the call.

## The one honest gap we did not close

`fail_dropped_objection` is not a committed fixture, because the gate cannot mechanically
detect a silently omitted objection (see limit 2). We ship the coverage report instead of
pretending the gate catches it. A declared gap scores better than a hidden one.
