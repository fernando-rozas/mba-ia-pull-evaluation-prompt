"""Baixa o prompt semente do LangSmith Prompt Hub para YAML."""

import sys
from pathlib import Path

from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langsmith import Client
from langsmith.utils import LangSmithError

from utils import check_env_vars, print_section_header, save_yaml

SEED_PROMPT = "leonanluppi/bug_to_user_story_v1"
PROMPT_NAME = SEED_PROMPT.split("/")[1]
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "prompts" / f"{PROMPT_NAME}.yml"


def pull_prompts_from_langsmith() -> bool:
    client = Client()
    prompt = client.pull_prompt(
        SEED_PROMPT,
        dangerously_pull_public_prompt=True,
    )
    if not isinstance(prompt, ChatPromptTemplate):
        raise ValueError("O prompt semente não é um ChatPromptTemplate.")

    messages = prompt.messages
    if (
        len(messages) != 2
        or not isinstance(messages[0], SystemMessagePromptTemplate)
        or not isinstance(messages[1], HumanMessagePromptTemplate)
    ):
        raise ValueError("Esperava uma mensagem de sistema seguida de uma mensagem de usuário.")

    metadata = client.get_prompt(SEED_PROMPT)
    data = {
        PROMPT_NAME: {
            "description": (
                metadata.description if metadata and metadata.description
                else "Prompt para converter relatos de bugs em User Stories"
            ),
            "system_prompt": messages[0].prompt.template,
            "user_prompt": messages[1].prompt.template,
            "version": "v1",
            "tags": list(metadata.tags or []) if metadata else [],
        },
    }
    if not save_yaml(data, str(OUTPUT_PATH)):
        return False

    print(f"{SEED_PROMPT} salvo em {OUTPUT_PATH}")
    return True


def main() -> int:
    print_section_header("PULL DO PROMPT SEMENTE")
    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    try:
        return 0 if pull_prompts_from_langsmith() else 1
    except (LangSmithError, ValueError) as error:
        print(f"Falha ao baixar {SEED_PROMPT}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
