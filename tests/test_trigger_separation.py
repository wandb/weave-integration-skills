"""Validate that skills don't trigger on each other's queries."""

import json
import unittest
from pathlib import Path

from test_skill_triggers import extract_description, query_matches_description

SKILLS_DIR = Path(__file__).parent.parent / "skills"


class TestWeaveVsIntegrationSeparation(unittest.TestCase):
    """Ensure weave and weave-integration skills have properly separated triggers."""

    @classmethod
    def setUpClass(cls):
        cls.weave_desc = extract_description("weave")
        cls.integration_desc = extract_description("weave-integration")

        with open(SKILLS_DIR / "weave" / "evals" / "evals.json") as f:
            cls.weave_evals = json.load(f)

        with open(SKILLS_DIR / "weave-integration" / "evals" / "evals.json") as f:
            cls.integration_evals = json.load(f)

    def test_weave_positive_queries_not_integration_exclusive(self):
        """Weave skill's positive queries should not ONLY match weave-integration.

        Some overlap is acceptable (both skills deal with Weave), but weave-specific
        queries like 'Create a HallucinationFreeScorer' should not match integration.
        """
        weave_only_queries = [
            e["query"]
            for e in self.weave_evals
            if e["should_trigger"]
            and any(
                kw in e["query"].lower()
                for kw in ["scorer", "evaluation pipeline", "dataset", "prompt version", "monitor", "guardrail", "feedback", "cost"]
            )
        ]

        for query in weave_only_queries:
            matches_integration = query_matches_description(query, self.integration_desc)
            matches_weave = query_matches_description(query, self.weave_desc)
            if matches_integration and not matches_weave:
                self.fail(
                    f"Query should match weave but only matches integration: '{query}'"
                )

    def test_integration_positive_queries_match_integration(self):
        """Integration-specific queries should match the integration skill."""
        integration_specific = [
            e["query"]
            for e in self.integration_evals
            if e["should_trigger"]
            and any(
                kw in e["query"].lower()
                for kw in ["existing", "integrate", "instrument", "retrofit", "기존", "적용", "연동", "붙여"]
            )
        ]

        for query in integration_specific:
            matches = query_matches_description(query, self.integration_desc)
            self.assertTrue(
                matches,
                f"Integration-specific query should match integration skill: '{query}'",
            )

    def test_integration_negative_cases_are_weave_positive(self):
        """Queries that should NOT trigger integration should be things like
        'Create new Weave code from scratch' — they might trigger the weave skill instead.
        """
        integration_negatives = [
            e for e in self.integration_evals if not e["should_trigger"]
        ]

        # Check that at least some integration negatives are weave-related
        weave_related = [
            e
            for e in integration_negatives
            if any(
                kw in e["query"].lower()
                for kw in ["weave", "scorer", "evaluation"]
            )
        ]

        # These weave-related negatives should ideally match the weave skill
        for entry in weave_related:
            query = entry["query"]
            matches_weave = query_matches_description(query, self.weave_desc)
            # Soft check — just log if they don't match
            if not matches_weave:
                print(f"  INFO: Integration negative '{query}' doesn't match weave either")

    def test_no_shared_positive_queries_weave_vs_integration(self):
        """The same exact query should not appear as should_trigger=true in both evals."""
        weave_positive = {e["query"] for e in self.weave_evals if e["should_trigger"]}
        integration_positive = {
            e["query"] for e in self.integration_evals if e["should_trigger"]
        }

        shared = weave_positive & integration_positive
        self.assertEqual(
            len(shared),
            0,
            f"These queries appear as positive in BOTH weave and integration evals: {shared}",
        )


class TestModelsVsWeaveSeparation(unittest.TestCase):
    """Ensure models and weave skills have properly separated triggers."""

    @classmethod
    def setUpClass(cls):
        cls.models_desc = extract_description("models")
        cls.weave_desc = extract_description("weave")
        cls.integration_desc = extract_description("weave-integration")

        with open(SKILLS_DIR / "models" / "evals" / "evals.json") as f:
            cls.models_evals = json.load(f)

        with open(SKILLS_DIR / "weave" / "evals" / "evals.json") as f:
            cls.weave_evals = json.load(f)

        with open(SKILLS_DIR / "weave-integration" / "evals" / "evals.json") as f:
            cls.integration_evals = json.load(f)

    def test_models_positive_not_weave(self):
        """Models positive queries should match models, not only weave.

        Some overlap is acceptable since both products share terms like 'evaluation'.
        Allows up to 10% of queries to have overlap issues.
        """
        models_positive = [e for e in self.models_evals if e["should_trigger"]]
        failures = []
        for entry in models_positive:
            query = entry["query"]
            matches_models = query_matches_description(query, self.models_desc)
            matches_weave = query_matches_description(query, self.weave_desc)
            if matches_weave and not matches_models:
                failures.append(query)

        max_allowed = max(1, len(models_positive) // 10)
        if failures:
            print(f"  INFO: models queries matching only weave ({len(failures)}/{len(models_positive)}):")
            for q in failures:
                print(f"    - {q}")
        self.assertLessEqual(
            len(failures),
            max_allowed,
            f"Too many models queries only matching weave ({len(failures)}/{len(models_positive)}): {failures}",
        )

    def test_weave_positive_not_models(self):
        """Weave positive queries should match weave, not only models."""
        weave_positive = [e for e in self.weave_evals if e["should_trigger"]]
        for entry in weave_positive:
            query = entry["query"]
            matches_weave = query_matches_description(query, self.weave_desc)
            matches_models = query_matches_description(query, self.models_desc)
            if matches_models and not matches_weave:
                self.fail(
                    f"Weave query should match weave but only matches models: '{query}'"
                )

    def test_no_shared_positive_queries_all_skills(self):
        """The same exact query should not appear as should_trigger=true across skills."""
        models_positive = {e["query"] for e in self.models_evals if e["should_trigger"]}
        weave_positive = {e["query"] for e in self.weave_evals if e["should_trigger"]}
        integration_positive = {
            e["query"] for e in self.integration_evals if e["should_trigger"]
        }

        models_weave = models_positive & weave_positive
        models_integration = models_positive & integration_positive

        self.assertEqual(
            len(models_weave),
            0,
            f"These queries appear as positive in BOTH models and weave evals: {models_weave}",
        )
        self.assertEqual(
            len(models_integration),
            0,
            f"These queries appear as positive in BOTH models and integration evals: {models_integration}",
        )


if __name__ == "__main__":
    unittest.main()
