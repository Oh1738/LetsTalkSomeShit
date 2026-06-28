"""
Optional text-to-speech via pyttsx3.
If pyttsx3 is not installed, speak() silently does nothing.
"""

VOICE_AVAILABLE = False

try:
    import pyttsx3 as _pyttsx3

    _engine = None

    def _get_engine():
        global _engine
        if _engine is None:
            _engine = _pyttsx3.init()
            _engine.setProperty("rate", 175)
        return _engine

    def speak(text: str) -> None:
        try:
            eng = _get_engine()
            eng.say(text)
            eng.runAndWait()
        except Exception as e:
            print(f"[voice] TTS error: {e}")

    VOICE_AVAILABLE = True

except ImportError:
    def speak(text: str) -> None:
        pass
