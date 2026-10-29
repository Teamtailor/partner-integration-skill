# Authentication and signatures

Keep customer credentials, integration API keys, company Public API tokens and webhook signing secrets separate. Configure authentication for each enabled endpoint and activation mode; one recipe does not cover every request.

## Credentials

| Credential | Direction and purpose |
|---|---|
| Customer activation credentials | Teamtailor sends the saved customer connection settings to the integration |
| Partner API key | Integration authenticates to the Partner API; also verifies ordinary customer-form activation JWTs |
| Job-board API key | Integration authenticates to the Channel API; verifies ordinary customer-form JWTs and regular channel webhook signatures |
| Partner webhook signing secret | Verifies configured partner webhook signatures; not the customer's API token |
| `Teamtailor-Api-Token` | Optional, separately enabled company Public API access; not a Partner/Channel API credential |

For the ordinary customer form flow, verify the Bearer JWT with HS256 and the corresponding integration API key before reading its credential object. Pin the algorithm; decoding is not verification. Do not require claims such as expiration or audience unless the agreed sender supplies them.

The decoded ordinary credential object contains the activation field IDs directly, without a `credentials` wrapper. For fields `api_token` and `tenant_id`, a synthetic example is:

```json
{"api_token": "synthetic-customer-token", "tenant_id": "tenant-example"}
```

Underscores in these activation keys remain unchanged. This is the verified JWT payload, not the literal Authorization header and not a webhook body.

Other activation modes differ: an empty partner activation can supply a random identifier, a sole `default_key` can be a raw credential, and OAuth has a separate contract. A channel with an empty ordinary form and an API key can still supply a JWT. Raw/non-form channel tokens can follow a different wrapping/signing path; they are not necessarily JWTs you can verify using the channel API key. Agree the authentication contract for that mode with Teamtailor instead of disabling verification or assuming every Bearer value has the same format.

Initial activation cannot depend on credentials the customer has not saved. For dependent callbacks, see [activation](activation.md). Protect endpoints according to their actual configured authentication, including those without a webhook signature.

For the ordinary customer-form mode, the checked request paths are:

| Request | Authorization context | Signature when configured |
|---|---|---|
| Partner `/activation`, `/config`, validation GET | Saved activation token; first setup may lack credentials | Empty-body signature with partner webhook secret |
| Partner dependent GET | Saved activation token, not unsaved siblings | Empty-body signature with partner webhook secret |
| Partner webhook POST | Saved activation token | Configured event-ID or body mode |
| Channel `/activation` and validation GET | Stored activation token; first setup may lack credentials | Empty-body signature with channel API key |
| Channel `/config` GET | Customer activation authorization | Empty-body signature with channel API key |
| Channel dependent GET | Customer activation authorization | May be absent before a promotion exists |
| Channel regular create/update and DELETE | Customer activation authorization | Raw body for create/update; empty body for DELETE |
| Channel pause/resume | Customer activation authorization | Omitted in the checked path |

This table does not redefine OAuth/raw-token modes. For first setup, verify the configured integration-level signature where available without demanding a nonexistent customer token. Agree any other bootstrap authentication with Teamtailor. An empty-body signature does not bind the path or query parameters; validate tenant ownership and referenced resources independently.

## Signature calculation

Parse `Teamtailor-Signature` by named components. Read its timestamp `t` and the supported digest `v1`; ignore unrelated version components rather than treating them as a fallback. Reject missing, malformed or ambiguous required components. Compare the computed hexadecimal digest in constant time. Use a bounded timestamp tolerance appropriate to your system, for example five minutes; that is a local verification policy, not a Teamtailor delivery guarantee.

The signed bytes are UTF-8 timestamp, a literal period, then the mode-specific payload:

| Configured request | Payload after the period | HMAC-SHA256 key |
|---|---|---|
| Partner event-ID signature mode | Exact `partner-event.id` | Partner webhook signing secret |
| Partner body signature mode | Exact raw request body bytes | Partner webhook signing secret |
| Regular job-board create/update webhook | Exact raw request body bytes | Job-board API key |
| Signed bodyless GET or DELETE | Empty bytes | The key configured for that integration/request |

Both partner modes use the `v1` digest label. **The header label does not choose the signing algorithm.** Confirm the provisioned partner mode; use event-ID mode when that is the configured contract. Do not propose switching modes without confirming sender support, and do not try alternative algorithms after verification fails.

Preserve raw body bytes before parsing JSON for body-signed requests. Reserializing JSON changes whitespace/order and can invalidate the digest. In event-ID mode, changing another JSON field leaves the digest unchanged: this signature authenticates the event ID and timestamp, not the entire body. Apply the configured activation authentication and HTTPS separately.

The checked channel implementation does not supply a usable signature on every path: a dependent-field request before the promotion exists can lack one, and pause/resume requests omit it. Do not apply an unconditional signed-request requirement to every route, or make signatures globally optional to work around those cases. Agree authentication for the specific enabled paths and test them in the sandbox.

The [signature vectors](../assets/examples/signature-vectors.json) contain synthetic keys, exact signed input and expected digests for interoperable verification. They are test data, not usable credentials. The package tests compare them with standard cryptographic implementations and check tampering boundaries.

## Outbound API calls

Use the integration's API key for its own API. A conventional authorization header is `Authorization: Token token="<integration-api-key>"`. Send `Content-Type: application/vnd.api+json` and the documented `X-Api-Version: 20180828` when calling these APIs. Keep company Public API permissions and version requirements separate.

Use the correct regional Teamtailor host supplied for the integration. Before forwarding credentials to a payload-provided update URL or a `Teamtailor-Host`, validate HTTPS and an allowlist of the agreed Teamtailor API hosts. Never forward a credential to an arbitrary URL solely because it appears in a payload.

Public references: [partner signatures](https://partner.teamtailor.com/partners/#webhook-signatures), [job-board signatures](https://partner.teamtailor.com/job_boards/#webhook-signatures), [company Public API](https://docs.teamtailor.com/).
