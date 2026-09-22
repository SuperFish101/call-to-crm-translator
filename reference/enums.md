# Closed enums the output must obey

These are copied from the real CRM type definitions. When an output field is one of these
enums, its `value` MUST be a member of the set below and nothing else. If the transcript
does not justify any member, the field is empty (`not_in_source` or `requires_judgment`),
never a guessed member.

## ContactSource — `src/types/contacts.ts`

```
"website-form" | "web-chat" | "booking-page" | "community" | "get-leads"
| "website" | "referral" | "ads" | "other"
| "facebook" | "instagram" | "webinar" | ""
```

Mapping guidance (the only allowed reasoning; anything ambiguous goes to `other`):

- A person met in real life who then looked you up -> `other`. The real origin
  ("open house, then the neighborhood Facebook group") is preserved verbatim in a
  `context` note and/or `unmapped`, because it does not fit any enum value cleanly.
- **Do NOT map "a Facebook group" to `facebook`.** In this CRM `facebook` means a Facebook
  Messenger DM inbound stamped by the Meta webhook — a specific channel, not "the prospect
  mentioned Facebook." Mapping it there would be an invented claim about how the lead
  entered the system.
- `referral` only when the prospect names a person who referred them.
- Empty string `""` is a legal value (unknown), but prefer `not_in_source` on the field so
  the reason is explicit.

## PipelineStageId — `src/types/deals.ts`

```
"new" | "contacted" | "qualified" | "proposal" | "won" | "lost"
```

The translator NEVER sets this. It is always `requires_judgment`. Rationale in rules.md.

## DealPriority — `src/types/deals.ts`

```
"high" | "medium" | "low"
```

The translator NEVER sets this. Always `requires_judgment`.

## Note category (this translator's own fixed set, not a CRM enum)

```
"objection" | "context" | "property" | "financial"
```

This classifies the KIND of fact, so a reader can find the objection quickly. It is a
label on the note, not a judgment about the prospect.
