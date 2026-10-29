# Validation scope

Reviewed 29 October 2026. This package distinguishes contract examples, implementation checks and live integration acceptance.

## Executed checks

- Public-documentation-only exercises exposed incorrect dependent-response envelopes, candidate mapping metadata and channel activation attributes. The skill addresses these with separate partner/channel contracts.
- 189 local implementation checks passed: 172 existing examples plus 17 independent synthetic probes. They cover dependent requests, mapping creation/serialization, document inclusion, authentication formats, signatures, result parsing, status-ordering races, promotion responses and API routing. These used the application's test environment and mocked network calls.
- Two fresh-context developer exercises used the skill for an HRIS and a Java job board/XML importer. They correctly rejected the major contract mistakes. Their remaining questions led to explicit decoded credentials, document paths, error responses, ID serialization rules and result-ordering guidance. These are agent evaluations, not deployed integrations.
- 26 repository checks passed, covering JSON files and fenced JSON, the XML fragment, local links, example consistency, synthetic URL boundaries, selected private-data patterns, signature vectors and archive contents. The skill-format validator also passed. These are targeted regressions for this package, not a complete schema validator or a general secret scanner.
- Signature vectors were generated with Ruby OpenSSL and independently checked with Python's HMAC implementation. Cases include event-ID mode, raw JSON, UTF-8, bodyless requests, wrong keys, changed timestamps and body reserialization. The tests explicitly demonstrate the limited coverage of event-ID signatures.

## Limits

No live external integration, browser-based sandbox session or production delivery was exercised for this release. UI context restrictions were inspected in implementation; actual appearance and full customer setup must be accepted in the provisioned sandbox. Requested file-signing lifetimes are implementation observations, not availability guarantees.

Use the [sandbox checklist](../skills/teamtailor-integration/references/verification.md) for an actual partner deployment. Do not reuse synthetic IDs or keys as integration credentials. Known public-documentation differences are tracked in [known gaps](../skills/teamtailor-integration/references/known-gaps.md).
