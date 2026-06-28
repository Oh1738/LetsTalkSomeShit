"""
Single serialized worker thread for all Claude API calls.
All auto-watch and user-chat requests flow through one queue so the shared
conversation history is never touched by two threads simultaneously.
"""
import os
import queue
import threading
from typing import Any

import anthropic


SYSTEM_PROMPT = """\
You are a sharp, no-nonsense gaming co-pilot watching the player's screen.
Game: {game_name}

RULES — follow these exactly:
1. Be concise: 2-4 sentences for auto observations, up to a short paragraph for direct questions.
2. Give specific, actionable advice based ONLY on what is visible. Never invent game state.
3. If you cannot see something clearly, say so directly. Do not guess.
4. For questions about quest progression, "where do I go next", builds, lore, or anything
   not visible on screen: USE the web_search tool to find accurate info from wikis/guides.
   Only search when genuinely needed — not for things you can already see.
5. No padding, no "Great question!", no repeating "I can see...". Just give the tip.
6. AUTO-WATCH ONLY: if nothing notable or actionable is on screen, respond with exactly: <SILENT>
"""


class AIWorker(threading.Thread):
    """Queue-backed worker; all API calls serialize through this single thread."""

    def __init__(self, config: dict, signals) -> None:
        super().__init__(daemon=True, name="AIWorker")
        self._cfg = config
        self._signals = signals
        self._q: queue.Queue = queue.Queue()
        self._history: list[dict] = []
        self._stop = threading.Event()

        api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            signals.error_occurred.emit(
                "ANTHROPIC_API_KEY is not set.\n\n"
                "Fix: open PowerShell and run:\n"
                '  setx ANTHROPIC_API_KEY "sk-ant-..."\n'
                "Then close this window and relaunch."
            )
            self._client: anthropic.Anthropic | None = None
        else:
            self._client = anthropic.Anthropic(api_key=api_key)

    # ── public API ──────────────────────────────────────────────────────────

    def submit_watch(self, b64_image: str) -> None:
        if not self._stop.is_set():
            self._q.put_nowait({"type": "watch", "image": b64_image})

    def submit_user(self, text: str, b64_image: str | None = None) -> None:
        if not self._stop.is_set():
            self._q.put_nowait({"type": "user", "text": text, "image": b64_image})

    def stop(self) -> None:
        self._stop.set()
        self._q.put_nowait(None)  # unblock blocking get()

    # ── thread loop ─────────────────────────────────────────────────────────

    def run(self) -> None:
        while not self._stop.is_set():
            try:
                item = self._q.get(timeout=1.0)
            except queue.Empty:
                continue
            if item is None:
                break
            try:
                if item["type"] == "watch":
                    self._handle_watch(item["image"])
                elif item["type"] == "user":
                    self._handle_user(item["text"], item.get("image"))
            except Exception as e:
                self._signals.error_occurred.emit(f"Worker error: {e}")
            finally:
                try:
                    self._q.task_done()
                except ValueError:
                    pass

    # ── handlers ────────────────────────────────────────────────────────────

    def _handle_watch(self, b64: str) -> None:
        if not self._client:
            return
        self._signals.thinking_start.emit()
        try:
            user_content = [
                _img_block(b64),
                {
                    "type": "text",
                    "text": (
                        "Observe the screen. If you spot something notable, urgent, or actionable "
                        "(enemy position, loot, quest update, UI alert, stat change, etc.) give a "
                        "brief concrete tip. If nothing notable is happening, respond with exactly: "
                        "<SILENT>"
                    ),
                },
            ]
            self._push("user", user_content)
            text = self._call_api(use_search=False)
            self._push("assistant", [{"type": "text", "text": text}])
            self._prune()

            if text and text.strip() not in ("", "<SILENT>"):
                self._signals.message_ready.emit(text.strip())
        finally:
            self._signals.thinking_stop.emit()

    def _handle_user(self, question: str, b64: str | None) -> None:
        if not self._client:
            return
        self._signals.thinking_start.emit()
        try:
            user_content: list = []
            if b64:
                user_content.append(_img_block(b64))
            user_content.append({"type": "text", "text": question})
            self._push("user", user_content)
            text = self._call_api(use_search=True)
            self._push("assistant", [{"type": "text", "text": text}])
            self._prune()
            if text:
                self._signals.message_ready.emit(text.strip())
        finally:
            self._signals.thinking_stop.emit()

    # ── API machinery ────────────────────────────────────────────────────────

    def _call_api(
        self,
        use_search: bool,
        messages: list | None = None,
    ) -> str:
        if messages is None:
            messages = self._stripped_messages()

        system = SYSTEM_PROMPT.format(game_name=self._cfg["game_name"])
        base: dict[str, Any] = dict(
            model=self._cfg["model"],
            max_tokens=1500 if use_search else 512,
            system=system,
            messages=messages,
        )

        if use_search:
            resp = self._call_with_search(base)
        else:
            resp = self._client.messages.create(**base)  # type: ignore[union-attr]

        return self._extract_and_continue(resp, use_search, messages)

    def _call_with_search(self, base_kwargs: dict) -> Any:
        """Try the newer web-search tool version, fall back to the older one on error."""
        for version in ("web_search_20260209", "web_search_20250305"):
            kw = dict(base_kwargs, tools=[{"type": version, "name": "web_search"}])
            try:
                return self._client.messages.create(**kw)  # type: ignore[union-attr]
            except (anthropic.BadRequestError, anthropic.APIStatusError) as exc:
                if version == "web_search_20250305":
                    raise  # both versions failed — let it propagate
                print(f"[ai] {version} rejected ({exc}), trying fallback…")
        # Unreachable, but satisfies type checker
        return self._client.messages.create(**base_kwargs)  # type: ignore[union-attr]

    def _extract_and_continue(
        self,
        resp: Any,
        use_search: bool,
        messages: list,
        depth: int = 0,
    ) -> str:
        if depth > 6:
            return "[Search took too long — please try again]"

        texts: list[str] = []
        for block in resp.content:
            btype = getattr(block, "type", "")
            if btype == "text":
                texts.append(block.text)
            # Intentionally skip: tool_use, web_search_tool_result, etc.

        if resp.stop_reason == "pause_turn":
            # Server-side tool still running — append partial response and continue
            system = SYSTEM_PROMPT.format(game_name=self._cfg["model"])
            new_msgs = messages + [
                {"role": "assistant", "content": _blocks_to_dicts(resp.content)}
            ]
            kw: dict[str, Any] = dict(
                model=self._cfg["model"],
                max_tokens=1500,
                system=SYSTEM_PROMPT.format(game_name=self._cfg["game_name"]),
                messages=new_msgs,
            )
            if use_search:
                # Keep the tool available for follow-up searches
                kw["tools"] = [{"type": "web_search_20260209", "name": "web_search"}]
            cont = self._client.messages.create(**kw)  # type: ignore[union-attr]
            return self._extract_and_continue(cont, use_search, new_msgs, depth + 1)

        return " ".join(t for t in texts if t).strip()

    # ── history helpers ──────────────────────────────────────────────────────

    def _push(self, role: str, content: list) -> None:
        self._history.append({"role": role, "content": content})

    def _prune(self) -> None:
        max_msgs = int(self._cfg.get("max_history_messages", 16))
        if len(self._history) > max_msgs:
            self._history = self._history[-max_msgs:]

    def _stripped_messages(self) -> list:
        """Return history with screenshots removed from all but the latest user turn."""
        last_user_idx = -1
        for i, m in enumerate(self._history):
            if m["role"] == "user":
                last_user_idx = i

        result = []
        for i, m in enumerate(self._history):
            if m["role"] == "user" and i != last_user_idx:
                stripped = []
                for block in m["content"]:
                    if isinstance(block, dict) and block.get("type") == "image":
                        stripped.append(
                            {"type": "text", "text": "[earlier screenshot — omitted to save tokens]"}
                        )
                    else:
                        stripped.append(block)
                result.append({"role": "user", "content": stripped})
            else:
                result.append(dict(m))
        return result


# ── helpers ──────────────────────────────────────────────────────────────────

def _img_block(b64: str) -> dict:
    return {
        "type": "image",
        "source": {"type": "base64", "media_type": "image/jpeg", "data": b64},
    }


def _blocks_to_dicts(blocks) -> list:
    result = []
    for b in blocks:
        if hasattr(b, "model_dump"):
            result.append(b.model_dump())
        elif isinstance(b, dict):
            result.append(b)
    return result
