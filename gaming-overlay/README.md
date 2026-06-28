# Gaming Co-Pilot Overlay

An always-on-top AI overlay that watches your game screen and gives you concise, specific tips — powered by Claude. Proactively notices changes (enemy positions, quest updates, stat changes) and answers your typed questions, including web searches for guides when it can't see the answer on screen.

Tested primarily with **Warhammer 40,000: Rogue Trader** but fully game-agnostic via `config.json`.

---

## Before you start — must-reads

### The game must run in Borderless Windowed mode (NOT exclusive fullscreen)

Windows exclusive fullscreen apps own the display adapter entirely. No desktop overlay can paint over them. Set your game to **Borderless Window** or **Windowed** mode in its graphics settings. Rogue Trader: Options → Display → Fullscreen Mode → **Borderless**.

### Web search costs extra and must be enabled in your Anthropic account

When you ask a question the overlay can't answer from the screen (quest steps, builds, lore), it calls the Claude web-search tool. This is billed per search and **must be enabled** in the [Anthropic Console](https://console.anthropic.com) under **API → Integrations → Web Search**. See the Console docs for current pricing. Auto-watch observations never trigger a search.

---

## Installation (copy-paste these into PowerShell)

### 1. Install Python 3.11+

Download from <https://python.org/downloads/>. During install tick **"Add Python to PATH"**.

Verify:
```powershell
python --version
```

### 2. Clone or download this project

```powershell
git clone https://github.com/oh1738/letstalksomeshit.git
cd letstalksomeshit\gaming-overlay
```

Or just download and unzip the ZIP from GitHub and `cd` into the `gaming-overlay` folder.

### 3. Create a virtual environment and install dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> **If you get "running scripts is disabled"** run this once:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 4. Set your Anthropic API key (permanent, survives reboots)

Get your key from <https://console.anthropic.com/keys>.

```powershell
setx ANTHROPIC_API_KEY "sk-ant-YOUR-KEY-HERE"
```

**Close this PowerShell window and open a fresh one** — `setx` only takes effect in new sessions.

Verify:
```powershell
echo $env:ANTHROPIC_API_KEY
```

---

## Tweak these config values first

Open `config.json` in Notepad before launching:

```json
{
  "monitor_index": 1,          // 1 = primary monitor, 2 = second monitor, etc.
  "model": "claude-haiku-4-5-20251001",  // cheapest/fastest; swap to "claude-sonnet-4-6" for sharper reads
  "change_threshold": 8.0,     // LOWER = more sensitive (triggers on subtle changes); HIGHER = only big changes
  "poll_interval_seconds": 3.0,// how often to check the screen (seconds)
  "min_seconds_between_auto_calls": 15.0, // minimum gap between AI auto-observations
  "voice_enabled": false,      // set to true for text-to-speech (pyttsx3 must be installed)
  "hotkey": "<ctrl>+<shift>+g",// global hotkey to show/hide the overlay
  "game_name": "Warhammer 40000: Rogue Trader", // injected into the AI system prompt
  "max_history_messages": 16,  // how many recent turns to keep in memory
  "capture_scale": 0.25        // fraction of screen size used for change-detection (smaller = faster)
}
```

**For Rogue Trader specifically:**  
- Keep `change_threshold` at 8–12 (the game has a lot of idle animation)
- `poll_interval_seconds: 3` is fine for turn-based
- `min_seconds_between_auto_calls: 20` prevents it from pinging Claude every single turn

---

## Running from source

With the virtual environment activated:

```powershell
python main.py
```

Or double-click **`run.bat`** (it activates the environment and starts the app).

---

## Building a standalone .exe (no Python needed on the target PC)

```powershell
# Make sure you're in the gaming-overlay folder with .venv active
build.bat
```

This runs PyInstaller and produces `dist\GamingOverlay.exe`.

**To distribute / run on another PC:**
1. Copy `dist\GamingOverlay.exe` and `config.json` into the same folder.
2. Set `ANTHROPIC_API_KEY` on the target PC (same `setx` command above).
3. Double-click `GamingOverlay.exe`.

> Note: PySide6 bundled .exe files are large (~60–120 MB) — this is normal.

---

## Using the overlay

| Thing | How |
|---|---|
| **Move it** | Click and drag anywhere on the dark panel |
| **Show / hide** | `Ctrl+Shift+G` (or your configured hotkey) |
| **Ask a question** | Type in the chat box at the bottom → Enter or → |
| **Collapse chat** | Click the small "▼ Chat" / "▶ Chat" toggle |
| **Thinking indicator** | The green dot turns amber while Claude is working |
| **Close** | Click the ✕ button |

The AI will proactively comment when the screen changes meaningfully. During idle moments or in-engine cinematics it stays silent.

---

## Optional: voice output

1. Uncomment `pyttsx3>=2.90` in `requirements.txt`
2. `pip install pyttsx3`
3. Set `"voice_enabled": true` in `config.json`

No microphone / speech-to-text is included in this build (marked as a stretch goal).

---

## Global hotkey and admin rights

`pynput` (used for the hotkey) works without admin rights for most games. Some games with kernel-level anti-cheat (Easy Anti-Cheat, BattlEye) may block it. In that case, right-click `run.bat` or `GamingOverlay.exe` → **Run as Administrator**. Never run as admin unless you actually need to.

---

## Project structure

```
gaming-overlay/
├── main.py              # Entry point — wires everything together
├── config.json          # All user-tweakable settings
├── requirements.txt     # Python dependencies
├── run.bat              # One-click launcher
├── build.bat            # PyInstaller build script
└── src/
    ├── config.py        # Config loader (handles both source and frozen .exe)
    ├── signals.py       # Qt signals hub shared across threads
    ├── capture.py       # Screen capture + change-detection thread
    ├── ai_worker.py     # Serialized Claude API worker thread
    ├── overlay.py       # PySide6 overlay window
    ├── voice.py         # Optional TTS (pyttsx3)
    └── hotkey.py        # Global hotkey listener (pynput)
```

---

## Troubleshooting

**"ANTHROPIC_API_KEY is not set"** — Run the `setx` command, then **open a new terminal**.

**Overlay doesn't appear over the game** — Switch the game to Borderless Windowed mode.

**The overlay is too chatty / too quiet** — Adjust `change_threshold` (higher = less sensitive) and `min_seconds_between_auto_calls` (higher = longer quiet periods).

**Web search isn't working** — Enable it in the Anthropic Console under API → Integrations. Also make sure your account has credits.

**PyInstaller build fails on PySide6** — Make sure you're running `build.bat` with the virtual environment active. Some AV software blocks PyInstaller; temporarily disable it during the build.

**Hotkey doesn't work** — Try running as Administrator. Check that `pynput` is installed (`pip show pynput`). Change the hotkey combo in `config.json` if there's a conflict with the game.
