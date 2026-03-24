"""Validate the structural integrity of all skills."""

import json
import re
import unittest
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent / "skills"

SKILLS = {
    "models": {
        "reference_dir": "reference",
        "references": [
            "experiments.md",
            "artifacts.md",
            "registry.md",
            "sweeps.md",
            "api-patterns.md",
            "leaderboard.md",
            "integrations.md",
            "table-examples.md",
            "troubleshooting.md",
        ],
        "keyword": "wandb",
    },
    "weave": {
        "reference_dir": "references",
        "references": [
            "tracing.md",
            "evaluation.md",
            "scorers.md",
            "datasets.md",
            "prompts.md",
            "monitors-guardrails.md",
            "feedback.md",
            "costs.md",
            "integrations.md",
            "troubleshooting.md",
        ],
        "keyword": "weave",
    },
    "weave-integration": {
        "reference_dir": "references",
        "references": [
            "codebase-analysis.md",
            "tracing-integration.md",
            "model-conversion.md",
            "evaluation-integration.md",
            "prompt-versioning.md",
            "framework-specific.md",
            "integration-checklist.md",
        ],
        "keyword": "weave",
    },
}


class TestSkillStructure(unittest.TestCase):
    """Test that each skill has the required files and valid format."""

    def test_skill_directories_exist(self):
        for skill_name in SKILLS:
            skill_dir = SKILLS_DIR / skill_name
            self.assertTrue(skill_dir.is_dir(), f"Skill directory missing: {skill_dir}")

    def test_skill_md_exists(self):
        for skill_name in SKILLS:
            skill_md = SKILLS_DIR / skill_name / "SKILL.md"
            self.assertTrue(skill_md.is_file(), f"SKILL.md missing: {skill_md}")

    def test_skill_md_has_yaml_front_matter(self):
        for skill_name in SKILLS:
            skill_md = SKILLS_DIR / skill_name / "SKILL.md"
            content = skill_md.read_text()
            self.assertTrue(
                content.startswith("---"),
                f"{skill_name}/SKILL.md must start with YAML front matter (---)",
            )
            # Check closing ---
            parts = content.split("---", 2)
            self.assertGreaterEqual(
                len(parts), 3, f"{skill_name}/SKILL.md must have closing --- for YAML front matter"
            )

    def test_skill_md_has_name_field(self):
        for skill_name in SKILLS:
            skill_md = SKILLS_DIR / skill_name / "SKILL.md"
            content = skill_md.read_text()
            front_matter = content.split("---", 2)[1]
            self.assertIn(
                "name:", front_matter, f"{skill_name}/SKILL.md YAML must contain 'name:' field"
            )

    def test_skill_md_has_description_field(self):
        for skill_name in SKILLS:
            skill_md = SKILLS_DIR / skill_name / "SKILL.md"
            content = skill_md.read_text()
            front_matter = content.split("---", 2)[1]
            self.assertIn(
                "description:",
                front_matter,
                f"{skill_name}/SKILL.md YAML must contain 'description:' field",
            )

    def test_reference_files_exist(self):
        for skill_name, config in SKILLS.items():
            ref_dir = config["reference_dir"]
            for ref_file in config["references"]:
                ref_path = SKILLS_DIR / skill_name / ref_dir / ref_file
                self.assertTrue(ref_path.is_file(), f"Reference file missing: {ref_path}")

    def test_evals_json_exists(self):
        for skill_name in SKILLS:
            evals_path = SKILLS_DIR / skill_name / "evals" / "evals.json"
            self.assertTrue(evals_path.is_file(), f"evals.json missing: {evals_path}")

    def test_evals_json_valid_format(self):
        for skill_name in SKILLS:
            evals_path = SKILLS_DIR / skill_name / "evals" / "evals.json"
            with open(evals_path) as f:
                data = json.load(f)

            self.assertIsInstance(data, list, f"{skill_name}/evals.json must be a JSON array")
            self.assertGreater(len(data), 0, f"{skill_name}/evals.json must not be empty")

            for i, entry in enumerate(data):
                self.assertIn(
                    "query", entry, f"{skill_name}/evals.json entry {i} missing 'query'"
                )
                self.assertIn(
                    "should_trigger",
                    entry,
                    f"{skill_name}/evals.json entry {i} missing 'should_trigger'",
                )
                self.assertIsInstance(entry["query"], str)
                self.assertIsInstance(entry["should_trigger"], bool)

                if entry["should_trigger"]:
                    self.assertIn(
                        "expected",
                        entry,
                        f"{skill_name}/evals.json entry {i}: should_trigger=true but missing 'expected'",
                    )
                    self.assertIsInstance(entry["expected"], list)

    def test_evals_has_positive_and_negative_cases(self):
        for skill_name in SKILLS:
            evals_path = SKILLS_DIR / skill_name / "evals" / "evals.json"
            with open(evals_path) as f:
                data = json.load(f)

            positive = [e for e in data if e["should_trigger"]]
            negative = [e for e in data if not e["should_trigger"]]

            self.assertGreater(
                len(positive), 0, f"{skill_name}/evals.json must have positive cases"
            )
            self.assertGreater(
                len(negative), 0, f"{skill_name}/evals.json must have negative cases"
            )

    def test_reference_files_contain_code_blocks(self):
        """Reference files should contain Python code examples (except checklists)."""
        # Checklist files use markdown checkboxes, not code blocks
        exceptions = {"integration-checklist.md"}

        for skill_name, config in SKILLS.items():
            ref_dir = config["reference_dir"]
            for ref_file in config["references"]:
                if ref_file in exceptions:
                    continue
                ref_path = SKILLS_DIR / skill_name / ref_dir / ref_file
                content = ref_path.read_text()
                has_code = "```python" in content or "```bash" in content or "```" in content
                self.assertTrue(
                    has_code,
                    f"{skill_name}/{ref_dir}/{ref_file} should contain code blocks",
                )

    def test_reference_files_mention_product_keyword(self):
        """Reference files should mention their product keyword (wandb or weave)."""
        for skill_name, config in SKILLS.items():
            ref_dir = config["reference_dir"]
            keyword = config["keyword"]
            for ref_file in config["references"]:
                ref_path = SKILLS_DIR / skill_name / ref_dir / ref_file
                content = ref_path.read_text().lower()
                self.assertIn(
                    keyword,
                    content,
                    f"{skill_name}/{ref_dir}/{ref_file} should mention '{keyword}'",
                )

    def test_bilingual_triggers(self):
        """SKILL.md description should contain both English and Korean triggers."""
        for skill_name in SKILLS:
            skill_md = SKILLS_DIR / skill_name / "SKILL.md"
            content = skill_md.read_text()
            front_matter = content.split("---", 2)[1]

            # Check for Korean characters in description
            has_korean = bool(re.search(r"[\uac00-\ud7af]", front_matter))
            self.assertTrue(
                has_korean,
                f"{skill_name}/SKILL.md description should contain Korean trigger keywords",
            )

            # Check for English keywords
            has_english = bool(re.search(r"[a-zA-Z]{4,}", front_matter))
            self.assertTrue(
                has_english,
                f"{skill_name}/SKILL.md description should contain English trigger keywords",
            )


if __name__ == "__main__":
    unittest.main()
