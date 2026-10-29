# Documentation corrections and boundaries

Reviewed 29 October 2026 against public documentation and implementation tests. This file records concrete differences; it does not establish deployment parity across every Teamtailor region. Validate enabled behavior in the integration's sandbox before launch.

| Topic | Correction / actionable boundary |
|---|---|
| Dependent response shape | Return a bare field array. The job-board page's description of the same structure as `/config` is misleading. |
| Dependent request context | Only the changed parent, configured query and locale are supplied automatically, not all current form answers. |
| Partner activation credentials | Dependent callbacks use saved credentials; unsaved sibling secrets are absent. |
| Channel activation dependencies | The checked activation UI has no dependent callback source. Use promotion configuration for interactive dependencies. |
| Dynamic channel activation attribute | Use `activation-config`, not the partner's `webhook-activation-config` shown in the channel example. |
| Candidate mapping metadata | The actual wire key is `mapped_from`, not the documentation's `mapped-from`. |
| Candidate boolean values | The checked custom-field serializer emits `"true"`/`"false"` strings with type `boolean`; do not use string truthiness. |
| Company placement | The checked partner webhook nests company under `partner-event.company`, unlike the top-level company in the public sample. |
| Field IDs across contexts | Webhook hash keys change underscores to hyphens; activation JWT and dependent-query keys preserve the original field ID. |
| Channel mapping | Supported for job fields, but underexplained publicly; payloads use flat entries with `mapped_as`, not candidate-style wrappers. |
| Mapping creation | Select/multiselect require nonempty string options. Existing-field compatibility is broader than creation support. |
| Strict select matching | Existing options may be a nonempty subset; matching does not translate submitted values. |
| Dynamic mapping save | Activation definitions may be requested again during mapping creation; preserve stable definitions and mappings then. |
| File-control lifetime | Public docs say 60 seconds; the checked partner form-upload path requests 24 hours for matching unsigned URLs. Download promptly; do not depend on that longer lifetime. |
| Token format | Ordinary customer-form JWT guidance is not universal for raw, empty, OAuth or hybrid activation modes. |
| Signature coverage | Both partner modes label digests `v1`; event-ID signatures do not cover other body fields. Some channel paths omit usable signatures. |
| Inline result subset | Summary, URL and other wider API attributes are ignored inline. Update through the Partner API. |
| Result ordering | A fast API completion can be overwritten by inline pending; early failed can become sent during delivery processing. Retain and reconcile the intended terminal result. |
| Job-board response | External IDs must be top-level; partial nested response handling can hide mistakes. Prefer documented HTTP 200, including removal. |
| Promotion IDs | An incoming promotion request ID is not the promotion resource ID needed for asynchronous API updates. |

Public documentation: [partners](https://partner.teamtailor.com/partners/), [job boards](https://partner.teamtailor.com/job_boards/). Detailed recipes live in this skill's references. These notes contain no customer data, private implementation paths or internal deployment instructions.
