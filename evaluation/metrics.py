def accuracy_score(correct: int, total: int) -> float:
    if total == 0:
        return 0.0
    return correct / total


def safe_equal(a, b) -> bool:
    return a == b


def contains_all_keywords(text: str, keywords: list[str]) -> bool:
    text_lower = text.lower()
    return all(keyword.lower() in text_lower for keyword in keywords)