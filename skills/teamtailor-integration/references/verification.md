# Verification before launch

Run package checks when modifying this skill. Those checks validate examples and cryptographic vectors; they do not start a Teamtailor integration or prove an external service works.

For an integration, use the provisioned Teamtailor sandbox plus the destination's test environment and synthetic records. Record the actual request/response shape with credentials, signed URLs and personal data redacted.

1. **Activation:** open first setup without saved credentials; save valid and invalid credentials; verify the configured authentication mode; reopen settings. If dynamic definitions include mapping creation, ensure the declarations are still returned when saving.
2. **Controls:** test required/optional choices, empty lists and defaults; change the parent after choosing a child; verify the child belongs to the new parent; ensure answers remain flat. Check the actual supported context before using specialized controls.
3. **Mapping:** map an existing field; create each needed supported type; test missing values and incompatible options. Confirm `mapped_from` for candidates or `mapped_as` for job fields. Validate explicit enum translation separately.
4. **Security:** test known valid signatures, wrong keys, malformed headers, stale timestamps and changed signed input. For event-ID mode, explicitly recognize that unrelated body changes are outside signature coverage. Verify endpoint-specific authentication for unsigned channel paths.
5. **Documents:** test inclusion disabled, enabled with no document, successful immediate download and expired URL. Ensure a queued worker uses captured bytes, not an old temporary URL.
6. **Partner results:** accept durably, return inline pending, update the existing result via API, then test failure. Verify API-only attributes through the API rather than inline. Include candidate-only events without job data. Force API completion before returning inline pending, then read/reconcile the result; repeat with early failure to detect delivery status regression.
7. **Job board:** create, update and remove the same ad; verify the flat external ID response and all ID mappings. Repeat delivery/removal. If XML, test complete feed removal and failed/partial imports instead of webhook endpoints.
8. **Recovery:** crash after durable acceptance, retry destination work safely, and retry failed result reporting without creating duplicate business records.

State what was actually tested: local fixture checks, implementation tests, browser rendering, sandbox delivery, or production observation. Do not describe one level as another. When sandbox access or a configured feature is missing, identify that specific acceptance gap.

## Focused sandbox reproductions

Use disposable synthetic records and the integration's own test endpoints:

1. Return `partner-config.json` from the test partner's `/config` and `partner-dynamic-fields.json` from its office endpoint. Select Engineering. Expect a GET carrying `department=engineering` and an Office dropdown. Temporarily return a config envelope instead of the array; expect no dependent fields. Restore the valid response.
2. Map an existing candidate select field to `employment-country`, fill it with NL and trigger a send. Expect the mapped entry's value array and `mapped_from`. Repeat without a value and verify the integration's explicit validation error. For channels, inspect `mapped_as` on the flat job-field entry instead.
3. Open partner activation, change an unsaved sibling credential, and trigger a dependent choice. Compare the authenticated saved identity rather than logging credentials. Expect the previous saved identity; after validation/save, verify the new identity. Channel activation should not be used for this callback test.
4. Create a test ad and return flat `externalId`. Verify the next update/delete carries that value in its query. Repeat with a wrapped ID only on a disposable test promotion to reproduce the missing-ID problem; remove the test ad through the board's own cleanup flow if necessary.
5. In a controlled partner handler, update the result to completed via API before responding with inline pending. Read the result after delivery settles, observe any regression, and verify your reconciliation restores completed. Repeat with failed. Do not intentionally run this race against real candidates.
