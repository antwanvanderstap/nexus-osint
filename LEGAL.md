# Legal Guidance for Operators

This document is informational only and does not constitute legal advice.
Consult a qualified attorney for advice specific to your jurisdiction and use case.

---

## What Nexus OSINT Is

Nexus OSINT is a self-hosted research tool that aggregates publicly available information
from open data sources. It is designed to assist with investigative research, due diligence,
and fraud prevention.

## What Nexus OSINT Is Not

Nexus OSINT is **not** a consumer reporting agency. It does not produce consumer reports
as defined by the Fair Credit Reporting Act (FCRA) or equivalent legislation in other jurisdictions.

---

## United States: FCRA

The **Fair Credit Reporting Act (15 U.S.C. § 1681)** regulates "consumer reports" — any
written, oral, or other communication of information bearing on a consumer's creditworthiness,
credit standing, credit capacity, character, general reputation, personal characteristics,
or mode of living — when used for:

- Employment decisions
- Housing / tenant screening
- Credit or insurance underwriting
- Any other "permissible purpose" under § 1681b

**If you use this tool to inform any of the above decisions, you may be operating as a
Consumer Reporting Agency and subject to FCRA obligations**, including furnisher requirements,
adverse action notices, and dispute rights.

### Safe Uses Under FCRA
- General research with no adverse decision outcome
- Fraud investigation where no FCRA permissible purpose is triggered
- Journalism and public interest research
- Internal security investigations (not affecting consumer rights)

---

## United States: CFAA

The **Computer Fraud and Abuse Act** prohibits unauthorized access to computer systems.
Per *hiQ Labs v. LinkedIn* (9th Cir. 2022), automated access to **publicly available** data
(no login required) likely does not constitute unauthorized access under the CFAA.

However, platform Terms of Service violations remain a civil matter separate from CFAA.

---

## European Union: GDPR

If you process personal data of EU residents, the **General Data Protection Regulation**
(Regulation 2016/679) applies. Key obligations:

- Identify a lawful basis for processing (Article 6)
- Respect data subject rights (access, erasure, portability)
- Implement appropriate technical safeguards
- Maintain records of processing activities

Legitimate interest (Article 6(1)(f)) may apply for fraud prevention and security research,
but requires a balancing test against data subject rights.

---

## Terms of Service Considerations

Every data source has its own Terms of Service. Nexus OSINT modules carry a `tos_risk`
rating to help operators understand the landscape:

| Risk Level | Meaning |
|---|---|
| `none` | Official API or public domain data — no T&S concerns |
| `low` | Existence checks only; no content extraction |
| `medium` | Public data accessed programmatically; gray area |
| `high` | Likely T&S violation; operator assumes full risk |

Operators are solely responsible for ensuring their use of each module complies with
the Terms of Service of the underlying data source.

---

## Operator Checklist

Before deploying Nexus OSINT for business use:

- [ ] Identify your primary use cases and confirm they are not FCRA-regulated
- [ ] Review T&S for any `medium` or `high` risk modules you intend to enable
- [ ] Implement a data retention policy (configure `AUDIT_LOG_RETENTION_DAYS`)
- [ ] Train users on permissible purposes before granting access
- [ ] Consult legal counsel if tenant screening or employment decisions are involved
- [ ] If operating in the EU, conduct a GDPR legitimate interest assessment

---

## Reporting Legal Concerns

If you believe a module raises legal concerns not addressed here, please open an issue
with the `legal` label. The community takes compliance seriously.
