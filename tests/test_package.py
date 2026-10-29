import hashlib
import hmac
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import urlparse
from zipfile import ZipFile
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "teamtailor-integration"
EXAMPLES = SKILL / "assets" / "examples"


def fixture(name):
    return json.loads((EXAMPLES / f"{name}.json").read_text())


def digest(vector, payload=None, key=None):
    value = vector["payload"] if payload is None else payload
    secret = vector["key"] if key is None else key
    message = f'{vector["timestamp"]}.{value}'.encode("utf-8")
    return hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()


class PackageChecks(unittest.TestCase):
    def test_frontmatter(self):
        source = (SKILL / "SKILL.md").read_text()
        self.assertTrue(source.startswith("---\nname: teamtailor-integration\n"))
        self.assertRegex(source, r"(?m)^description: .{30,}$")
        self.assertLess(len(source.splitlines()), 150)

    def test_json_files_and_markdown_json_are_valid(self):
        for path in EXAMPLES.glob("*.json"):
            with self.subTest(file=path.name):
                json.loads(path.read_text())
        for path in ROOT.rglob("*.md"):
            if ".git" in path.parts:
                continue
            for block in re.findall(r"```json\s*\n(.*?)\n```", path.read_text(), re.S):
                with self.subTest(file=str(path.relative_to(ROOT)), block=block[:40]):
                    json.loads(block)

    def test_relative_markdown_links_resolve_inside_repository(self):
        for path in ROOT.rglob("*.md"):
            if ".git" in path.parts:
                continue
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
                if target.startswith(("https://", "#")):
                    continue
                resolved = (path.parent / target.split("#")[0]).resolve()
                with self.subTest(file=path.name, target=target):
                    self.assertTrue(resolved.is_relative_to(ROOT))
                    self.assertTrue(resolved.exists())

    def test_xml_fragment_has_distinct_identity_and_application_url(self):
        source = (SKILL / "references" / "job-boards.md").read_text()
        fragments = re.findall(r"```xml\s*\n(.*?)\n```", source, re.S)
        self.assertEqual(len(fragments), 1)
        job = ElementTree.fromstring(fragments[0]).find("job")
        self.assertNotEqual(job.findtext("companyuuid"), job.findtext("referencenumber"))
        self.assertTrue(job.findtext("applyurl").endswith("/applications/new"))

    def test_portable_skill_has_no_private_paths_or_service_dependencies(self):
        forbidden = [r"/Users/", r"/home/", r"adapters-core", r"arn:aws:", r"AKIA[A-Z0-9]{16}", r"gh[pousr]_[A-Za-z0-9]{20,}", r"BEGIN .*PRIVATE KEY", r"https://github\.com/Teamtailor/(?:adapters|teamtailor)(?:/|\b)"]
        for path in SKILL.rglob("*"):
            if path.is_file():
                for pattern in forbidden:
                    with self.subTest(file=path.name, pattern=pattern):
                        self.assertIsNone(re.search(pattern, path.read_text()))

    def test_fixture_urls_are_synthetic_or_public_teamtailor_api(self):
        for path in EXAMPLES.glob("*.json"):
            for url in re.findall(r'https://[^"\s]+', path.read_text()):
                host = urlparse(url).hostname
                self.assertTrue(host.endswith(".example") or host == "api.teamtailor.com", (path.name, host))

    def test_archive_contains_only_complete_skill_and_is_reproducible(self):
        expected = {str(path.relative_to(SKILL.parent)) for path in SKILL.rglob("*") if path.is_file()}
        with tempfile.TemporaryDirectory() as directory:
            outputs = [Path(directory) / name for name in ("one.zip", "two.zip")]
            for output in outputs:
                subprocess.run([sys.executable, str(ROOT / "scripts" / "package.py"), "--output", str(output)], check=True, capture_output=True)
                with ZipFile(output) as archive:
                    self.assertEqual(set(archive.namelist()), expected)
                    for name in archive.namelist():
                        self.assertNotIn("..", Path(name).parts)
                        self.assertEqual(archive.read(name), (SKILL.parent / name).read_bytes())
            self.assertEqual(outputs[0].read_bytes(), outputs[1].read_bytes())


