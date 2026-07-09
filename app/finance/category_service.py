import rapidfuzz


def find_similar_category(
    new_name: str, existing_categories: list[str], threshold: int = 80
) -> str | None:
    if not existing_categories:
        return None

    similar = rapidfuzz.process.extractOne(new_name, existing_categories)
    if similar is not None and similar[1] >= threshold:
        return similar[0]
    return None
