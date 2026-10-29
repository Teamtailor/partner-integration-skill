# Teamtailor integration skill

A portable agent skill for third-party developers building Teamtailor partner integrations and job boards. It covers the HTTP/data contracts and customer configuration while leaving language, framework, hosting and development workflow to the partner.

Start with the [Teamtailor partner portal](https://partner.teamtailor.com/) for onboarding and official API documentation. Read [SKILL.md](skills/teamtailor-integration/SKILL.md) for the guided workflow, or open the references directly.

## Use the skill

Download the `teamtailor-integration.zip` asset from the [latest release](https://github.com/Teamtailor/partner-integration-skill/releases/latest), or clone this repository. Copy the **entire** `skills/teamtailor-integration` directory into your agent's supported skill location. The copied directory must contain `SKILL.md`, `references/` and `assets/`; copying only the entrypoint loses the detailed contracts and examples.

For an agent without skill discovery, provide `SKILL.md` and make the referenced files available in the same relative layout. The Markdown references can also be read without an agent. Installation does not provision a Teamtailor integration or grant API access.

## Contents

- [Activation](skills/teamtailor-integration/references/activation.md): static versus dynamic definitions, credentials and validation.
- [Fields](skills/teamtailor-integration/references/fields.md) and [dependencies](skills/teamtailor-integration/references/dynamic-fields.md): controls, options, presentation and dependent requests.
- [Custom-field mapping](skills/teamtailor-integration/references/custom-field-mapping.md): purpose, creation, type support and delivered shapes.
- [Authentication/signatures](skills/teamtailor-integration/references/authentication-and-signatures.md) and [documents](skills/teamtailor-integration/references/documents.md).
- [Partner workflows](skills/teamtailor-integration/references/partners.md) and [job boards](skills/teamtailor-integration/references/job-boards.md), including XML feeds.
- [Known documentation gaps](skills/teamtailor-integration/references/known-gaps.md), [sandbox acceptance checklist](skills/teamtailor-integration/references/verification.md) and [synthetic examples](skills/teamtailor-integration/assets/examples/).

This is an independently maintained public package with its own history. It has no dependency on an internal adapter repository, SDK, hosting platform or private skill. All examples use synthetic data. Examples are intentionally reduced contract illustrations, not full API schemas.

## Validation and maintenance

Python 3.10+ is sufficient for the repository checks; the skill itself has no runtime dependency:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/package.py
```

The packager creates `dist/teamtailor-integration.zip` containing only the portable skill directory. CI runs the checks and builds the archive. Releases pin a reviewed version; link partners to a release when reproducibility matters.

See [validation scope](docs/validation.md) for what has actually been tested. Local checks do not replace end-to-end acceptance in a provisioned Teamtailor sandbox. Changes to contracts should update the relevant reference, example and regression check together. Report reproducible documentation discrepancies through [repository issues](https://github.com/Teamtailor/partner-integration-skill/issues) with synthetic/redacted examples.
