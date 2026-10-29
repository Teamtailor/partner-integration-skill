# Documents and temporary file URLs

Separate three workflows:

1. **Existing candidate documents:** ask the Teamtailor team to enable document inclusion for your partner integration. Describe the use case and required categories: resume, uploaded documents, signed documents and offer PDFs as appropriate. Availability still depends on the candidate, permissions and enabled capabilities.
2. **A file uploaded in the send form:** a `type: "file"` control collects another document and supplies a URL in `webhook-data`.
3. **A result attachment:** your service returns a document URL as part of a partner result. This is a different direction of data transfer.

A custom `send_documents` checkbox only expresses a preference to your integration. It does not enable Teamtailor document inclusion. Structured job-offer data requires separate enablement and job context; enabling candidate documents alone does not imply that every offer record is included.

Relevant partner payload paths:

- `partner-event.candidate.resume`: a file object with `file-name` and `url`, when present.
- `partner-event.candidate.uploads`: an array of file objects with `file-name`, `url` and optional category metadata.
- `partner-event.candidate.questions`: file answers carry their URL in the question's `answer` value.
- `partner-event.webhook-data.<file-field-id>`: a send-form upload URL.

The [document payload fragment](../assets/examples/partner-documents.json) illustrates these optional paths. Treat each as potentially missing; do not assume enabling one supplies every category.

## Capture files promptly

URLs are temporary. Download the required bytes promptly on receipt, before slow destination calls or deferred processing, and queue a reference to your own access-controlled storage. Do not treat a signed URL as a durable file identifier or log its query string.

Checked implementation behavior:

| Source | Requested signing lifetime | Boundary |
|---|---|---|
| Candidate resume/uploads, including included offer PDFs | 60 seconds | Data may be absent without enablement or an available document |
| File-question answer | One hour | Separate from candidate-document inclusion |
| Matching unsigned form-upload URL in top-level partner `webhook-data` | 24 hours when signed during serialization | Already-signed and unrelated URLs pass through unchanged |

The public file-control documentation says 60 seconds, while the checked form-upload signing path requests 24 hours. **Do not schedule work around the longer value.** Requested expiry is not a promise that the file remains available until then. Do not extrapolate the partner form-upload rule to channel uploads or nested values.

On download failure, distinguish an expired/missing file from an integration processing error. There is no documented general renewal endpoint. Retrying the same expired URL does not renew it, and another serialization does not necessarily renew an already-signed link. Obtain a fresh upload or a new authorized delivery when necessary. If a document is optional, report its absence; if required, fail clearly before an incomplete destination write.

Bound download size/time, validate the permitted URL destinations and redirects for the integration, and handle unexpected content types. Use retention appropriate to the agreed workflow.

Public background: [partner webhooks and file fields](https://partner.teamtailor.com/partners/). See [known discrepancies](known-gaps.md).
