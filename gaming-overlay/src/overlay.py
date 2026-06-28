"""
PySide6 overlay window — Warhammer 40K Imperial gothic theme.
Frameless, translucent, always-on-top, draggable.
ALL widget updates happen in slots connected to AppSignals — never from worker threads.
"""
import threading
from typing import Callable

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFrame, QSizePolicy, QTextEdit,
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QLinearGradient


# ── Warhammer 40K Imperial colour palette ────────────────────────────────────
BG           = "rgba(10, 7, 4, 235)"
BG_INPUT     = "rgba(18, 12, 6, 220)"
BORDER       = "#7a5c1e"          # aged brass
BORDER_LIVE  = "#c9972a"          # bright gold — active/response state
BORDER_ERR   = "#6b1a1a"          # dark crimson
TEXT         = "#e8dcc8"          # parchment
TEXT_DIM     = "#7a6a56"
TEXT_ERR     = "#e07070"
ACCENT       = "#c9972a"          # gold accent
FONT_MAIN    = "'Palatino Linotype', 'Palatino', 'Book Antiqua', Georgia, serif"
FONT_SIZE    = "14px"


# ── Avatar ────────────────────────────────────────────────────────────────────

class AvatarWidget(QWidget):
    """Painted imperial seal avatar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(48, 48)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Outer ring — dark brass
        p.setPen(QPen(QColor("#7a5c1e"), 1))
        p.setBrush(QBrush(QColor("#0a0704")))
        p.drawEllipse(2, 2, 44, 44)

        # Inner ring — bright gold
        p.setPen(QPen(QColor("#c9972a"), 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(6, 6, 36, 36)

        # Aquila cross symbol
        font = QFont("Palatino Linotype", 18, QFont.Weight.Bold)
        p.setFont(font)
        p.setPen(QColor("#c9972a"))
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "✠")


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
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumWidth(320)
        self.setMaximumWidth(420)

        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.right() - 440, screen.top() + 30)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(6, 6, 6, 6)
        outer.setSpacing(0)

        self._frame = QFrame()
        self._frame.setObjectName("main_frame")
        self._frame.setStyleSheet(
            f"QFrame#main_frame {{"
            f"  background-color: {BG};"
            f"  border: 1px solid {BORDER};"
            f"  border-radius: 4px;"
            f"}}"
        )
        outer.addWidget(self._frame)

        layout = QVBoxLayout(self._frame)
        layout.setContentsMargins(10, 8, 10, 10)
        layout.setSpacing(8)

        layout.addLayout(self._build_header())
        layout.addWidget(self._build_divider())
        layout.addWidget(self._build_bubble())
        layout.addWidget(self._build_chat_toggle())
        layout.addWidget(self._build_chat_panel())

    def _build_header(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)

        self._avatar = AvatarWidget()
        row.addWidget(self._avatar)

        title = QLabel("IMPERIAL CO-PILOT")
        title.setStyleSheet(
            f"color: {ACCENT};"
            f"font-size: 11px;"
            f"font-family: {FONT_MAIN};"
            f"letter-spacing: 2px;"
            f"font-weight: bold;"
        )
        row.addWidget(title, 1)

        self._dot = QLabel("●")
        self._dot.setStyleSheet(f"color: {ACCENT}; font-size: 9px; padding-right: 2px;")
        self._dot.setToolTip("Watching")
        row.addWidget(self._dot)

        for label, slot, hover in (
            ("—", self.showMinimized, TEXT_DIM),
            ("✕", self.close,         "#e07070"),
        ):
            btn = QPushButton(label)
            btn.setFixedSize(20, 20)
            btn.setStyleSheet(
                f"QPushButton {{ color: {TEXT_DIM}; background: transparent; border: none;"
                f"  font-size: 12px; border-radius: 2px; }}"
                f"QPushButton:hover {{ color: {hover}; background: rgba(255,255,255,10); }}"
            )
            btn.clicked.connect(slot)
            row.addWidget(btn)

        return row

    def _build_divider(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFixedHeight(1)
        line.setStyleSheet(f"background-color: {BORDER}; border: none;")
        return line

    def _build_bubble(self) -> QTextEdit:
        self._bubble = QTextEdit()
        self._bubble.setReadOnly(True)
        self._bubble.setFixedHeight(180)
        self._bubble.setPlainText("FOR THE EMPEROR.\n\nWatching your screen…")
        self._bubble.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self._bubble.setStyleSheet(self._bubble_style(BORDER))
        return self._bubble

    def _build_chat_toggle(self) -> QPushButton:
        self._toggle_btn = QPushButton("▼  Vox Channel")
        self._toggle_btn.setStyleSheet(
            f"QPushButton {{ color: {TEXT_DIM}; background: transparent; border: none;"
            f"  font-size: 10px; font-family: {FONT_MAIN}; letter-spacing: 1px;"
            f"  text-align: left; padding: 0px 2px; }}"
            f"QPushButton:hover {{ color: {ACCENT}; }}"
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
        self._input.setPlaceholderText("Speak, Rogue Trader…")
        self._input.setStyleSheet(
            f"QLineEdit {{"
            f"  background-color: {BG_INPUT};"
            f"  color: {TEXT};"
            f"  border: 1px solid {BORDER};"
            f"  border-radius: 3px;"
            f"  padding: 6px 10px;"
            f"  font-family: {FONT_MAIN};"
            f"  font-size: {FONT_SIZE};"
            f"}}"
            f"QLineEdit:focus {{ border-color: {ACCENT}; }}"
        )
        self._input.returnPressed.connect(self._send)
        row.addWidget(self._input, 1)

        send_btn = QPushButton("⚔")
        send_btn.setFixedSize(34, 34)
        send_btn.setStyleSheet(
            f"QPushButton {{"
            f"  background-color: rgba(30, 20, 5, 200);"
            f"  color: {ACCENT};"
            f"  border: 1px solid {BORDER};"
            f"  border-radius: 3px;"
            f"  font-size: 16px;"
            f"}}"
            f"QPushButton:hover {{ border-color: {ACCENT}; background: rgba(60, 40, 10, 200); }}"
            f"QPushButton:pressed {{ background: rgba(20, 13, 3, 200); }}"
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

    # ── slots ──────────────────────────────────────────────────────────────────

    def _on_message(self, text: str):
        self._bubble.setStyleSheet(self._bubble_style(BORDER_LIVE))
        self._bubble.setPlainText(text)
        self._bubble.verticalScrollBar().setValue(0)

        if self._cfg.get("voice_enabled", False):
            from src.voice import speak
            threading.Thread(target=speak, args=(text,), daemon=True).start()

    def _on_error(self, text: str):
        self._bubble.setStyleSheet(self._bubble_style(BORDER_ERR, TEXT_ERR))
        self._bubble.setPlainText(text)

    def _on_thinking_start(self):
        self._dot.setStyleSheet("color: #c9972a; font-size: 9px; padding-right: 2px;")
        self._dot.setToolTip("Consulting the cogitators…")

    def _on_thinking_stop(self):
        self._dot.setStyleSheet(f"color: {ACCENT}; font-size: 9px; padding-right: 2px;")
        self._dot.setToolTip("Watching")

    # ── chat ──────────────────────────────────────────────────────────────────

    def _send(self):
        text = self._input.text().strip()
        if not text:
            return
        self._input.clear()
        self._bubble.setStyleSheet(self._bubble_style(BORDER))
        self._bubble.setPlainText(f"You: {text}\n\n⏳ Consulting the archives…")
        b64 = None
        try:
            b64 = self._capture_fn()
        except Exception:
            pass
        self._ai_worker.submit_user(text, b64)

    def _toggle_chat(self):
        self._chat_visible = not self._chat_visible
        self._chat_panel.setVisible(self._chat_visible)
        self._toggle_btn.setText(
            "▼  Vox Channel" if self._chat_visible else "▶  Vox Channel"
        )
        self.adjustSize()

    # ── drag ──────────────────────────────────────────────────────────────────

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
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()

    # ── helpers ───────────────────────────────────────────────────────────────

    def _bubble_style(self, border_color: str, text_color: str = TEXT) -> str:
        return (
            f"QTextEdit {{"
            f"  color: {text_color};"
            f"  background-color: {BG_INPUT};"
            f"  border: 1px solid {border_color};"
            f"  border-radius: 3px;"
            f"  padding: 8px 10px;"
            f"  font-family: {FONT_MAIN};"
            f"  font-size: {FONT_SIZE};"
            f"  line-height: 1.5;"
            f"}}"
            f"QScrollBar:vertical {{ width: 0px; }}"
        )
