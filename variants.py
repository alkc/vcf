import re


def get_info_field(variant: str, key: str) -> dict | None:
    match = re.search(_info_match_pattern(key), variant)

    if match:
        return match.group(2)

    return None


def _info_match_pattern(key: str):
    return rf"({key})=([^;=]+)"
