# examples.md — the contract holding across three calls

Three real (pseudonymized) discovery calls, three outputs, one shape. The full inputs and
outputs are in [`samples/`](samples/); this file shows the contract's behaviour on the parts
that matter. Every value cites the line it came from. Run `python3 verify-translation.py
-v <transcript> <output.json>` to see the full trace for any of them.

## 1. Nakamura — a seller, full call

Input: [`samples/discovery-call-nakamura.txt`](samples/discovery-call-nakamura.txt)
Output: [`samples/discovery-call-nakamura.output.json`](samples/discovery-call-nakamura.output.json)
Readable: [`samples/discovery-call-nakamura.record.md`](samples/discovery-call-nakamura.record.md)

What this one proves:

- **The comp is NOT the deal value.** Line 12 says two things: "hoping somewhere around
  six-fifty" (the prospect's expectation) and "a house two doors down sold for six-eighty"
  (a comp). `deal.value` = 650000, and the 680 comp goes to a `financial` note. Blending them
  is the `fail_comp_as_value` fixture, and the gate fails it.
- **The objection is captured, not dropped.** The commission worry on line 18 becomes a
  `notes` entry with `category: "objection"`. The brief names a dropped objection as the
  canonical failure.
- **A conditional next step is NOT a task.** The agent floats a house walk on line 25 but the
  prospect never commits. It goes to `unmapped` with the reason, not to `tasks`.
- **stageId and priority refuse.** Both are `requires_judgment`, every run.

## 2. Priya — a buyer, messy, missing fields

Input: [`samples/discovery-call-priya.txt`](samples/discovery-call-priya.txt)
Output: [`samples/discovery-call-priya.output.json`](samples/discovery-call-priya.output.json)

What this one proves:

- **Same shape, more empties.** No phone digits, no email, no timeline were spoken, so those
  fields are `not_in_source`. The output has every field the Nakamura output has — just more
  of them empty. The shape did not shrink because the call was thinner.
- **First-name-only stays first-name-only.** Line 2 gives "Priya" and no surname. `contact.name`
  = "Priya"; no surname is invented.
- **A named referrer maps to `referral`.** "My coworker Devon, you helped him buy" (line 10) ->
  `contact.source` = "referral" and a relation `Devon (coworker)`.
- **The budget is the pre-approval, quoted.** "pre-approved for four hundred" -> `deal.value`
  = 400000, with the derivation declared.

## 3. Osei — an estate sale, a different call shape entirely

Input: [`samples/discovery-call-osei.txt`](samples/discovery-call-osei.txt)
Output: [`samples/discovery-call-osei.output.json`](samples/discovery-call-osei.output.json)

What this one proves:

- **No price at all is fine.** The seller never states a target price, so `deal.value` is
  `not_in_source`. The translator does not guess one from the comp discussion or the property
  condition.
- **A yard sign has no enum value.** "I saw your sign on the corner of Third and Elm" -> source
  `other`, with the real origin in a `context` note. Not forced into `ads` or `website`.
- **Empty `relations` and empty `unmapped` are legal.** No relations were named; everything
  mapped. The arrays are present and empty, not omitted. Shape holds.
- **A different due phrase, same rule.** "by Monday" is kept verbatim as `dueAt`, not resolved
  to a date.

## The invention attacks the gate catches

Each file in [`tests/fixtures/`](tests/fixtures/) is a broken output that must FAIL the gate.
They cover: an invented date, an invented next step, a misspelled name, a correct quote on the
wrong line (the neighbour-line swap), the comp blended into the deal value, a guessed pipeline
stage, an illegal source enum, and a dropped top-level key (shape drift). Run them all with
`python3 verify-translation.py --self-test`.
