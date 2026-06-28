"""
Global hotkey listener via pynput.
On Windows this usually works without admin rights.
If a game uses kernel-level anti-cheat (EAC, BE), admin rights may be required.
"""
from typing import Callable

HOTKEY_AVAILABLE = False

try:
    from pynput import keyboard as _kb

    def start_hotkey_listener(combo: str, callback: Callable[[], None]):
        """
        Start a background listener for the given combo string,
        e.g. "<ctrl>+<shift>+g".
        Returns the Listener object (call .stop() to shut it down).
        """
        try:
            hotkey = _kb.HotKey(_kb.HotKey.parse(combo), callback)

            def _press(key):
                try:
                    hotkey.press(listener.canonical(key))
                except Exception:
                    pass

            def _release(key):
                try:
                    hotkey.release(listener.canonical(key))
                except Exception:
                    pass

            listener = _kb.Listener(on_press=_press, on_release=_release)
            listener.daemon = True
            listener.start()
            return listener
        except Exception as e:
            print(f"[hotkey] Failed to start listener for '{combo}': {e}")
            return None

    HOTKEY_AVAILABLE = True

except ImportError:
    def start_hotkey_listener(combo: str, callback: Callable[[], None]):
        print("[hotkey] pynput not installed — global hotkey disabled.")
        return None
