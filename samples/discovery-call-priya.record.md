# CRM record from samples/discovery-call-priya.txt

_Translated by call-to-crm v1.0.0 from a 16-line transcript. Every value below cites the transcript line it came from. Empty fields say why._

**Declared assumptions (not from the call):**
- The CRM applies a default currency of USD downstream. The call states no currency, so deal.currency is left not_in_source rather than filled.

## Contact
- **Name:** Priya  _(line 2: "Yeah this is Priya")_
- **Phone:** _not in source_
- **Email:** _not in source_
- **Company:** _not in source_
- **Address:** _not in source_
- **Source:** referral  _(line 10: "My coworker Devon, you helped him buy last year. He said call you.")_
- **Personal notes:** First-time buyer; nervous about the process.  _(line 4: "first place, kind of nervous about the whole thing honestly")_
- **Relations:**
  - Devon (coworker)  _(line 10: "My coworker Devon")_

## Deal
- **Title:** Buy first home in Roseville  _(line 4,8: "looking to buy, first place")_
- **Value:** 400000  _(line 6: "I got pre-approved for four hundred")_
- **Currency:** _not in source_
- **Timeline:** _not in source_
- **Pipeline stage:** _requires human judgment_
- **Priority:** _requires human judgment_

## Tasks
- **Send Roseville listings under 400k**
  - title: Send Roseville listings under 400k  _(line 15: "send you a few listings in Roseville under four hundred to start")_
  - due: _not in source_
  - notes: _not in source_

## Notes
- **[objection]** First-time buyer, nervous about the whole process.  _(line 4: "first place, kind of nervous about the whole thing honestly")_
- **[financial]** Pre-approved for 400k, wants to stay a bit under to be safe.  _(line 6: "I got pre-approved for four hundred. Maybe a bit under to be safe.")_
- **[property]** Target area: Roseville, near where she works.  _(line 8: "Somewhere in Roseville ideally, near where I work.")_
- **[context]** Prefers to be contacted by text, does not check email.  _(line 12: "can you just text me? I never check email")_

## Not mapped to any field
- line 12: "can you just text me? I never check email" — Prospect asked to be contacted by text and said she never checks email, so contact.email stays not_in_source and this preference is recorded. Also captured as a context note; kept here to make explicit WHY the email field is empty rather than missed.

