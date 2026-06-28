import json
import sys
from pathlib import Path

DEFAULTS: dict = {
    "monitor_index": 1,
    "model": "claude-haiku-4-5-20251001",
    "change_threshold": 8.0,
    "poll_interval_seconds": 3.0,
    "min_seconds_between_auto_calls": 15.0,
    "voice_enabled": False,
    "hotkey": "<ctrl>+<shift>+g",
    "game_name": "Warhammer 40000: Rogue Trader",
    "max_history_messages": 16,
    "capture_scale": 0.25,
}


def _base_dir() -> Path:
    # When frozen by PyInstaller the .exe lives next to config.json
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent.parent


def load_config() -> dict:
    cfg = dict(DEFAULTS)
    p = _base_dir() / "config.json"
    if p.exists():
        try:
            cfg.update(json.loads(p.read_text(encoding="utf-8")))
        except Exception as e:
            print(f"[config] Warning loading config.json: {e}")
    return cfg
