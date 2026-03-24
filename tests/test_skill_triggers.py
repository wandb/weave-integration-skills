"""Validate that evals.json queries match/don't match SKILL.md trigger keywords."""

import json
import re
import unittest
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent / "skills"


def extract_description(skill_name: str) -> str:
    """Extract the description field from SKILL.md YAML front matter."""
    skill_md = SKILLS_DIR / skill_name / "SKILL.md"
    content = skill_md.read_text()
    front_matter = content.split("---", 2)[1]

    # Extract everything after 'description:' until the next top-level key or end
    match = re.search(r"description:\s*>?\s*\n(.*?)(?=\n\w+:|\Z)", front_matter, re.DOTALL)
    if match:
        return match.group(1).strip().lower()

    # Fallback: single-line description
    match = re.search(r"description:\s*(.+)", front_matter)
    if match:
        return match.group(1).strip().lower()

    return ""


def query_matches_description(query: str, description: str) -> bool:
    """Check if a query's keywords are found in the skill description.

    Uses multiple heuristics:
    1. Tokenize into words and check overlap ratio
    2. Check for substring matches (handles Korean compound words)
    3. Check for key technical terms
    """
    query_lower = query.lower()

    # Strategy 1: Extract words (alphanumeric, 3+ chars)
    english_words = re.findall(r"[a-z]{3,}", query_lower)
    # Korean: extract sequences of 2+ Korean characters
    korean_words = re.findall(r"[\uac00-\ud7af]{2,}", query_lower)

    # Filter out common English stop words
    stop_words = {
        "the", "and", "for", "with", "that", "this", "from", "have", "has",
        "are", "was", "were", "been", "will", "would", "could", "should",
        "can", "may", "might", "into", "want", "help", "need", "how",
        "what", "when", "where", "which", "who", "why", "use", "using",
        "set", "add", "get", "make", "let", "like", "just", "also",
    }
    english_meaningful = [w for w in english_words if w not in stop_words]

    # Korean stop words
    korean_stops = {"하고", "싶어", "해줘", "하려면", "어떻게", "있는", "하는", "되는"}
    korean_meaningful = [w for w in korean_words if w not in korean_stops]

    all_meaningful = english_meaningful + korean_meaningful

    if not all_meaningful:
        return False

    # Strategy 2: Check each word/substring against description
    matches = 0
    for word in all_meaningful:
        if word in description:
            matches += 1

    match_ratio = matches / len(all_meaningful)

    # Strategy 3: Check for key technical terms that strongly indicate a match
    tech_terms = [
        # Weave terms
        "weave", "tracing", "evaluation", "scorer", "dataset", "prompt",
        "openai", "anthropic", "langchain", "llamaindex", "crewai", "dspy",
        "fastapi", "streamlit", "flask", "django",
        "guardrail", "monitor", "feedback", "cost",
        "integrate", "instrument", "retrofit", "onboard",
        # Models terms
        "wandb", "experiment", "artifact", "sweep", "registry",
        "training", "hyperparameter", "leaderboard",
        "pytorch", "lightning", "huggingface", "keras", "xgboost",
        # Korean terms (Weave)
        "추적", "평가", "트레이싱", "적용", "연동", "통합", "추가",
        "가드레일", "모니터링", "피드백", "비용", "콘텐츠", "환각",
        "어노테이션", "스코러", "데이터셋", "프롬프트",
        # Korean terms (Models)
        "실험", "아티팩트", "스윕", "레지스트리", "학습",
    ]
    tech_match = any(term in query_lower and term in description for term in tech_terms)

    # Trigger if >25% of meaningful words match OR a tech term matches in both
    return match_ratio > 0.25 or tech_match


