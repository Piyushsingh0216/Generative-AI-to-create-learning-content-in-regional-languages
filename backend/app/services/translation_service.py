from typing import Dict, List

from deep_translator import GoogleTranslator


# ====== API KEY PLACEHOLDER ======
# GOOGLE_TRANSLATE_API_KEY = "YOUR_API_KEY_HERE"
# =================================


SUPPORTED_LANGUAGES: Dict[str, str] = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "bn": "Bengali",
    "gu": "Gujarati",
    "kn": "Kannada",
}


def _chunk_text(text: str, chunk_size: int = 4500) -> List[str]:
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    current = []
    current_len = 0
    for line in text.splitlines():
        if current_len + len(line) + 1 > chunk_size and current:
            chunks.append("\n".join(current))
            current = [line]
            current_len = len(line)
        else:
            current.append(line)
            current_len += len(line) + 1
    if current:
        chunks.append("\n".join(current))

    normalized_chunks = []
    for chunk in chunks:
        if len(chunk) <= chunk_size:
            normalized_chunks.append(chunk)
            continue
        # Fallback split for very long single lines
        for idx in range(0, len(chunk), chunk_size):
            normalized_chunks.append(chunk[idx : idx + chunk_size])
    return normalized_chunks


def translate_text(text: str, target_lang: str, source_lang: str = "auto") -> str:
    if target_lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported target language code: {target_lang}")
    if source_lang != "auto" and source_lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported source language code: {source_lang}")
    if not text.strip():
        return ""

    translated_chunks = []
    for chunk in _chunk_text(text):
        translated_chunks.append(GoogleTranslator(source=source_lang, target=target_lang).translate(chunk))
    return "\n".join(translated_chunks)