class ContractExamples(unittest.TestCase):
    def test_activation_envelopes(self):
        for kind in ("partner", "channel"):
            config = fixture(f"{kind}-activation")["config"]
            self.assertIsInstance(config["fields"], list)
            self.assertEqual(config["validateEndpoint"], "activation/validate")
            self.assertIsInstance(config["customFieldMapping"], list)

    def test_decoded_credentials_are_unwrapped_activation_ids(self):
        value = fixture("activation-credentials-decoded")
        self.assertEqual(set(value), {"api_token", "tenant_id"})
        self.assertNotIn("credentials", value)

    def test_static_channel_resource_embeds_activation_contract(self):
        attributes = fixture("channel-static-resource-update")["data"]["attributes"]
        self.assertFalse(attributes["dynamic-activation-config"])
        self.assertEqual(attributes["activation-config"], fixture("channel-activation"))

    def test_resource_attributes_are_not_interchangeable(self):
        partner = fixture("partner-resource-update")["data"]
        channel = fixture("channel-resource-update")["data"]
        self.assertEqual(partner["type"], "partners")
        self.assertIn("webhook-activation-config", partner["attributes"])
        self.assertNotIn("activation-config", partner["attributes"])
        self.assertEqual(channel["type"], "channels")
        self.assertIn("activation-config", channel["attributes"])
        self.assertNotIn("webhook-activation-config", channel["attributes"])
        self.assertTrue(channel["attributes"]["dynamic-activation-config"])

    def test_mapping_options_are_strings_not_form_options(self):
        for kind in ("partner", "channel"):
            mapping = fixture(f"{kind}-activation")["config"]["customFieldMapping"][0]
            self.assertTrue(mapping["options"])
            self.assertTrue(all(isinstance(value, str) for value in mapping["options"]))
            self.assertTrue(mapping["apiName"])

    def test_partner_and_channel_config_shapes_differ(self):
        self.assertIsInstance(fixture("partner-config")["config"]["fields"], list)
        channel = fixture("channel-config")["config"]
        self.assertEqual(next(iter(channel)), "1")
        self.assertIsInstance(channel["1"], list)
        self.assertEqual(channel["page"], "1")
        self.assertFalse(channel["hasNextPage"])
        self.assertNotIn("fields", channel)

    def test_dynamic_responses_are_bare_arrays(self):
        for kind in ("partner", "channel"):
            fields = fixture(f"{kind}-dynamic-fields")
            self.assertIsInstance(fields, list)
            self.assertTrue(fields)
            self.assertTrue(all("id" in field and "type" in field for field in fields))

    def test_dependent_values_match_options_and_remain_flat(self):
        for kind, parent_id, child_id in (("partner", "department", "office"), ("channel", "profession", "specialization")):
            config = fixture(f"{kind}-config")["config"]
            parent = config["fields" if kind == "partner" else "1"][0]
            child = fixture(f"{kind}-dynamic-fields")[0]
            payload = fixture("partner-webhook" if kind == "partner" else "promotion-webhook")
            answers = (payload["partner-event"] if kind == "partner" else payload)["webhook-data"]
            self.assertIn(answers[parent_id], [option["id"] for option in parent["options"]])
            self.assertIn(answers[child_id], [option["id"] for option in child["options"]])
            self.assertTrue(all(not isinstance(value, dict) for value in answers.values()))
            self.assertIn("dynamicField", parent)

    def test_candidate_mapping_uses_underscore_metadata_and_array_value(self):
        fields = fixture("partner-webhook")["partner-event"]["candidate"]["custom-fields"]
        mapped = next(field["employment-country"] for field in fields if "employment-country" in field)
        self.assertEqual(mapped["mapped_from"], "payroll-country")
        self.assertNotIn("mapped-from", mapped)
        self.assertEqual(mapped["value"], ["NL"])

    def test_partner_company_is_inside_event_and_promotion_job_has_no_invented_id(self):
        partner = fixture("partner-webhook")
        self.assertIn("company", partner["partner-event"])
        self.assertNotIn("company", partner)
        self.assertNotIn("job", partner["partner-event"])
        self.assertNotIn("id", fixture("promotion-webhook")["job"])

    def test_document_fragment_paths_match_form_id(self):
        event = fixture("partner-documents")["partner-event"]
        self.assertEqual(set(event["candidate"]["resume"]), {"file-name", "url"})
        self.assertIsInstance(event["candidate"]["uploads"], list)
        self.assertIsInstance(event["candidate"]["questions"][0]["answer"], str)
        field = next(field for field in fixture("partner-config")["config"]["fields"] if field["type"] == "file")
        self.assertIn(field["id"], event["webhook-data"])

    def test_channel_mapping_preserves_original_name(self):
        mapped = fixture("promotion-webhook")["job"]["custom-fields"][0]
        self.assertEqual(mapped["mapped_as"], "contract-type")
        self.assertEqual(mapped["mapped_from"], mapped["api_name"])
        self.assertNotEqual(mapped["api_name"], mapped["mapped_as"])
        self.assertNotIn("contract-type", mapped)

    def test_inline_result_uses_only_supported_subset(self):
        attributes = fixture("partner-result-inline")["partner_result_attributes"]
        self.assertLessEqual(set(attributes), {"status", "assessment", "details", "attachments", "criteria"})
        self.assertEqual(attributes["status"], "pending")

    def test_result_update_targets_existing_result(self):
        existing = fixture("partner-webhook")["partner-event"]["partner-result"]
        update = fixture("partner-result-update")["data"]
        self.assertEqual(update["id"], existing["id"])
        self.assertEqual(update["type"], "partner-results")
        self.assertTrue(existing["update-url"].endswith("/" + update["id"]))
        self.assertEqual(update["attributes"]["status"], "completed")
        self.assertLessEqual(len(update["attributes"]["summary"]), 150)

    def test_promotion_response_is_flat_and_ids_are_distinct(self):
        response = fixture("promotion-response")
        request = fixture("promotion-webhook")
        self.assertEqual(set(response), {"externalId", "externalUrl"})
        self.assertEqual(len({response["externalId"], request["id"], request["reference-id"]}), 3)


