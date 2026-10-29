# Job boards

Choose the delivery model that fits the existing board. Webhook and XML integrations have different lifecycles; an XML importer does not require a webhook application. Agree supported edit/remove/refresh behavior during onboarding.

## Webhook board

Keep customer activation separate from job promotion configuration. Channel activation uses the `activation-config` attribute; read [activation](activation.md) for the dynamic-definition option and activation dependency limitation.

`GET /config` uses numbered page arrays:

```json
{
  "config": {
    "1": [
      {
        "id": "profession",
        "type": "select",
        "label": "Profession",
        "required": true,
        "options": [{"id": "engineering", "label": "Engineering"}],
        "dynamicField": {"url": "https://board.example/config/specializations"}
      }
    ],
    "hasNextPage": false,
    "page": "1"
  }
}
```

Put numbered page entries before metadata for compatibility with the checked config validator, whose traversal can stop at metadata. Preserve that order in your serializer when practical, and verify multipage behavior in the target sandbox; this is not a general JSON ordering rule. Do not replace page arrays with partner-style `fields`. A profession-dependent specialization endpoint returns a bare array as described in [dynamic fields](dynamic-fields.md). For job custom fields use [channel mapping](custom-field-mapping.md), not candidate serialization.

## Posting lifecycle and IDs

| Request | Meaning | Key detail |
|---|---|---|
| `POST /webhook` | Create an ad | Return your external ad ID |
| `PUT /webhook` | Update an ad | Use the supplied `externalId` query value to identify your ad |
| `DELETE /webhook/:reference_id` | Remove an ad | Teamtailor reference in path; external ad ID in `externalId` query |

Distinguish the incoming request/event `id`, Teamtailor's `reference-id`, your `externalId`, the integration ID and job-board ID. They are not interchangeable. Config requests can use `external_id`; webhook queries use `externalId`.

On create/update return HTTP 200 and **top-level** values:

```json
{"externalId": "ad-example", "externalUrl": "https://board.example/jobs/ad-example"}
```

Do not wrap these in `body`, `data` or another object: a wrapped response can lose the external ID even if another part of the response appears successful. Persist the Teamtailor-reference-to-ad association before acknowledging. Return HTTP 200 for successful removal too; do not substitute 204, which is not consistently recorded as success in the checked implementation. Make repeated removal safe. The platform has a retry path for failed removals; this does not imply the same policy for partner candidate deliveries.

Return meaningful non-success errors for rejected requests. Validate required job data and mapped values before posting. Verify the exact [authentication and body-signature contract](authentication-and-signatures.md) for enabled paths, including optional pause/resume behavior.

For example, return HTTP 422 with `Content-Type: application/json`:

```json
{"errors": ["Select a specialization belonging to the selected profession."]}
```

Do not invent an asynchronous protocol by returning an undocumented status and assuming Teamtailor will discover the result later. If asynchronous promotion reporting is required, agree it with Teamtailor. The Channel API has a promotion update resource, but its promotion ID is not necessarily the incoming request ID or `reference-id`; establish how the integration obtains the correct resource ID before implementing updates.

Once the actual promotion resource ID is known, the public API documents `PUT /channel/v1/promotions/{promotion-resource-id}` to update the external URL, using the channel API key and JSON:API headers:

```json
{
  "data": {
    "type": "promotions",
    "id": "promotion-resource-example",
    "attributes": {"external-url": "https://board.example/jobs/ad-example"}
  }
}
```

This documented URL update is not an asynchronous status protocol. Use the agreed regional API host, not the localhost host shown in some documentation examples.

## XML feed

Keep the board's existing feed importer. Ask Teamtailor for the assigned feed URL and mode:

- **Always included:** eligible jobs from activated customers.
- **Premium:** the selected promotions.

Use `referencenumber` for ad identity and `companyuuid` for customer association. Reconcile against a complete successfully retrieved feed; only then remove ads absent from that snapshot. A failed or partial download is not an empty feed. The generic public cadence is three times daily; confirm the assigned feed's schedule instead of promising real-time delivery.

Check the XML schema independently of JSON webhook examples. Use the provided application URL unless a separate Direct Apply contract is requested. Agree customer account linkage and any premium-specific metadata during onboarding. No `/config`, create/update/delete receiver, or candidate-result handler is required merely to import an XML feed.

Minimal identity/application fragment, omitting other feed fields:

```xml
<source>
  <job>
    <companyuuid>company-example</companyuuid>
    <referencenumber>teamtailor-example</referencenumber>
    <title>Example engineer</title>
    <url>https://careers.example/jobs/example-engineer</url>
    <applyurl>https://careers.example/jobs/example-engineer/applications/new</applyurl>
  </job>
</source>
```

Public sources: [job-board contracts](https://partner.teamtailor.com/job_boards/), [job-board onboarding](https://support.teamtailor.com/en/articles/7883983-integrate-your-job-board-with-teamtailor).
