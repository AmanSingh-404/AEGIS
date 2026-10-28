"""Deterministic scoring functions for AEGIS benchmark evaluations."""

import re
from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class Score:
    """Normalized metric result."""

    name: str
    value: float


def normalize_text(text: str, *, lowercase: bool = True) -> str:
    """Normalize whitespace and optionally lowercase text."""
    normalized = " ".join(text.split())
    return normalized.lower() if lowercase else normalized


def exact_match(
    expected: str,
    actual: str,
    *,
    lowercase: bool = True,
) -> Score:
    """Return 1.0 for a match and 0.0 otherwise."""
    return Score(
        name="exact_match",
        value=float(
            normalize_text(expected, lowercase=lowercase)
            == normalize_text(actual, lowercase=lowercase)
        ),
    )


def token_f1(expected: str, actual: str) -> Score:
    """Calculate token-level F1 using multiset word overlap."""
    expected_tokens = re.findall(r"\w+", expected.lower())
    actual_tokens = re.findall(r"\w+", actual.lower())

    if not expected_tokens and not actual_tokens:
        return Score(name="token_f1", value=1.0)

    if not expected_tokens or not actual_tokens:
        return Score(name="token_f1", value=0.0)

    overlap = sum(
        (Counter(expected_tokens) & Counter(actual_tokens)).values()
    )

    precision = overlap / len(actual_tokens)
    recall = overlap / len(expected_tokens)

    if precision + recall == 0:
        value = 0.0
    else:
        value = 2 * precision * recall / (precision + recall)

    return Score(name="token_f1", value=value)
