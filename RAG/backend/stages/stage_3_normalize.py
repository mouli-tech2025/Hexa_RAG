import json
import re
from pathlib import Path
from typing import Dict, Optional, Tuple

from config import NORMALIZATION_TERMS_PATH

# domain -> (terms dict, compiled whole-word pattern or None if no terms)
_domain_cache: Dict[str, Tuple[dict, Optional[re.Pattern]]] = {}


def _load_domain(domain: str) -> Tuple[dict, Optional[re.Pattern]]:
    if domain in _domain_cache:
        return _domain_cache[domain]

    path = Path(NORMALIZATION_TERMS_PATH) / f"{domain}.json"
    if path.is_file():
        with open(path, "r", encoding="utf-8") as f:
            terms: dict = json.load(f)
    else:
        # No dict for this domain - normalize_text() becomes a no-op for it
        # rather than erroring, so unconfigured domains still work.
        terms = {}

    if terms:
        # Longest abbreviation first so overlapping terms (e.g. "N1" vs "N")
        # don't get partially shadowed by a shorter match.
        alternation = "|".join(re.escape(term) for term in sorted(terms, key=len, reverse=True))
        pattern = re.compile(r"\b(?:" + alternation + r")\b")
    else:
        pattern = None

    _domain_cache[domain] = (terms, pattern)
    return terms, pattern


def normalize_text(text: str, domain: str = "general") -> str:
    terms, pattern = _load_domain(domain)
    if pattern is None:
        return text

    def _replace(match: re.Match) -> str:
        abbrev = match.group(0)
        expansion = terms[abbrev]

        # Don't double-expand when the spelled-out form already precedes
        # this abbreviation in parens, e.g. "High Pressure Compressor
        # (HPC)" should stay as-is, not become "... (High Pressure
        # Compressor)".
        before = text[: match.start()].rstrip()
        if before.endswith("(") and before[:-1].rstrip().endswith(expansion):
            return abbrev

        return expansion

    return pattern.sub(_replace, text)
