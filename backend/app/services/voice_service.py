from pathlib import Path
from uuid import uuid4

from gtts import gTTS

from app.core.config import settings


GTTS_LANG_MAP = {
    "en": "en",
    "hi": "hi",
    "ta": "ta",
    "te": "te",
    "mr": "mr",
    "bn": "bn",
    "gu": "gu",
    "kn": "kn",
}


def synthesize_speech(text: str, language_code: str = "en") -> str:
    if not text.strip():
        return ""

    lang = GTTS_LANG_MAP.get(language_code, "en")
    audio_dir = Path(settings.audio_path)
    audio_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid4().hex}.mp3"
    output_path = audio_dir / filename

    tts = gTTS(text=text, lang=lang)
    tts.save(str(output_path))

    return f"/audio/{filename}"
