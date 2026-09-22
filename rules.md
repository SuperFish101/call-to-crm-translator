# rules.md — how the mapping works

This is the law. When a run and this file disagree, this file wins. Read it top to bottom
before translating anything. The output shape it produces is fixed by
[`reference/output-schema.json`](reference/output-schema.json).

## The three standing rules

1. **Fixed shape, every time.** Emit every field in the schema on every run, in schema
   order, whether or not the call filled it. A short call produces the same shape as a long
   one, with more empty fields. The shape never depends on the input.

2. **Nothing invented.** Every populated field carries `evidence` — a substring that appears
   VERBATIM in the transcript — and `source_lines`, the line number(s) that substring is on.
   If you cannot quote it, you cannot write it. No claim, number, name, date, or spelling
   that is not in the transcript may appear in a `value`. The one exception is a declared
   assumption (see rule below), which is listed in `meta.assumptions` and never dressed up as
   a fact from the call.

3. **Nothing that matters dropped.** Every business-relevant statement in the call must land
   somewhere: a field, a note, a task, or the `unmapped` list. The objection especially — if
   the prospect raised a concern, it MUST appear as a `notes` entry with `category:
   "objection"`. A record that eats the objection has failed the brief by name.

## value vs evidence vs derivation

- **`evidence`** is always a verbatim substring of the transcript. This is the thing the gate
  checks and the judge traces.
- **`value`** is what gets written into the CRM field. Often it equals the evidence. When it
  differs (a normalized phone number, a dollar figure parsed from "six-fifty"), you MUST add
  a **`derivation`** string naming the deterministic rule you applied. No derivation may add
  information — only reshape what the evidence already contains.
- If applying a derivation would require information not in the evidence, do not derive.
  Leave the value as the verbatim phrase, or mark the field empty.

## The two empty statuses (never guess instead of using them)

- **`not_in_source`** — the call is silent on this fact. Use it freely. It is not a failure;
  it is the honest answer.
- **`requires_judgment`** — the field needs a decision, not a transcription. Use it for the
  fields listed under "What the translator refuses to set". Never downgrade a
  `requires_judgment` field to a guessed value because the call "sort of implied" it.

## Field-by-field mapping

### contact.name
The prospect's name as spoken. Spell it the way the transcript spells it, even if that is an
unusual spelling. If only a first name is given, that is the value; do not invent a surname.

### contact.phone — normalization
Evidence = the verbatim spoken number ("seven, one, six, five, five, five, ..."). Value =
those digits joined in order, nothing added: `7165550198`. Derivation: "spoken digits joined
in order". Do NOT add a country code, area-code parentheses, or dashes the speaker did not
say. If digits are missing or unclear, keep only what was said and note the gap in `unmapped`.

### contact.email — normalization
Evidence = the verbatim spoken address ("trevor.nakamura at gmail dot com"). Value = the same
with spoken "at" -> `@` and " dot " -> `.`, lowercased only if the speaker did not specify
case: `trevor.nakamura@gmail.com`. Derivation: "spoken 'at'->@, 'dot'->., joined". Add no
domain the speaker did not say.

### contact.company
Almost always `not_in_source` on a residential seller call. Fill only if the prospect names
their own company/employer AND it is relevant as a company field. A mentioned employer that
is just rapport goes to `personalNotes`, not here.

### contact.address
The prospect's OWN mailing/home address, only if distinct and stated. The SUBJECT PROPERTY
being sold is NOT the contact address — it belongs to the deal. If the only address on the
call is the property being sold, `contact.address` is `not_in_source` and the property lands
in a `property` note and/or the deal title.

### contact.source
One of the `ContactSource` enum values in [`reference/enums.md`](reference/enums.md). Follow
the mapping guidance there exactly. When the stated origin does not fit an enum value, use
`other` and preserve the real origin verbatim in a `context` note. Never map "mentioned a
social network" to that network's channel value.

### contact.personalNotes
Rapport and personal-life facts: a third kid on the way, moving in with in-laws, a team they
support. Business facts (price, timeline, objection) do NOT go here — they have their own
fields. This mirrors the CRM's own definition of the field.

