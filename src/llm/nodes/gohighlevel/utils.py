def generate_headers(pit: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {pit}",
        "Version": "v3"
    }