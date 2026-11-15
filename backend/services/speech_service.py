from typing import Dict, Any, Tuple
import io
import base64
import re
from gtts import gTTS

# Language BCP-47 voice tags for high fidelity Web Speech API and TTS
VOICE_LANGUAGE_TAGS: Dict[str, str] = {
    "en": "en-IN", # Indian English accent
    "ta": "ta-IN", # Tamil
    "te": "te-IN", # Telugu
    "hi": "hi-IN", # Hindi
    "ml": "ml-IN", # Malayalam
    "kn": "kn-IN", # Kannada
    "bn": "bn-IN", # Bengali
    "mr": "mr-IN"  # Marathi
}

GTTS_LANG_MAP: Dict[str, str] = {
    "en": "en",
    "ta": "ta",
    "te": "te",
    "hi": "hi",
    "ml": "ml",
    "kn": "kn",
    "bn": "bn",
    "mr": "mr"
}

# In-memory LRU-like cache for generated audio to give instantaneous 0ms playback
_audio_cache: Dict[str, bytes] = {}
_MAX_CACHE_ITEMS = 200

def _clean_speech_text(text: str) -> str:
    """Clean formatting and punctuation symbols so speech sounds natural."""
    cleaned = re.sub(r'[*_~#`>|]', '', text)
    cleaned = cleaned.replace('⚠️', 'Warning: ').replace('•', ', ')
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def generate_speech_audio(text: str, language_code: str) -> Tuple[bytes, str]:
    """
    Generates authentic regional MP3 audio using gTTS.
    Returns (audio_bytes, 'audio/mpeg').
    """
    cleaned = _clean_speech_text(text)
    lang = GTTS_LANG_MAP.get(language_code, "en")
    cache_key = f"{lang}:{cleaned}"

    if cache_key in _audio_cache:
        return _audio_cache[cache_key], "audio/mpeg"

    try:
        tts = gTTS(text=cleaned, lang=lang, slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        audio_bytes = buf.getvalue()

        # Cache audio
        if len(_audio_cache) >= _MAX_CACHE_ITEMS:
            # Drop oldest 50 items
            keys_to_remove = list(_audio_cache.keys())[:50]
            for k in keys_to_remove:
                _audio_cache.pop(k, None)
        _audio_cache[cache_key] = audio_bytes

        return audio_bytes, "audio/mpeg"
    except Exception as e:
        print(f"gTTS audio generation error for lang={lang}: {e}")
        # Fallback to English if regional generation hit an unexpected error
        if lang != "en":
            try:
                tts = gTTS(text=cleaned, lang="en", slow=False)
                buf = io.BytesIO()
                tts.write_to_fp(buf)
                buf.seek(0)
                return buf.getvalue(), "audio/mpeg"
            except Exception:
                pass
        return b"", "audio/mpeg"

def prepare_speech_payload(text: str, language_code: str) -> Dict[str, Any]:
    """
    Formats the verified text for speech synthesis and embeds base64 audio.
    """
    cleaned_text = _clean_speech_text(text)
    locale = VOICE_LANGUAGE_TAGS.get(language_code, "en-IN")
    
    audio_bytes, _ = generate_speech_audio(cleaned_text, language_code)
    
    audio_base64 = ""
    has_audio = False
    if audio_bytes:
        try:
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            has_audio = True
        except Exception as e:
            print(f"Error encoding audio base64: {e}")

    return {
        "text": cleaned_text,
        "language": language_code,
        "voice_locale": locale,
        "audio_base64": audio_base64,
        "has_audio": has_audio,
        "rate": 0.95,
        "pitch": 1.0
    }
