"""Publica o prompt otimizado no LangSmith Prompt Hub."""

import os
import sys
from pathlib import Path
from string import Formatter

from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client
from langsmith.utils import LangSmithError

from utils import check_env_vars, load_yaml, print_section_header, validate_prompt_structure

PROMPT_NAME = "bug_to_user_story_v2"
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / f"{PROMPT_NAME}.yml"


def validate_prompt(prompt_data: dict) -> tuple[bool, list[str]]:
    if not isinstance(prompt_data, dict):
        return False, [f"O YAML deve conter o mapeamento {PROMPT_NAME}."]

    errors = []
    for field in ("description", "system_prompt", "user_prompt", "version"):
        value = prompt_data.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} deve ser um texto não vazio.")

    for field in ("tags", "techniques_applied"):
        values = prompt_data.get(field)
        if not isinstance(values, list) or not values or any(
            not isinstance(value, str) or not value.strip() for value in values
        ):
            errors.append(f"{field} deve ser uma lista de textos não vazios.")

    if errors:
        return False, errors

    _, errors = validate_prompt_structure(prompt_data)
    if prompt_data["version"] != "v2":
        errors.append("A versão deve ser v2.")
    if len({item.strip().casefold() for item in prompt_data["techniques_applied"]}) < 2:
        errors.append("Liste pelo menos duas técnicas distintas.")

    try:
        system_fields = [
            field for _, field, _, _ in Formatter().parse(prompt_data["system_prompt"])
            if field is not None
        ]
        user_fields = [
            (field, spec, conversion)
            for _, field, spec, conversion in Formatter().parse(prompt_data["user_prompt"])
            if field is not None
        ]
        if system_fields or user_fields != [("bug_report", "", None)]:
            errors.append("Use {bug_report} uma única vez, na mensagem de usuário.")
    except ValueError as error:
        errors.append(f"Template inválido: {error}")

    return not errors, errors


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    valid, errors = validate_prompt(prompt_data)
    if not valid:
        for error in errors:
            print(error, file=sys.stderr)
        return False

    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_data["system_prompt"]),
        ("user", prompt_data["user_prompt"]),
    ])
    techniques = prompt_data["techniques_applied"]
    technique_tags = [technique.lower().replace(" ", "-") for technique in techniques]
    tags = list(dict.fromkeys([*prompt_data["tags"], *technique_tags]))
    description = f"{prompt_data['description']} Técnicas aplicadas: {', '.join(techniques)}."

    try:
        client = Client()
        url = client.push_prompt(
            prompt_name,
            object=prompt,
            is_public=True,
            description=description,
            tags=tags,
        )
        published = client.get_prompt(prompt_name)
        if published is None or not published.is_public:
            print(f"O Hub não confirmou a publicação pública de {prompt_name}.", file=sys.stderr)
            return False
    except (LangSmithError, ValueError) as error:
        print(f"Falha ao publicar {prompt_name}: {error}", file=sys.stderr)
        return False

    print(f"Prompt público: {prompt_name}\n{url}")
    return True


def main() -> int:
    print_section_header("PUSH DO PROMPT OTIMIZADO")
    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    username = os.environ["USERNAME_LANGSMITH_HUB"].strip()
    if not username or any(character in username for character in "/:") or any(
        character.isspace() for character in username
    ):
        print("USERNAME_LANGSMITH_HUB deve conter somente o handle público.", file=sys.stderr)
        return 1

    data = load_yaml(str(PROMPT_PATH))
    prompt_data = data.get(PROMPT_NAME) if isinstance(data, dict) else None
    return 0 if push_prompt_to_langsmith(f"{username}/{PROMPT_NAME}", prompt_data) else 1


if __name__ == "__main__":
    sys.exit(main())
