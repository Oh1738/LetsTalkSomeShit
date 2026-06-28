"""
Gaming Co-Pilot Overlay — entry point.
Wires together the capture thread, AI worker, and PySide6 overlay.
"""
import sys
import time
from pathlib import Path

# Allow "from src.xxx import ..." whether running from source or frozen .exe
if not getattr(sys, "frozen", False):
    sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.config import load_config
from src.signals import AppSignals
from src.ai_worker import AIWorker
from src.capture import CaptureThread, encode_jpeg
from src.overlay import OverlayWindow
from src.hotkey import start_hotkey_listener


def main() -> None:
    cfg = load_config()

    app = QApplication(sys.argv)
    app.setApplicationName("Gaming Co-Pilot")
    app.setQuitOnLastWindowClosed(True)

    signals = AppSignals()
    ai_worker = AIWorker(cfg, signals)

    # Rate-gate: don't spam the API if the screen keeps changing rapidly
    _last_watch_ts = [0.0]
    min_gap = float(cfg.get("min_seconds_between_auto_calls", 15.0))

    def on_screen_change(b64: str) -> None:
        now = time.monotonic()
        if now - _last_watch_ts[0] >= min_gap:
            _last_watch_ts[0] = now
            ai_worker.submit_watch(b64)

    def capture_current() -> str | None:
        """Grab the current screen and return as base64 JPEG (for user chat context)."""
        try:
            import mss
            from PIL import Image

            mon_idx = int(cfg.get("monitor_index", 1))
            with mss.mss() as sct:
                monitors = sct.monitors
                mon_idx = max(1, min(mon_idx, len(monitors) - 1))
                shot = sct.grab(monitors[mon_idx])
                img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
            return encode_jpeg(img)
        except Exception as e:
            print(f"[main] capture_current error: {e}")
            return None

    capture_thread = CaptureThread(cfg, on_screen_change)
    overlay = OverlayWindow(cfg, signals, ai_worker, capture_current)

    # Global hotkey: toggle overlay show/hide
    hotkey_combo = cfg.get("hotkey", "<ctrl>+<shift>+g")
    listener = start_hotkey_listener(hotkey_combo, overlay.toggle_visibility)

    ai_worker.start()
    capture_thread.start()
    overlay.show()

    ret = app.exec()

    capture_thread.stop()
    ai_worker.stop()
    if listener is not None:
        try:
            listener.stop()
        except Exception:
            pass

    sys.exit(ret)


if __name__ == "__main__":
    main()
