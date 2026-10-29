# Candidate/partner integrations

Use this contract for HRIS, assessments, onboarding and other candidate workflows. Preserve the partner's existing application architecture.

## Onboarding and endpoints

Apply through [Teamtailor's partner portal](https://partner.teamtailor.com/). An approved partner can use its sandbox and Integrations Hub to configure the integration, base URL, activation and marketplace information. Obtain the integration ID, Partner API key, configured signature mode/secret and required capabilities. Keep staging and production configuration separate.

- `GET /activation`: only when dynamic activation is configured; returns `{"config":{"fields":[]}}`, optionally with validation and mapping definitions.
- `GET /config`: returns per-send/trigger definitions as `{"config":{"fields":[]}}`. Tenant-specific department/office choices belong here after activation.
- `POST /webhook`: receives the partner event. Authenticate before performing destination actions.
- Additional validation and `dynamicField` endpoints: only as configured. A dependent endpoint returns an array, not the `/config` envelope.

See [activation](activation.md) and [fields](fields.md). A bulk/candidate-only workflow may omit job context; do not assume `job` is always present.

## Receiving an event

Read identity and data from `partner-event`: the event ID, `company`, `candidate`, `webhook-data` answers, and existing `partner-result` with its update URL. Optional job context is at `partner-event.candidate.job`, not a top-level job object. Use the authenticated activation to identify the destination tenant. Do not route a transfer using an unverified company label.

Use event ID plus tenant for delivery deduplication, and an appropriate destination business key for idempotent employee/application creation. Manual resubmission may be a new event; event-ID deduplication alone does not prevent duplicate employees. Persist enough state to resume work after a crash. Ordinary failed candidate webhook deliveries are not automatically retried; implement recovery for your own queued work and outbound API calls.

Validate mapped values and parent/child option combinations again on receipt. Capture required temporary [documents](documents.md) promptly. Return a successful acknowledgement only after accepting work durably or completing it. Do not return success for work you have discarded.

For a synchronous rejection, the public webhook contract uses HTTP 4xx/5xx with a plain text error message for recruiter display, for example HTTP 422, `Content-Type: text/plain`, and `Employment country is missing.` Do not reuse the activation validation error object automatically. For work already accepted, report processing failure through the existing partner result instead.

## Inline result versus later update

With partner results enabled, update the result Teamtailor already created. An HTTP 200 webhook response can include:

```json
{"partner_result_attributes": {"status": "pending"}}
```

The inline contract accepts `status`, `assessment.score`, `details`, `attachments` and `criteria`. API attributes such as `summary`, `url`, `label`, `actions`, assessment grade and duration are not automatically accepted inline. Use the Partner API for those fields.

For asynchronous completion, PUT the supplied, validated result update URL using the Partner API key and JSON:API headers. Example:

```json
{
  "data": {
    "type": "partner-results",
    "id": "result-example",
    "attributes": {"status": "completed", "summary": "Employee created"}
  }
}
```

Use the actual existing result ID in the URL and body. On failure use `failed` and a useful correction. Do not create a second result for the same trigger. `pending`, `completed` and `failed` cover the usual integration lifecycle; `sending` and `sent` are also platform statuses, not proof of destination completion.

### Result ordering

A very fast API update can race with processing the webhook response: `completed` can be overwritten by a later inline `pending`. The checked delivery path can also replace an early `failed` with `sent`. Returning the HTTP response and then starting a worker does not prove Teamtailor has persisted the response yet; an arbitrary sleep is not an ordering guarantee.

Persist the intended final result in your service. Read the existing result through the Partner API and reconcile/reapply its terminal update if delivery processing regresses it. Include bounded retries and an actionable failure state if reporting cannot complete. If work finishes synchronously, return the matching inline `completed` rather than a stale `pending`. For a synchronous rejection, use the non-success response described above. Test both rapid completion and failure in the sandbox.

Follow the documented maximum summary length of 150 and label length of 255. Result validation includes score 0–100, details nesting up to two levels, criteria nesting up to one level, and attachments with `url` and `description`. An accepted parser field can still fail model validation. Use the documented result schema for advanced assessment/actions behavior and test the actual response. Keep sensitive data out of recruiter-visible errors.

## Launch acceptance

Test in the provisioned sandbox with synthetic candidates and destination test accounts. Cover candidate-only and job-linked workflows, credential failure, absent mapped values, document enablement/expiry, inline pending then API completion, duplicate delivery and failure recovery. Teamtailor enablement and marketplace launch remain onboarding steps; hosting a webhook does not publish the integration automatically.

Public sources: [Partner API](https://partner.teamtailor.com/partners/), [partner onboarding](https://support.teamtailor.com/en/articles/5477200-integrate-your-hr-recruitment-tool-with-teamtailor).
