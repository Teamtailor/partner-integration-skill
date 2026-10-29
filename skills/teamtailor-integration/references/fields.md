# Form controls and presentation

Choose controls by the customer's task. Explain where the control appears, whether its answer is a saved activation setting or send/promotion data, and the value sent to the integration. Form types, mapping declaration types and serialized custom-field types are separate contracts.

Use stable unique `id` values, a clear `label`, and `required` when a value is necessary. Existing saved answers normally take precedence over a definition's default `value`; `useValue: true` explicitly asks to use the new definition value. Avoid overriding a recruiter's answer accidentally.

Prefer hyphenated IDs for send/promotion fields. In both webhook formats, hash keys in `webhook-data` change underscores to hyphens: `employee_reference` becomes `employee-reference`. Activation JWT credential keys and dependent-request parent keys preserve the original field ID. Option values are not renamed. Do not apply this conversion indiscriminately to array-contained objects; custom-field metadata such as `mapped_from` keeps its underscore.

## Common inputs

| Type | Presentation | Submitted value / caveat |
|---|---|---|
| `text`, `email`, `tel`, `url`, `password` | Single-line input; password masked | String; validate on your server |
| `number` | Numeric input | Can be a string; parse and validate explicitly |
| `date` | Date control | ISO plain-date string `YYYY-MM-DD` |
| `checkbox` | Toggle/checkbox | Boolean |
| `select` | Searchable dropdown | One option ID, or empty/null when optional |
| `multiselect` | Multiple-choice dropdown | Array of option IDs |
| `radio` | Choice cards, optional descriptions | One selected option value |
| `textarea` | Multiline plain text | String |
| `textarea-html` | Rich text | HTML content; sanitize when displaying it |
| `file` | Upload control | Temporary URL, not file bytes; see [documents](documents.md) |

Options for a form dropdown use objects:

```json
{
  "id": "department",
  "type": "select",
  "label": "Department",
  "placeholder": "Choose a department",
  "required": true,
  "options": [
    {"id": "engineering", "label": "Engineering"},
    {"id": "people", "label": "People"}
  ]
}
```

Use consistent string IDs. Labels are for people; IDs are what your server receives. Mapping declarations use string options instead, as described in [mapping](custom-field-mapping.md).

For grouped dropdown choices, replace `options` with `optgroups`:

```json
{
  "id": "office",
  "type": "select",
  "label": "Office",
  "optgroups": [
    {"label": "Netherlands", "options": [{"id": "amsterdam", "label": "Amsterdam"}]},
    {"label": "Sweden", "options": [{"id": "stockholm", "label": "Stockholm"}]}
  ]
}
```

For visible choice cards with descriptions:

```json
{
  "id": "employment-schedule",
  "type": "radio",
  "label": "Employment schedule",
  "options": [
    {"id": "full_time", "label": "Full time", "description": "Standard weekly hours"},
    {"id": "part_time", "label": "Part time", "description": "Reduced weekly hours"}
  ]
}
```

Radio options can also be strings, but object options make stable IDs and human labels explicit.

## Layout and explanations

| Type | Purpose | Data effect |
|---|---|---|
| `group` | Visible heading with child `fields` | Child IDs stay flat |
| `expandable`, `advanced` | Collapsible optional details | Child IDs stay flat |
| `infobox` | Explanation using `content`; optional icon such as `info`, `warning`, `error`, `success` | No business answer |
| `error` | Blocking form error using `message` | Requires correction before proceeding |
| `link` | Help/navigation link | No business answer |

Example:

```json
{
  "type": "group",
  "label": "Employee placement",
  "fields": [
    {"id": "employee-reference", "type": "text", "label": "Employee reference"},
    {"type": "infobox", "icon": "info", "content": "Use the reference from your HR system."}
  ]
}
```

The answer is `{"employee-reference":"example-123"}`, not a nested group object. Test accessibility, labels, empty states and long option lists in the actual form.

## Specialized controls and limitations

The renderer also recognizes `description-editor`, `geolocation`, `select-image`, `spawnable`, and HTML-like primitive types including `color`, `datetime`, `datetime-local`, `hidden`, `month`, `range`, `reset`, `search` and `week`. Recognition does not establish identical behavior in every context or browser. Prefer the common controls above; validate a specialized control in its intended form before relying on it.

`description-editor` with `job_body` needs job promotion context; do not use that preset in a candidate-only form. Rich-text sanitization and styling differ by context. Do not promise arbitrary HTML/CSS rendering.

Primitive inputs expose properties such as `disabled`, `readonly`, `pattern`, `min`, `max`, `step` and `maxlength` where applicable. These are not universal properties: the select/multiselect components do not pass through `disabled`/`readonly`. UI validation is not a substitute for validating final webhook values.

For dependent options, use [dynamic fields](dynamic-fields.md). Public background: [partner config](https://partner.teamtailor.com/partners/#webhook-config), [job-board config](https://partner.teamtailor.com/job_boards/#get-config).
