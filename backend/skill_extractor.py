"""NLP skill extraction and semantic matching.

Approach
--------
1. Normalise the text (lower-case, unify whitespace).
2. Match every alias in the skill catalogue with boundary-aware regular
   expressions (so "java" does not match "javascript" and "sql" does not match
   "mysql").
3. Optionally use spaCy (if installed) only to support sentence handling; the
   core method works without it so the app runs on a normal laptop.
4. A semantic matcher (character n-gram TF-IDF cosine similarity from
   scikit-learn; Sentence Transformers if installed) finds near matches.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from typing import Dict, List

from config import SEMANTIC_THRESHOLD, SKILLS_FILE


@lru_cache(maxsize=1)
def load_data() -> dict:
    with open(SKILLS_FILE, "r", encoding="utf-8") as fh:
        return json.load(fh)


def get_catalog() -> Dict[str, dict]:
    return load_data()["skill_catalog"]


def get_roles() -> Dict[str, dict]:
    return load_data()["roles"]


def normalize(text: str) -> str:
    text = text.replace("\u2022", " ").replace("\u2013", "-").replace("\u2014", "-")
    return re.sub(r"[ \t]+", " ", text.lower())


@lru_cache(maxsize=1)
def _compiled_patterns() -> Dict[str, re.Pattern]:
    patterns = {}
    for skill, info in get_catalog().items():
        names = {skill.lower(), *[a.lower() for a in info["aliases"]]}
        # longest first so "scikit-learn" wins over shorter alternatives
        alt = "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True))
        patterns[skill] = re.compile(rf"(?<![a-z0-9+#])(?:{alt})(?![a-z0-9+#])")
    return patterns


def extract_skills(text: str) -> Dict[str, List[str]]:
    """Return {'technical': [...], 'soft': [...]} using canonical skill names."""
    norm = normalize(text or "")
    catalog = get_catalog()
    technical, soft = [], []
    for skill, pattern in _compiled_patterns().items():
        if pattern.search(norm):
            (soft if catalog[skill]["category"] == "soft" else technical).append(skill)
    return {"technical": sorted(technical), "soft": sorted(soft)}


def all_skills(text: str) -> List[str]:
    found = extract_skills(text)
    return found["technical"] + found["soft"]


# ----------------------------------------------------------------- semantic
class SemanticMatcher:
    """Finds the most similar candidate for a skill name.

    Uses Sentence Transformers when available; otherwise character n-gram
    TF-IDF cosine similarity. Scores are similarity values, not probabilities.
    """

    def __init__(self) -> None:
        self.backend = "tfidf-char-ngrams"
        self._model = None
        try:  # optional heavy dependency
            from sentence_transformers import SentenceTransformer  # type: ignore

            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            self.backend = "sentence-transformers"
        except Exception:
            self._model = None

    def best_match(self, skill: str, candidates: List[str]) -> tuple[str | None, float]:
        if not candidates:
            return None, 0.0
        if self._model is not None:
            from sentence_transformers import util  # type: ignore

            emb = self._model.encode([skill] + candidates)
            sims = util.cos_sim(emb[0], emb[1:])[0].tolist()
        else:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 4))
            try:
                matrix = vec.fit_transform([skill.lower()] + [c.lower() for c in candidates])
            except ValueError:
                return None, 0.0
            sims = cosine_similarity(matrix[0:1], matrix[1:])[0].tolist()
        idx = max(range(len(sims)), key=lambda i: sims[i])
        return candidates[idx], float(sims[idx])


_matcher: SemanticMatcher | None = None


def get_matcher() -> SemanticMatcher:
    global _matcher
    if _matcher is None:
        _matcher = SemanticMatcher()
    return _matcher


def semantic_candidate(skill: str, candidates: List[str], threshold: float = SEMANTIC_THRESHOLD):
    best, score = get_matcher().best_match(skill, candidates)
    if best is not None and score >= threshold:
        return best, round(score, 3)
    return None, round(score, 3)
