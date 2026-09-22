# Control run — bare model, no folder

**Method (frozen before the run):** the same transcript given to a general assistant with
**no folder, no rules.md, no schema, no gate** — just "turn this call into a CRM record the way
you naturally would." One shot, one API call. The point is not whether the bare model is
*useful* (it is) — it is to show **what it invents when nothing stops it**, and therefore what
this folder actually adds.

The bare model produced a clean, confident, well-formatted CRM record. It also invented, guessed,
or silently normalized **ten** things that are not in the transcript. Every one would enter a
real CRM as if the prospect had said it.

| # | Bare model wrote | Transcript actually says | What this folder does instead |
|---|---|---|---|
| 1 | Title: "likely VP Finance / Head of Finance" | never stated | `not_in_source` |
| 2 | Company: **Northpeak** | only the email domain `northpeak.io` — never spoken as a company | `not_in_source` (do not infer a company from a domain) |
| 3 | Phone: **(415) 222-8765** | "four one five, two two two, eight seven six five" | `4152228765` — digits joined, no parens/dash the speaker didn't say |
| 4 | Stage: "Qualified / Proposal to be sent" | the call never states its own pipeline stage | `requires_judgment` — refused on purpose |
| 5 | Close probability: "Medium–High" | invented | not a field; a guess the tool never makes |
| 6 | Deal name: "Northpeak — BrightLedger Migration" | company name inferred (see #2) | title derived only from spoken words |
| 7 | Task: "Follow-up call to review proposal — ~Following week" | nobody agreed to this on the call | not created — only committed actions become tasks |
| 8 | Sentiment: "Positive / engaged" | invented | not a field; the tool files facts, not reads |
| 9 | BANT scoring (Budget ✅ / Authority ⚠️ / …) | invented judgment | not a field |
| 10 | Due dates "After Friday", "~Following week" | not stated | verbatim "Friday" only; no resolved dates |

## The honest part

The bare model **caught the same real facts** — the $30k vs $80k distinction, the migration
objection, the CFO approval threshold, the March timeline. On extraction it is genuinely good.

So the folder's value is **not** "it finds more." It is: **every field it writes can be checked
against the transcript in one glance, and it refuses to guess the four things above rather than
dressing them up as facts.** The bare model's record reads more complete and is partly fiction.
This one reads more sparse and is entirely checkable. That is the whole trade, stated plainly.

The bare model's #2 (company inferred from the email domain) is the sharpest example: it is the
kind of guess that looks like diligence and quietly plants an unspoken fact in the CRM. The gate
in this folder fails any field whose evidence is not verbatim in the call, so that guess cannot
survive.
