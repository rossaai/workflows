import re
from typing import Optional


def clean_and_format_string(input_str: str) -> Optional[str]:
    # Replace spaces with hyphens
    input_str = input_str.replace(" ", "-")

    # Convert the string to lowercase
    input_str = input_str.lower()

    # Remove all characters that are not alphanumeric, hyphens, or underscores
    cleaned_str = re.sub(r"[^a-z0-9-_]", "", input_str)

    # Clamp the string to a maximum length of 64 characters
    clamped_str = cleaned_str[:64]

    return clamped_str