### contact.relations[]
People named as connected to the prospect (spouse, kids, coworkers). Each is `{name,
relationship, evidence, source_lines}`. "my wife Danielle" -> `{name: "Danielle",
relationship: "wife"}`. If a person is mentioned with no name ("a third kid on the way"),
that is NOT a relation with a name — it goes to `personalNotes` instead.

### deal.title
A short label for the opportunity. Derived, with derivation declared, from the intent + the
subject property: e.g. evidence "selling our place over on Cambridge Court in Elk Grove" ->
value "Sell Cambridge Court, Elk Grove". The derivation may only reshape words already in the
evidence. Do not add a price, a name, or a date to the title.

### deal.value — price normalization
Evidence = the verbatim price the PROSPECT stated as their own expectation ("around
six-fifty"). Value = `650000`. Derivation: "'six-fifty' in a home-price context = 650,000".
CRITICAL: only the prospect's own stated expectation is the deal value. A comp the agent or
prospect mentions ("a house two doors down sold for six-eighty") is NOT the deal value — it
is a `financial` note. Never blend a comp into the expected price.

### deal.currency
The call almost never states a currency, so this field is `not_in_source`. The CRM applies
its own default (USD) downstream; that default is recorded in `meta.assumptions` as a plain
sentence so a reader sees it, but it is NOT written into the field as if the call said it.
This keeps the "nothing unsourced in a value" promise absolute. If a call DOES state a
currency, that becomes sourced evidence and the field is filled normally.

### deal.timeline
The stated listing timeframe, verbatim as evidence ("list in the spring, so probably March
or April next year"). Keep the phrase; do not convert "spring" to a specific date.

### deal.stageId and deal.priority
See "What the translator refuses to set" below. Always `requires_judgment`.

### tasks[]
One task per real commitment made ON the call — something a person said they would do. "Can
I get that CMA over to you by this Thursday?" + "Thursday works" -> a task. `title` =
"Send CMA for Cambridge Court" (derived from the quote), `dueAt` evidence = "by this
Thursday", value = "this Thursday" kept verbatim (NOT resolved to a date — the transcript
has no call date, so a calendar date would be invented). Do NOT create tasks for things
merely discussed but not committed to.

### notes[]
Facts that belong on the record but are not a structured field. Categories:
- **`objection`** — any concern, hesitation, or pushback the prospect raised. Mandatory to
  capture if present. "commission... six percent felt like a lot... discount brokers... I
  need to understand what I'm actually paying for" is one objection note.
- **`property`** — facts about the home being sold: location, updates, roof, kitchen.
- **`financial`** — money facts that are not the deal value: the comp, the remaining
  mortgage balance.
- **`context`** — origin, life situation framing, anything that sets the scene and does not
  fit a field or another category.

### unmapped[]
Anything business-relevant with no home above. Prefer mapping to a field or note; use
`unmapped` when nothing fits, so the drop is visible and explained. An empty `unmapped` array
is fine when everything mapped.

## What the translator refuses to set

These CRM fields exist, but assigning them is a DECISION the operator makes, not a fact the
transcript contains. The translator sets them to `requires_judgment`, every run, on purpose:

- **`deal.stageId`** — where in the pipeline this sits (new / contacted / qualified /
  proposal / won / lost) is the agent's call about their own process. A discovery call does
  not state its own pipeline stage.
- **`deal.priority`** — high / medium / low is a business decision about where to spend time.
  "Third kid on the way, wants to list in spring" does not encode a priority; the operator
  decides that.

Refusing these is not a gap in the tool. It is the tool refusing to do the judgment the brief
says a translator must not do. A downstream operator fills them in one click; the translator's
job is to never fake them.

## Declared assumptions

Anything the output states that is NOT derived from the transcript goes in `meta.assumptions`
as a plain sentence. Today that list is exactly one item: a note that the CRM applies a
default currency of USD downstream, since a call rarely states a currency. Note the
difference from a field value: the assumption is recorded in `meta`, NOT written into
`deal.currency` (which stays `not_in_source`). No `value` anywhere carries information that
is not in the transcript. If you ever find yourself wanting to write an unsourced `value`,
stop — that is the invention the brief disqualifies.
