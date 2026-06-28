"""
PySide6 overlay window: frameless, translucent, always-on-top, draggable.
ALL widget updates happen in slots connected to AppSignals — never from worker threads.
"""
import threading
from typing import Callable

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFrame, QSizePolicy, QTextEdit,
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush


# ── Avatar ────────────────────────────────────────────────────────────────────

class AvatarWidget(QWidget):
    """Painted circle avatar — no external image files needed."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(46, 46)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Background circle
        p.setPen(QPen(QColor("#4ade80"), 2))
        p.setBrush(QBrush(QColor("#0f172a")))
        p.drawEllipse(2, 2, 42, 42)
        # "AI" label
        font = QFont("Segoe UI", 13, QFont.Weight.Bold)
        p.setFont(font)
        p.setPen(QColor("#4ade80"))
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "AI")


# ── Main Overlay Window ───────────────────────────────────────────────────────

class OverlayWindow(QWidget):
    def __init__(
        self,
        config: dict,
        signals,
        ai_worker,
        capture_fn: Callable[[], str | None],
    ):
        super().__init__()
        self._cfg = config
        self._signals = signals
        self._ai_worker = ai_worker
        self._capture_fn = capture_fn

        self._drag_pos: QPoint | None = None
        self._chat_visible = True

        self._init_window()
        self._build_ui()
        self._connect_signals()

    # ── window setup ──────────────────────────────────────────────────────────

    def _init_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool          # keeps overlay out of the taskbar
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumWidth(300)
        self.setMaximumWidth(380)

        # Default position: top-right of the primary screen
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.right() - 380, screen.top() + 30)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # Outer layout is transparent; only the inner frame is visible
        outer = QVBoxLayout(self)
        outer.setContentsMargins(6, 6, 6, 6)
        outer.setSpacing(0)

        self._frame = QFrame()
        self._frame.setObjectName("main_frame")
        self._frame.setStyleSheet(
            "QFrame#main_frame {"
            "  background-color: rgba(13, 17, 35, 218);"
            "  border: 1px solid #1e3a5f;"
            "  border-radius: 12px;"
            "}"
        )
        outer.addWidget(self._frame)

        layout = QVBoxLayout(self._frame)
        layout.setContentsMargins(10, 8, 10, 10)
        layout.setSpacing(8)

        layout.addLayout(self._build_header())
        layout.addWidget(self._build_bubble())
        layout.addWidget(self._build_chat_toggle())
        layout.addWidget(self._build_chat_panel())

    def _build_header(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(6)

        self._avatar = AvatarWidget()
        row.addWidget(self._avatar)

        title = QLabel(f"Gaming Co-Pilot")
        title.setStyleSheet(
            "color: #64748b; font-size: 11px; font-family: 'Segoe UI';"
        )
        row.addWidget(title, 1)

        self._dot = QLabel("●")
        self._dot.setStyleSheet("color: #4ade80; font-size: 9px; padding-right: 2px;")
        self._dot.setToolTip("Watching")
        row.addWidget(self._dot)

        for label, slot, color in (
            ("_",  self.showMinimized, "#64748b"),
            ("✕",  self.close,         "#ef4444"),
        ):
            btn = QPushButton(label)
            btn.setFixedSize(20, 20)
            btn.setStyleSheet(
                f"QPushButton {{ color: #475569; background: transparent; border: none;"
                f"  font-size: 11px; border-radius: 3px; }}"
                f"QPushButton:hover {{ color: {color}; background: rgba(255,255,255,15); }}"
            )
            btn.clicked.connect(slot)
            row.addWidget(btn)

        return row

    def _build_bubble(self) -> QTextEdit:
        self._bubble = QTextEdit()
        self._bubble.setReadOnly(True)
        self._bubble.setFixedHeight(150)
        self._bubble.setPlainText("Watching your game…")
        self._bubble.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self._bubble.setStyleSheet(
            "QTextEdit {"
            "  color: #e2e8f0;"
            "  background-color: rgba(8, 12, 28, 200);"
            "  border: 1px solid #2d4a6e;"
            "  border-radius: 8px;"
            "  padding: 7px 9px;"
            "  font-family: 'Segoe UI', sans-serif;"
            "  font-size: 12px;"
            "  line-height: 1.4;"
            "}"
            "QScrollBar:vertical { width: 0px; }"
        )
        return self._bubble

    def _build_chat_toggle(self) -> QPushButton:
        self._toggle_btn = QPushButton("▼  Chat")
        self._toggle_btn.setStyleSheet(
            "QPushButton { color: #475569; background: transparent; border: none;"
            "  font-size: 10px; text-align: left; padding: 0px 2px; }"
            "QPushButton:hover { color: #94a3b8; }"
        )
        self._toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle_btn.clicked.connect(self._toggle_chat)
        return self._toggle_btn

    def _build_chat_panel(self) -> QWidget:
        self._chat_panel = QWidget()
        row = QHBoxLayout(self._chat_panel)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(5)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Ask anything about the game…")
        self._input.setStyleSheet(
            "QLineEdit {"
            "  background-color: rgba(8, 12, 28, 200);"
            "  color: #e2e8f0;"
            "  border: 1px solid #2d4a6e;"
            "  border-radius: 6px;"
            "  padding: 5px 8px;"
            "  font-family: 'Segoe UI', sans-serif;"
            "  font-size: 12px;"
            "}"
            "QLineEdit:focus { border-color: #4ade80; }"
        )
        self._input.returnPressed.connect(self._send)
        row.addWidget(self._input, 1)

        send_btn = QPushButton("→")
        send_btn.setFixedSize(30, 30)
        send_btn.setStyleSheet(
            "QPushButton {"
            "  background-color: #1a6b3c;"
            "  color: #4ade80;"
            "  border: 1px solid #4ade80;"
            "  border-radius: 6px;"
            "  font-size: 14px;"
            "  font-weight: bold;"
            "}"
            "QPushButton:hover { background-color: #22543d; }"
            "QPushButton:pressed { background-color: #166534; }"
        )
        send_btn.clicked.connect(self._send)
        row.addWidget(send_btn)

        return self._chat_panel

    # ── signal connections ─────────────────────────────────────────────────────

    def _connect_signals(self):
        self._signals.message_ready.connect(self._on_message)
        self._signals.error_occurred.connect(self._on_error)
        self._signals.thinking_start.connect(self._on_thinking_start)
        self._signals.thinking_stop.connect(self._on_thinking_stop)

    # ── slots (always called in main Qt thread) ────────────────────────────────

    def _on_message(self, text: str):
        self._bubble.setStyleSheet(
            "QTextEdit {"
            "  color: #e2e8f0;"
            "  background-color: rgba(8, 12, 28, 200);"
            "  border: 1px solid #4ade80;"
            "  border-radius: 8px;"
            "  padding: 7px 9px;"
            "  font-family: 'Segoe UI', sans-serif;"
            "  font-size: 12px;"
            "}"
            "QScrollBar:vertical { width: 0px; }"
        )
        self._bubble.setPlainText(text)
        self._bubble.verticalScrollBar().setValue(0)

        if self._cfg.get("voice_enabled", False):
            from src.voice import speak
            threading.Thread(target=speak, args=(text,), daemon=True).start()

    def _on_error(self, text: str):
        self._bubble.setStyleSheet(
            "QTextEdit {"
            "  color: #fca5a5;"
            "  background-color: rgba(28, 8, 8, 200);"
            "  border: 1px solid #ef4444;"
            "  border-radius: 8px;"
            "  padding: 7px 9px;"
            "  font-family: 'Segoe UI', sans-serif;"
            "  font-size: 12px;"
            "}"
            "QScrollBar:vertical { width: 0px; }"
        )
        self._bubble.setPlainText(text)

    def _on_thinking_start(self):
        self._dot.setStyleSheet("color: #f59e0b; font-size: 9px; padding-right: 2px;")
        self._dot.setToolTip("Thinking…")

    def _on_thinking_stop(self):
        self._dot.setStyleSheet("color: #4ade80; font-size: 9px; padding-right: 2px;")
        self._dot.setToolTip("Watching")

    # ── chat ──────────────────────────────────────────────────────────────────

    def _send(self):
        text = self._input.text().strip()
        if not text:
            return
        self._input.clear()
        self._bubble.setPlainText(f"You: {text}\n\n⏳ Thinking…")
        b64 = None
        try:
            b64 = self._capture_fn()
        except Exception:
            pass
        self._ai_worker.submit_user(text, b64)

    def _toggle_chat(self):
        self._chat_visible = not self._chat_visible
        self._chat_panel.setVisible(self._chat_visible)
        self._toggle_btn.setText("▼  Chat" if self._chat_visible else "▶  Chat")
        self.adjustSize()

    # ── drag support ──────────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and (
            event.buttons() & Qt.MouseButton.LeftButton
        ):
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, _event):
        self._drag_pos = None

    # ── public ────────────────────────────────────────────────────────────────

    def toggle_visibility(self):
        """Toggle called from hotkey (safe to call from any thread via Qt's queued connection)."""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()
