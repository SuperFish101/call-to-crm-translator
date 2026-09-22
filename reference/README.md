# reference/ — the contract

This folder is the written-down contract. If the output schema is not in a file a reader can
open, there is no way to check whether the translator kept its promise. The three files:

| File | What it holds |
|---|---|
| [`output-schema.json`](output-schema.json) | The JSON Schema (draft-07) the output must validate against. The fixed shape, and the `{value,evidence,source_lines}` / `{value:null,status}` field rule. |
| [`crm-fields.md`](crm-fields.md) | Every output field mapped to the real CRM field it comes from, naming the TypeScript type and file so a reader can open the codebase and check. |
| [`enums.md`](enums.md) | The closed sets an enum field must obey: `ContactSource`, `PipelineStageId`, `DealPriority`, and the note categories. Copied from the CRM types. |

The CRM is LeadStack, a GoHighLevel-style multi-tenant CRM. The field shapes come from its
`src/types/contacts.ts`, `deals.ts`, and `tasks.ts`. This translator does not invent a schema;
it targets a real one.

The gate (`verify-translation.py`, one level up) enforces the parts of this contract that can
be checked mechanically: shape, verbatim evidence, legal enums, and the refusals. What it
cannot check is in `LIMITS.md`.
