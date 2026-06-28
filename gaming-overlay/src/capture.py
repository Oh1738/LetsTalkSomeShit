"""
Background capture thread: grabs periodic screenshots, emits only on
meaningful screen change (suitable for turn-based games).
"""
import io
import base64
import threading
from typing import Callable

import numpy as np
from PIL import Image
import mss


class CaptureThread(threading.Thread):
    def __init__(self, config: dict, on_change: Callable[[str], None]):
        super().__init__(daemon=True, name="CaptureThread")
        self._cfg = config
        self._on_change = on_change
        self._stop = threading.Event()
        self._prev_gray: np.ndarray | None = None

    def stop(self) -> None:
        self._stop.set()

    def run(self) -> None:
        mon_idx   = int(self._cfg.get("monitor_index", 1))
        threshold = float(self._cfg.get("change_threshold", 8.0))
        interval  = float(self._cfg.get("poll_interval_seconds", 3.0))
        scale     = float(self._cfg.get("capture_scale", 0.25))

        with mss.mss() as sct:
            monitors = sct.monitors  # [0] = all combined, [1+] = individual
            mon_idx = max(1, min(mon_idx, len(monitors) - 1))
            monitor = monitors[mon_idx]

            while not self._stop.is_set():
                try:
                    shot = sct.grab(monitor)
                    full_img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")

                    # Downscale grayscale for cheap change detection
                    w = max(1, int(full_img.width * scale))
                    h = max(1, int(full_img.height * scale))
                    small = full_img.resize((w, h), Image.LANCZOS).convert("L")
                    arr = np.asarray(small, dtype=np.float32)

                    if self._prev_gray is not None:
                        diff = float(np.mean(np.abs(arr - self._prev_gray)))
                        if diff >= threshold:
                            self._prev_gray = arr
                            b64 = encode_jpeg(full_img)
                            try:
                                self._on_change(b64)
                            except Exception as e:
                                print(f"[capture] on_change error: {e}")
                    else:
                        self._prev_gray = arr

                except Exception as e:
                    print(f"[capture] Grab error: {e}")

                self._stop.wait(interval)


def encode_jpeg(img: Image.Image, max_height: int = 720) -> str:
    """Encode a PIL image as a base64 JPEG, downscaling if taller than max_height."""
    if img.height > max_height:
        ratio = max_height / img.height
        img = img.resize((int(img.width * ratio), max_height), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=72, optimize=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")
