# flake8: noqa

def transform_to_dict(metadata: str) -> dict[str, str]:
    if not metadata:
        return {}

    text = metadata.strip()
    if not (text.startswith("[") and text.endswith("]")):
        raise ValueError("Metadata must be enclosed in brackets")

    content = text[1:-1].strip()
    if not content:
        return {}

    result: dict[str, str] = {}

    for pair in content.split():
        if "=" not in pair:
            raise ValueError(f"Invalid metadata pair: {pair}")

        key, value = pair.split("=", 1)
        if not key:
            raise ValueError("Metadata key cannot be empty")

        result[key] = value

    return result

def main() -> None:
    s: str = "[zone=restricted color=orange max_drones=3]"
    print(transform_to_dict(s))

if __name__ == "__main__":
    main()
