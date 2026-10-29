# Activation configuration

Activation is the customer administrator's connection/setup form. Credentials belong here; job-specific choices normally belong in the later promotion/send form.

## Static or dynamic

Use **static activation** when every customer sees the same definitions, even though each enters different credentials. Use **dynamic activation** when the field definitions must be generated when setup opens, for example from an already-known company context. It calls `GET /activation` with company context and expects the same response envelope as static configuration.

Both use:

```json
{
  "config": {
    "fields": [
      {"id": "api_token", "type": "password", "label": "API token", "required": true}
    ],
    "validateEndpoint": "activation/validate",
    "customFieldMapping": [
      {"name": "Employment country", "type": "select", "apiName": "employment-country", "options": ["NL", "SE"], "strict": true}
    ]
  }
}
```

`fields` describes the form. `customFieldMapping` is its sibling inside `config`; it is not a form control. `validateEndpoint` also belongs inside `config`. Omit optional capabilities you do not need.

Use PUT to update the integration resource. Attributes differ:

- Partner: `/partner/v1/partners/{integration-id}` uses `webhook-activation-config`.
- Job board/channel: `/channel/v1/channels/{integration-id}` uses `activation-config`.

See the complete [static channel update](../assets/examples/channel-static-resource-update.json) and [static partner update](../assets/examples/partner-resource-update.json). API keys and headers are described in [authentication](authentication-and-signatures.md).

For a dynamic definition set `dynamic-activation-config` to `true` on the corresponding resource. The channel resource still uses `activation-config`; do not copy the partner attribute into a channel update. The integration ID is distinct from the job-board identifier used in promotion payloads. Configure through Integrations Hub or the corresponding API as available for your sandbox.

When the customer chooses to create mapped fields, Teamtailor can request dynamic activation definitions again while saving. Keep `config.fields` and the matching `config.customFieldMapping` available with stable `apiName`, type and options. Do not return the definitions only on the first visit. Initial and save-time requests need not carry identical context or credentials.

## Validate credentials

A configured relative `validateEndpoint` receives a GET after activation credentials have been saved. Validate the customer's credentials against your service. Return HTTP 200 when valid, or a 4xx response with useful errors, for example:

```json
{"errors": ["The API token is invalid or does not have permission to create employees."]}
```

Treat credential changes as untrusted input. Verify the configured activation authentication before using the credentials. Do not log secrets or put them in labels, dependent-field URLs, or query parameters. Password presentation masks a field; it does not remove the need for secure credential storage in your service.

## Dependent choices during setup

Generating `/activation` and loading dependent controls are different operations. See [dynamic fields](dynamic-fields.md).

- **Partner activation:** a dependent request uses the saved activation credentials. It includes the changed parent value and explicitly configured query parameters, not every unsaved sibling answer. A token just typed into another field is not automatically available. Prefer tenant-authenticated choices after credentials are saved/validated, or in the later partner `/config`.
- **Channel activation:** dependent-field callbacks are not wired in the checked implementation. Use static setup fields or a dynamically generated activation definition. Put interactive dependent choices in promotion `/config`.
- **First setup:** do not require newly entered credentials to already exist when serving the initial activation definition.

See [authentication](authentication-and-signatures.md) for JWT and other activation modes. Public documentation: [partner activation](https://partner.teamtailor.com/partners/#webhook-activation-config), [job-board activation](https://partner.teamtailor.com/job_boards/#webhook-activation-config).