class SignatureVectors(unittest.TestCase):
    def test_ruby_openssl_vectors_match_python_hmac(self):
        for vector in fixture("signature-vectors"):
            with self.subTest(vector=vector["name"]):
                self.assertEqual(vector["signed_input"], vector["timestamp"] + "." + vector["payload"])
                self.assertTrue(hmac.compare_digest(digest(vector), vector["digest"]))
                self.assertEqual(vector["header"], f't={vector["timestamp"]},v1={vector["digest"]}')

    def test_wrong_keys_and_changed_signed_input_fail(self):
        for vector in fixture("signature-vectors"):
            self.assertNotEqual(digest(vector, key="incorrect-synthetic-key"), vector["digest"])
            self.assertNotEqual(digest(vector, payload=vector["payload"] + "x"), vector["digest"])
            changed = dict(vector, timestamp=str(int(vector["timestamp"]) + 1))
            self.assertNotEqual(digest(changed), vector["digest"])

    def test_body_reserialization_changes_digest(self):
        vector = next(item for item in fixture("signature-vectors") if item["name"] == "channel-raw-body-unicode")
        rewritten = json.dumps(json.loads(vector["payload"]), ensure_ascii=False)
        self.assertNotEqual(digest(vector, payload=rewritten), vector["digest"])

    def test_event_id_signature_does_not_authenticate_other_fields(self):
        vector = next(item for item in fixture("signature-vectors") if item["mode"] == "event-id")
        original = fixture("partner-webhook")
        altered = json.loads(json.dumps(original))
        altered["partner-event"]["candidate"]["email"] = "different@example.com"
        self.assertNotEqual(original, altered)
        self.assertEqual(digest(vector, payload=original["partner-event"]["id"]), digest(vector, payload=altered["partner-event"]["id"]))


if __name__ == "__main__":
    unittest.main()
