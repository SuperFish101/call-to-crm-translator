# The output fields, traced to the real CRM

This translator does not invent a schema. Every field below is a real field on a
production CRM record (a GoHighLevel-style multi-tenant CRM), and the "CRM source"
column names the TypeScript type and file it comes from. The three record types a discovery
call touches are Contact, Deal and Task, plus free-form Notes. The enums are vendored in full
in [`enums.md`](enums.md) so the contract is checkable here without the CRM's own source.

Field-value shape is defined in [`output-schema.json`](output-schema.json). Every populated
field is `{ value, evidence, source_lines, derivation? }`; every empty field is
`{ value: null, status }`. The two status values are defined at the bottom.

## contact — from `Contact` in `src/types/contacts.ts`

| Output field | CRM field | Type | Notes |
|---|---|---|---|
| `contact.name` | `Contact.name` | string | The prospect's name, spelled the way it appeared in the transcript. |
| `contact.phone` | `Contact.phone` | string | Digits only, spoken digits joined. See rules.md "phone normalization". |
| `contact.email` | `Contact.email` | string | Spoken "at"/"dot" expanded to `@`/`.`. See rules.md "email normalization". |
| `contact.company` | `Contact.company` | string | Usually `not_in_source` on a residential call. |
| `contact.address` | `Contact.address` | string | The prospect's OWN mailing address if stated. NOT the subject property (that is the deal). |
| `contact.source` | `Contact.source` | `ContactSource` enum | Must be one of the enum values in [`enums.md`](enums.md). If the stated origin has no enum value, maps to `other` and the real origin is preserved in `notes`/`unmapped`. |
| `contact.personalNotes` | `Contact.personalNotes` | string | Rapport / personal life facts stated on the call (`Contact.personalNotes` is defined as "rapport / personal notes about the human, NOT business activity"). |
| `contact.relations[]` | `Contact.relations[]` | `{name, relationship}` | Spouse, kids, coworkers named on the call. |

## deal — from `Deal` in `src/types/deals.ts`

| Output field | CRM field | Type | Notes |
|---|---|---|---|
| `deal.title` | `Deal.title` | string | A short label. Derived from the subject property + intent; derivation is declared. |
| `deal.value` | `Deal.value` | number | The prospect's STATED price expectation, normalized to whole dollars. Carries the verbatim quote as evidence and the normalization as `derivation`. |
| `deal.currency` | `Deal.currency` | string | **`not_in_source`.** A call rarely states a currency; the translator does not pretend it did. The CRM's downstream USD default is recorded in `meta.assumptions`, not written into the field. |
| `deal.timeline` | (maps to a `customFields` value / operator's timeline field) | string | The stated timeframe for the deal ("list in the spring, March or April"). |
| `deal.stageId` | `Deal.stageId` | `PipelineStageId` enum | **Always `requires_judgment`.** Assigning a pipeline stage is a decision the operator makes, not a fact in the transcript. See rules.md "What the translator refuses to set". |
| `deal.priority` | `Deal.priority` | `DealPriority` enum | **Always `requires_judgment`.** Same reason as stageId. |

## tasks[] — from `Task` in `src/types/tasks.ts`

| Output field | CRM field | Type | Notes |
|---|---|---|---|
| `tasks[].title` | `Task.title` | string | An action someone committed to ON the call. Only real, stated commitments. |
| `tasks[].dueAt` | `Task.dueAt` | date | The stated due point ("by Thursday"). Kept as the verbatim phrase; NOT resolved to a calendar date (that needs the call date, which is not in the transcript). |
| `tasks[].notes` | `Task.notes` | string | Optional detail on the task, quoted. |

## notes[] — from `Note` in `src/types/contacts.ts`

Free-form notes attached to the contact. `category` is one of `objection`, `context`,
`property`, `financial` — a fixed classification of WHAT KIND of fact it is, not a judgment
of the prospect. The objection category exists because the brief names a dropped objection
as the canonical failure: "A CRM note that silently omits the objection the prospect raised
is worse than useless."

## unmapped[]

Anything said on the call that is business-relevant but has no home in the fields above.
Recording it here is how the translator proves it did not silently drop something. Each
entry names the line(s), the text, and why it did not map.

## The two empty-field statuses

- **`not_in_source`** — the call never contained this fact. The prospect did not give a
  company name, so `contact.company` is `not_in_source`.
- **`requires_judgment`** — the CRM has this field, and the call may even hint at it, but
  assigning a value is a DECISION, not a transcription. The translator refuses, because the
  brief disqualifies judgment. `deal.stageId` and `deal.priority` are always this.

The difference matters: `not_in_source` says "the source is silent"; `requires_judgment`
says "this is not the translator's call to make." Conflating them would hide a refusal
behind a shrug.
