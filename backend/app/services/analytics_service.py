import re
from collections import Counter
from typing import List, Optional

from app.models.user import User


STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "have",
    "you",
    "your",
    "are",
    "was",
    "were",
    "about",
    "into",
    "there",
    "their",
    "will",
    "would",
    "could",
}


def derive_topics(text: str, explicit_topic: Optional[str] = None) -> List[str]:
    topics = []
    if explicit_topic and explicit_topic.strip():
        topics.append(explicit_topic.strip())

    words = re.findall(r"[A-Za-z]{5,}", text.lower())
    candidates = [w for w in words if w not in STOPWORDS]
    for token, _ in Counter(candidates).most_common(3):
        topics.append(token.title())

    # Keep order while removing duplicates
    seen = set()
    unique = []
    for item in topics:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def update_user_topics(user: User, topics: List[str]) -> None:
    existing = user.topics_learned or []
    merged = existing + topics
    # Keep order while removing duplicates
    deduped = []
    seen = set()
    for topic in merged:
        if topic not in seen:
            seen.add(topic)
            deduped.append(topic)
    user.topics_learned = deduped[:50]
