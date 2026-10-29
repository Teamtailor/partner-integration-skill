# Custom-field mapping

Mapping connects a stable destination name, such as `employment-country`, to a customer's stored Teamtailor field, such as `payroll-country`. During activation the customer can select an eligible existing field or create a supported one. It prevents the integration from hardcoding a customer's display label or custom-field ID.

It does **not** collect the candidate's value, fill empty records, backfill historical records or convert the customer's option labels to destination codes. A send-time dropdown is a separate form answer. Configure explicit value translation if your destination requires it.

Add declarations to `config.customFieldMapping` in activation configuration:

```json
{
  "name": "Employment country",
  "apiName": "employment-country",
  "type": "select",
  "options": ["NL", "SE"],
  "strict": true
}
```

`name` is the setup label; `apiName` is the integration's stable name; `type` is the expected stored-field kind. Mapping can be configured for candidate fields in partner integrations and job fields in channel integrations. A field created in the wrong record type will not supply the intended data.

For dynamic activation, return the same mapping definitions when Teamtailor requests them again during field creation/save. A declaration that exists only during initial rendering cannot reliably create the mapped field.

## Creation and matching

| Declaration type | Creation support | Important behavior |
|---|---|---|
| `text`, `number`, `date`, `url`, `phone` | Supported | Validate the destination's required value and format |
| `checkbox` | Supported | Serialized custom-field type is `boolean` |
| `select`, `multiselect` | Supported with nonempty `options` | Mapping options are strings, e.g. `["NL","SE"]`, not form `{id,label}` objects |
| `email` | Existing-field mapping only | Not supported by the checked field-creation path |
| Other types | Not supported for creation | Do not promise a field will be created |

`strict: true` restricts compatibility for a single-select mapping with declared options. The existing field must have a nonempty subset of the allowed options; comparison trims whitespace and ignores case. It does not require both option sets to be identical. It does not rewrite the submitted values. Do not generalize it to every mapping type or rely on it as destination-side validation.

## Candidate payload

`partner-event.candidate.custom-fields` is an array of single-key objects:

```json
[
  {
    "employment-country": {
      "value": ["NL"],
      "type": "select",
      "mapped_from": "payroll-country"
    }
  }
]
```

Locate the object by the integration key; do not assume its array position. The metadata key is **`mapped_from`**, with an underscore. Unmapped fields retain their Teamtailor key. Unfilled values can be absent. Select and multiselect custom-field values are arrays, unlike a form `select` answer, which is a scalar option ID.

A candidate checkbox custom field has type `boolean` but its value is the string `"true"` or `"false"` in the checked serializer. Normalize those exact values explicitly: a nonempty `"false"` string is truthy in many languages. This differs from form checkbox answers and job custom-field boolean values, which are booleans.

## Job-board payload

`job.custom-fields` uses flat entries instead:

```json
[
  {
    "id": 42,
    "name": "Contract arrangement",
    "api_name": "contract-arrangement",
    "type": "select",
    "value": ["Permanent"],
    "mapped_as": "contract-type",
    "mapped_from": "contract-arrangement"
  }
]
```

Find `mapped_as == "contract-type"`. `api_name` remains the original Teamtailor name. Do not look for the candidate-style single-key object or overwrite `api_name` in your model of the incoming payload.

For a required single choice, reject missing, empty, multiple or unsupported values with an actionable message. If `Permanent` must become `PERM`, apply an explicit customer-agreed translation; mapping alone does not perform it.

Public background: [partner mapping](https://partner.teamtailor.com/partners/#custom-field-mapping), [Teamtailor custom fields](https://support.teamtailor.com/en/articles/3468522-custom-fields). See [documentation gaps](known-gaps.md) for the wire-key correction and channel mapping omission.
