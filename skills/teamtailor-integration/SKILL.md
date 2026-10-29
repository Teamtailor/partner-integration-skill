---
name: teamtailor-integration
description: Build, review, or troubleshoot a third-party Teamtailor partner integration or job board connection. Use for activation forms, custom-field mapping, dependent fields, webhook authentication, candidate documents, partner results, job promotions, or XML feeds.
---

# Teamtailor integration

Implement the Teamtailor contract in the partner's chosen language, architecture and hosting environment. Preserve the existing application and workflow. No particular framework, HTTP client, repository layout, cloud or deployment tool is required.

Start at the [Teamtailor partner portal](https://partner.teamtailor.com/). Identify the integration kind and the customer workflow before choosing endpoints:

- **Partner:** send candidates to an HRIS, assessment, onboarding or another service. Read [partners](references/partners.md).
- **Job board:** publish, update and remove jobs. Read [job boards](references/job-boards.md). An existing XML importer can consume a feed without implementing webhook endpoints.

Ask only for missing decisions that affect the contract: integration kind, desired customer actions, tenant authentication, destination-required data, and enabled capabilities. Use the supplied documentation and existing implementation to answer what is already known.

## Design the customer configuration

Keep three purposes distinct:

1. **Activation:** credentials and settings saved once per customer. Use static configuration unless the form definition itself must vary. Dynamic activation does not mean dependent dropdowns. Read [activation](references/activation.md).
2. **Custom-field mapping:** connect a destination field to a stored Teamtailor candidate/job field, or create an eligible field. Mapping does not fill missing data or translate option values. Read [mapping](references/custom-field-mapping.md).
3. **Send/promotion configuration:** choices made for a particular workflow, such as department, office or profession. Explain where each control appears and which value is delivered. Read [fields](references/fields.md).

Use `dynamicField` for dependent controls. Its endpoint returns a **bare array**, not a configuration envelope. Read [dynamic fields](references/dynamic-fields.md) before implementing dependencies, especially during activation.

## Implement and validate

Read [authentication and signatures](references/authentication-and-signatures.md) before handling credentials or webhook requests. Partner event signatures and job-board body signatures are different. Do not infer a token's format or an endpoint's signature requirement from another integration type.

Read [documents](references/documents.md) when files are involved. Request document inclusion from Teamtailor; a form toggle cannot enable it. Capture temporary files promptly before deferring processing.

Use the [synthetic examples](assets/examples/) as contract illustrations, not complete payload schemas. Preserve optional/unknown attributes, validate required destination data, handle absent job context, and make destination writes idempotent. Do not assume failed candidate webhook deliveries will retry automatically.

Test success and failure in the integration's Teamtailor sandbox: activation and credential rejection; dependent field changes; missing and incompatible mapped values; absent/expired files; duplicate delivery; asynchronous completion; and job update/removal where applicable. Local fixture checks do not establish that a customer sandbox is correctly configured. Follow the [verification checklist](references/verification.md).

Before delivering an implementation, report the configured capabilities, endpoint/response contracts, tests actually run and remaining integration-specific gaps. Consult [known documentation gaps](references/known-gaps.md) when a public example conflicts with these references. Those corrections describe checked implementation behavior, not a guarantee that every deployed stack has the same version.