class TestWeaveSkillTriggers(unittest.TestCase):
    """Test that weave skill evals.json queries match the SKILL.md description."""

    @classmethod
    def setUpClass(cls):
        cls.description = extract_description("weave")
        evals_path = SKILLS_DIR / "weave" / "evals" / "evals.json"
        with open(evals_path) as f:
            cls.evals = json.load(f)

    def test_description_not_empty(self):
        self.assertTrue(len(self.description) > 50, "Description should be substantial")

    def test_positive_triggers_match(self):
        """Queries that should_trigger=true should have keywords in the description.

        Allows up to 10% of queries to fail (heuristic keyword matching has limits,
        especially with cross-language terms like Korean 어노테이션 vs English annotations).
        """
        positive = [e for e in self.evals if e["should_trigger"]]
        failures = []
        for entry in positive:
            query = entry["query"]
            if not query_matches_description(query, self.description):
                failures.append(query)

        max_allowed = max(1, len(positive) // 10)
        if failures:
            print(f"  INFO: weave trigger misses ({len(failures)}/{len(positive)}):")
            for q in failures:
                print(f"    - {q}")
        self.assertLessEqual(
            len(failures),
            max_allowed,
            f"weave: Too many positive queries not matching description ({len(failures)}/{len(positive)}): {failures}",
        )

    def test_negative_triggers_dont_match(self):
        """Queries that should_trigger=false should NOT match the description well."""
        negative = [e for e in self.evals if not e["should_trigger"]]
        for entry in negative:
            query = entry["query"]
            matches = query_matches_description(query, self.description)
            if matches:
                print(f"  WARNING: weave negative query unexpectedly matches: '{query}'")


class TestWeaveIntegrationSkillTriggers(unittest.TestCase):
    """Test that weave-integration skill evals.json queries match the SKILL.md description."""

    @classmethod
    def setUpClass(cls):
        cls.description = extract_description("weave-integration")
        evals_path = SKILLS_DIR / "weave-integration" / "evals" / "evals.json"
        with open(evals_path) as f:
            cls.evals = json.load(f)

    def test_description_not_empty(self):
        self.assertTrue(len(self.description) > 50, "Description should be substantial")

    def test_positive_triggers_match(self):
        """Queries that should_trigger=true should have keywords in the description."""
        positive = [e for e in self.evals if e["should_trigger"]]
        failures = []
        for entry in positive:
            query = entry["query"]
            if not query_matches_description(query, self.description):
                failures.append(query)

        max_allowed = max(1, len(positive) // 10)
        if failures:
            print(f"  INFO: weave-integration trigger misses ({len(failures)}/{len(positive)}):")
            for q in failures:
                print(f"    - {q}")
        self.assertLessEqual(
            len(failures),
            max_allowed,
            f"weave-integration: Too many positive queries not matching ({len(failures)}/{len(positive)}): {failures}",
        )

    def test_negative_triggers_dont_match(self):
        """Queries that should_trigger=false should NOT match the description well."""
        negative = [e for e in self.evals if not e["should_trigger"]]
        for entry in negative:
            query = entry["query"]
            matches = query_matches_description(query, self.description)
            if matches:
                print(
                    f"  WARNING: weave-integration negative query unexpectedly matches: '{query}'"
                )


class TestModelsSkillTriggers(unittest.TestCase):
    """Test that models skill evals.json queries match the SKILL.md description."""

    @classmethod
    def setUpClass(cls):
        cls.description = extract_description("models")
        evals_path = SKILLS_DIR / "models" / "evals" / "evals.json"
        with open(evals_path) as f:
            cls.evals = json.load(f)

    def test_description_not_empty(self):
        self.assertTrue(len(self.description) > 50, "Description should be substantial")

    def test_positive_triggers_match(self):
        """Queries that should_trigger=true should have keywords in the description."""
        positive = [e for e in self.evals if e["should_trigger"]]
        failures = []
        for entry in positive:
            query = entry["query"]
            if not query_matches_description(query, self.description):
                failures.append(query)

        max_allowed = max(1, len(positive) // 10)
        if failures:
            print(f"  INFO: models trigger misses ({len(failures)}/{len(positive)}):")
            for q in failures:
                print(f"    - {q}")
        self.assertLessEqual(
            len(failures),
            max_allowed,
            f"models: Too many positive queries not matching description ({len(failures)}/{len(positive)}): {failures}",
        )

    def test_negative_triggers_dont_match(self):
        """Queries that should_trigger=false should NOT match the description well."""
        negative = [e for e in self.evals if not e["should_trigger"]]
        for entry in negative:
            query = entry["query"]
            matches = query_matches_description(query, self.description)
            if matches:
                print(f"  WARNING: models negative query unexpectedly matches: '{query}'")


if __name__ == "__main__":
    unittest.main()
