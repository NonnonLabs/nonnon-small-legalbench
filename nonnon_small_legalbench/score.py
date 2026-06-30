from __future__ import annotations

import re
import string


def normalize(text: object) -> str:
    value = str(text).strip().lower()
    value = value.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    value = re.sub(r"\s+", " ", value)
    value = value.strip(string.whitespace + string.punctuation)
    return value


def score_prediction(prediction: str, reference: object) -> float:
    """Public, label-normalized scorer.

    This is intentionally small and auditable. An independent evaluator may use
    a different scorer; this repository exists to make public-split reproduction
    easy, not to constrain third-party evaluation.
    """
    pred = normalize(prediction)
    ref = normalize(reference)
    if not ref:
        return 0.0
    if pred == ref:
        return 1.0
    first_line = normalize(str(prediction).splitlines()[0] if prediction else "")
    last_line = normalize(str(prediction).splitlines()[-1] if prediction else "")
    if first_line == ref or last_line == ref:
        return 1.0
    if ref in {"yes", "no"}:
        match = re.search(r"\b(yes|no)\b", pred)
        return 1.0 if match and match.group(1) == ref else 0.0
    if len(ref) == 1 and ref in "abcdef":
        match = re.search(r"\b([a-f])\b", pred)
        return 1.0 if match and match.group(1) == ref else 0.0
    if ref in pred and len(ref) >= 6:
        return 1.0
    return 0.0
