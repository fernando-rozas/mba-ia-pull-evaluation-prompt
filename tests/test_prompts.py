"""Validação do prompt otimizado em YAML."""

import re
from pathlib import Path

import pytest
import yaml

PROMPT_PATH = (
    Path(__file__).resolve().parents[1] / "prompts" / "bug_to_user_story_v2.yml"
)


@pytest.fixture(scope="module")
def prompt():
    return yaml.safe_load(PROMPT_PATH.read_text(encoding="utf-8"))["bug_to_user_story_v2"]


def test_prompt_has_system_prompt(prompt):
    assert isinstance(prompt.get("system_prompt"), str)
    assert prompt["system_prompt"].strip()


def test_prompt_has_role_definition(prompt):
    assert re.search(r"\bvocê é um product manager\b", prompt["system_prompt"], re.IGNORECASE)


def test_prompt_mentions_format(prompt):
    system = prompt["system_prompt"]
    assert re.search(r"User Story em Markdown", system, re.IGNORECASE)
    for part in ("Como [persona]", "eu quero", "para que", "Critérios de Aceitação"):
        assert part in system


def test_prompt_has_few_shot_examples(prompt):
    examples = re.split(r"(?m)^### Exemplo \d+.*$", prompt["system_prompt"])[1:]
    assert len(examples) >= 2
    for example in examples:
        assert re.fullmatch(r"\s*Entrada:\s*\S[\s\S]*?\n\s*Saída:\s*\S[\s\S]*", example)


def test_prompt_no_todos():
    assert "[TODO]" not in PROMPT_PATH.read_text(encoding="utf-8").upper()


def test_minimum_techniques(prompt):
    techniques = prompt["techniques_applied"]
    assert isinstance(techniques, list)
    assert all(isinstance(item, str) and item.strip() for item in techniques)
    names = {item.strip().casefold() for item in techniques}
    assert "few-shot learning" in names
    assert names & {
        "role prompting", "chain of thought", "tree of thought", "skeleton of thought", "react",
    }
    assert len(names) >= 2
