"""Tests for deterministic AEGIS benchmark scoring."""

import pytest

from evaluation.benchmarks.scorers import exact_match, normalize_text, token_f1


def test_normalize_text_collapses_whitespace_and_lowercases() -> None:
    assert normalize_text("  AEGIS  Agent\nPlatform ") == "aegis agent platform"


def test_normalize_text_can_preserve_case() -> None:
    assert normalize_text(" AEGIS ", lowercase=False) == "AEGIS"


@pytest.mark.parametrize(
    ("expected", "actual", "score"),
    [
        ("hello world", "hello world", 1.0),
        ("Hello  world", "hello\nworld", 1.0),
        ("hello world", "hello there", 0.0),
        ("", "", 1.0),
    ],
)
def test_exact_match(expected: str, actual: str, score: float) -> None:
    assert exact_match(expected, actual).value == score


def test_exact_match_can_be_case_sensitive() -> None:
    assert exact_match("AEGIS", "aegis", lowercase=False).value == 0.0


@pytest.mark.parametrize(
    ("expected", "actual", "score"),
    [
        ("red blue", "red blue", 1.0),
        ("red blue", "red green", 0.5),
        ("red blue", "green yellow", 0.0),
        ("red red blue", "red blue blue", pytest.approx(2 / 3)),
        ("", "", 1.0),
        ("hello", "", 0.0),
        ("", "hello", 0.0),
    ],
)
def test_token_f1(expected: str, actual: str, score: float) -> None:
    assert token_f1(expected, actual).value == score


def test_scores_have_stable_metric_names() -> None:
    assert exact_match("a", "a").name == "exact_match"
    assert token_f1("a", "a").name == "token_f1"


def test_scores_are_immutable() -> None:
    score = exact_match("a", "a")

    with pytest.raises((AttributeError, TypeError)):
        score.value = 0.0  # type: ignore[misc]
