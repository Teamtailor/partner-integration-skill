# Dependent fields

Use the singular property `dynamicField` on the controlling field. It loads additional field definitions on initial rendering and when the parent's value changes. The child can itself have `dynamicField` for another level of dependency.

```json
{
  "id": "department",
  "type": "select",
  "label": "Department",
  "required": true,
  "options": [{"id": "engineering", "label": "Engineering"}],
  "dynamicField": {
    "url": "https://integration.example/config/offices",
    "query": {"purpose": "employee-creation"}
  }
}
```

The endpoint receives a GET with the parent answer, configured query and locale, for example `?department=engineering&purpose=employee-creation&locale=en`. It does **not** automatically receive all other form answers. Avoid query keys that collide with the parent ID or locale. Keep secrets out of query parameters. If a dependency needs more context, use a tenant-scoped stable option ID and resolve its meaning on your server.

Return a **bare JSON array of field definitions**:

```json
[
  {
    "id": "office",
    "type": "select",
    "label": "Office",
    "required": true,
    "options": [{"id": "amsterdam", "label": "Amsterdam"}]
  }
]
```

Return `[]` when no children apply. A response such as `{"config":{"fields":[...]}}` or `{"fields":[...]}` is not accepted as the dependent-field array. The numbered channel `/config` envelope is also wrong here.

For an empty parent, return an empty array or a useful field-level explanation; do not fetch an unscoped list of another customer's resources. Validate parent and child membership again when processing the final webhook. Changing the form does not establish that an old child value is valid for a newly selected parent.

## URL and context rules

| Context | Dependent controls | URL |
|---|---|---|
| Partner send configuration | Supported | Relative to partner base URL, or absolute with the same scheme, host and port |
| Partner activation | Uses saved credentials; unsaved siblings are absent | Same partner URL restrictions |
| Channel promotion configuration | Supported | Absolute public URL |
| Channel activation | Not wired in the checked implementation | Use promotion controls instead |

Endpoints must be publicly reachable and pass URL safety checks; localhost/private-network destinations are unsuitable for Teamtailor requests. An absolute URL is not permission to forward credentials to arbitrary hosts: keep endpoints under the integration's control.

Children's answers remain flat: `{"department":"engineering","office":"amsterdam"}` in `webhook-data`. A group or dependency does not create a nested answer object.

See [activation constraints](activation.md), [authentication by endpoint](authentication-and-signatures.md) and [the documentation correction](known-gaps.md). Public background: [job-board configuration](https://partner.teamtailor.com/job_boards/#get-config).
