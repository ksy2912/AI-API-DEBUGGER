import re

_PLACEHOLDER_PATTERN = re.compile(r"\{\{(\s*[\w.-]+\s*)\}\}")


def substitute_variables(text: str | None, variables: dict[str, str]) -> str | None:
    if text is None:
        return None

    def replacer(match: re.Match[str]) -> str:
        key = match.group(1).strip()
        if key not in variables:
            raise ValueError(f"Undefined environment variable: {{{{{key}}}}}")
        return variables[key]

    return _PLACEHOLDER_PATTERN.sub(replacer, text)


def substitute_dict(data: dict, variables: dict[str, str]) -> dict[str, str]:
    return {
        str(key): substitute_variables(str(value), variables) or ""
        for key, value in data.items()
    }


def has_unresolved_placeholders(text: str) -> bool:
    return bool(_PLACEHOLDER_PATTERN.search(text))
