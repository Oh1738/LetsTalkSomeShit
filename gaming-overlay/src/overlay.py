"""
PySide6 overlay — Warhammer 40K Imperial theme.
Scrollable conversation log, no thought-process text, gothic aesthetic.
"""
import threading
from typing import Callable

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFrame, QSizePolicy, QTextEdit,
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush


# ── Imperial palette ──────────────────────────────────────────────────────────
BG          = "rgba(7, 4, 2, 245)"
BG_FIELD    = "rgba(14, 9, 4, 230)"
GOLD        = "#c9972a"
GOLD_DIM    = "#6b4f18"
PARCHMENT   = "#e8dcc8"
PARCHMENT_D = "#9a8878"
CRIMSON     = "#7a1515"
ERR_TEXT    = "#d97070"
FONT        = "'Palatino Linotype', 'Book Antiqua', Georgia, serif"


# ── Decorative frame with corner ornaments ────────────────────────────────────

class ImperialFrame(QFrame):
    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(GOLD), 1)
        p.setPen(pen)
        L = 14          # corner arm length
        w = self.width() - 1
        h = self.height() - 1
        for x0, x1, y0, y1 in (
            (0, L,   0, 0),   (0, 0,   0, L),    # top-left
            (w-L, w, 0, 0),   (w, w,   0, L),    # top-right
            (0, L,   h, h),   (0, 0,   h-L, h),  # bottom-left
            (w-L, w, h, h),   (w, w,   h-L, h),  # bottom-right
        ):
            p.drawLine(x0, y0, x1, y1)


# ── Avatar ────────────────────────────────────────────────────────────────────

class AvatarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(46, 46)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Outer ring
        p.setPen(QPen(QColor(GOLD_DIM), 1))
        p.setBrush(QBrush(QColor("#070402")))
        p.drawEllipse(1, 1, 44, 44)
        # Inner ring
        p.setPen(QPen(QColor(GOLD), 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(6, 6, 34, 34)
        # Aquila cross
        f = QFont("Palatino Linotype", 17, QFont.Weight.Bold)
        p.setFont(f)
        p.setPen(QColor(GOLD))
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "✠")


# ── Main Overlay Window ───────────────────────────────────────────────────────

class OverlayWindow(QWidget):
    def __init__(self, config, signals, ai_worker, capture_fn: Callable):
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

    def _init_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumWidth(330)
        self.setMaximumWidth(430)
        from PySide6.QtWidgets import QApplication
        g = QApplication.primaryScreen().availableGeometry()
        self.move(g.right() - 450, g.top() + 30)

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)
        outer.setSpacing(0)

        self._frame = ImperialFrame()
        self._frame.setStyleSheet(
            f"ImperialFrame {{"
            f"  background-color: {BG};"
            f"  border: 1px solid {GOLD_DIM};"
            f"  border-radius: 2px;"
            f"}}"
        )
        outer.addWidget(self._frame)

        inner = QVBoxLayout(self._frame)
        inner.setContentsMargins(12, 10, 12, 12)
        inner.setSpacing(0)

        inner.addLayout(self._build_header())
        inner.addWidget(self._divider(GOLD_DIM))
        inner.addSpacing(6)
        inner.addWidget(self._build_log())
        inner.addSpacing(6)
        inner.addWidget(self._divider(GOLD_DIM))
        inner.addWidget(self._build_chat_toggle())
        inner.addWidget(self._build_chat_panel())

    def _divider(self, color: str) -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.Shape.HLine)
        f.setFixedHeight(1)
        f.setStyleSheet(f"background: {color}; border: none;")
        return f

    def _build_header(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        row.setContentsMargins(0, 0, 0, 8)

        self._avatar = AvatarWidget()
        row.addWidget(self._avatar)

        col = QVBoxLayout()
        col.setSpacing(1)
        t1 = QLabel("IMPERIAL COGITATOR")
        t1.setStyleSheet(
            f"color: {GOLD}; font-family: {FONT};"
            f"font-size: 11px; font-weight: bold; letter-spacing: 2px;"
        )
        t2 = QLabel(self._cfg.get("game_name", "").upper())
        t2.setStyleSheet(
            f"color: {GOLD_DIM}; font-family: {FONT};"
            f"font-size: 9px; letter-spacing: 1px;"
        )
        col.addWidget(t1)
        col.addWidget(t2)
        row.addLayout(col, 1)

        self._dot = QLabel("●")
        self._dot.setStyleSheet(f"color: {GOLD}; font-size: 9px;")
        row.addWidget(self._dot)

        for lbl, slot, hover in (
            ("—", self.showMinimized, PARCHMENT_D),
            ("✕", self.close, "#e07070"),
        ):
            b = QPushButton(lbl)
            b.setFixedSize(20, 20)
            b.setStyleSheet(
                f"QPushButton {{ color: {GOLD_DIM}; background: transparent; border: none; font-size: 12px; }}"
                f"QPushButton:hover {{ color: {hover}; }}"
            )
            b.clicked.connect(slot)
            row.addWidget(b)

        return row

    def _build_log(self) -> QTextEdit:
        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setFixedHeight(240)
        self._log.setStyleSheet(
            f"QTextEdit {{"
            f"  background-color: {BG_FIELD};"
            f"  border: 1px solid {GOLD_DIM};"
            f"  color: {PARCHMENT};"
            f"  font-family: {FONT};"
            f"  font-size: 14px;"
            f"  padding: 6px 8px;"
            f"}}"
            f"QScrollBar:vertical {{"
            f"  background: {BG}; width: 8px; border: none;"
            f"}}"
            f"QScrollBar::handle:vertical {{"
            f"  background: {GOLD_DIM}; border-radius: 4px; min-height: 20px;"
            f"}}"
            f"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}"
        )
        self._log.setHtml(
            f'<p style="color:{GOLD_DIM}; font-size:11px; font-family:{FONT}; letter-spacing:1px;">'
            f'✠ &nbsp; FOR THE EMPEROR &nbsp; ✠</p>'
            f'<p style="color:{PARCHMENT_D}; font-size:13px; font-family:{FONT};">'
            f'Cogitator unit online. Watching for threats and opportunities…</p>'
        )
        return self._log

    def _build_chat_toggle(self) -> QPushButton:
        self._toggle_btn = QPushButton("▼  VOX CHANNEL")
        self._toggle_btn.setStyleSheet(
            f"QPushButton {{"
            f"  color: {GOLD_DIM}; background: transparent; border: none;"
            f"  font-family: {FONT}; font-size: 10px; letter-spacing: 2px;"
            f"  text-align: left; padding: 6px 0px 4px 0px;"
            f"}}"
            f"QPushButton:hover {{ color: {GOLD}; }}"
        )
        self._toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle_btn.clicked.connect(self._toggle_chat)
        return self._toggle_btn

    def _build_chat_panel(self) -> QWidget:
        self._chat_panel = QWidget()
        row = QHBoxLayout(self._chat_panel)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Issue a command, Rogue Trader…")
        self._input.setStyleSheet(
            f"QLineEdit {{"
            f"  background-color: {BG_FIELD};"
            f"  color: {PARCHMENT};"
            f"  border: 1px solid {GOLD_DIM};"
            f"  border-radius: 2px;"
            f"  padding: 6px 10px;"
            f"  font-family: {FONT};"
            f"  font-size: 14px;"
            f"}}"
            f"QLineEdit:focus {{ border-color: {GOLD}; }}"
            f"QLineEdit::placeholder {{ color: {PARCHMENT_D}; }}"
        )
        self._input.returnPressed.connect(self._send)
        row.addWidget(self._input, 1)

        send_btn = QPushButton("⚔")
        send_btn.setFixedSize(34, 34)
        send_btn.setStyleSheet(
            f"QPushButton {{"
            f"  background-color: {BG_FIELD};"
            f"  color: {GOLD};"
            f"  border: 1px solid {GOLD_DIM};"
            f"  border-radius: 2px;"
            f"  font-size: 16px;"
            f"}}"
            f"QPushButton:hover {{ border-color: {GOLD}; background: rgba(60,38,8,200); }}"
        )
        send_btn.clicked.connect(self._send)
        row.addWidget(send_btn)

        return self._chat_panel

    # ── signals ───────────────────────────────────────────────────────────────

    def _connect_signals(self):
        self._signals.message_ready.connect(self._on_message)
        self._signals.error_occurred.connect(self._on_error)
        self._signals.thinking_start.connect(self._on_thinking_start)
        self._signals.thinking_stop.connect(self._on_thinking_stop)

    # ── slots ─────────────────────────────────────────────────────────────────

    def _on_message(self, text: str):
        self._append_to_log("cogitator", text)
        if self._cfg.get("voice_enabled", False):
            from src.voice import speak
            threading.Thread(target=speak, args=(text,), daemon=True).start()

    def _on_error(self, text: str):
        self._append_to_log("error", text)

    def _on_thinking_start(self):
        self._dot.setStyleSheet("color: #c9972a; font-size: 9px;")
        self._dot.setToolTip("Consulting the archives…")

    def _on_thinking_stop(self):
        self._dot.setStyleSheet(f"color: {GOLD}; font-size: 9px;")
        self._dot.setToolTip("Watching")

    # ── chat ──────────────────────────────────────────────────────────────────

    def _send(self):
        text = self._input.text().strip()
        if not text:
            return
        self._input.clear()
        self._append_to_log("player", text)
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
            "▼  VOX CHANNEL" if self._chat_visible else "▶  VOX CHANNEL"
        )
        self.adjustSize()

    # ── log helper ─────────────────────────────────────────────────────────────

    def _append_to_log(self, role: str, text: str):
        cursor = self._log.textCursor()
        from PySide6.QtGui import QTextCursor
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._log.setTextCursor(cursor)

        if role == "cogitator":
            label_color = GOLD
            label = "✠  COGITATOR"
            text_color = PARCHMENT
        elif role == "player":
            label_color = GOLD_DIM
            label = "◈  YOU"
            text_color = PARCHMENT_D
        else:  # error
            label_color = CRIMSON
            label = "⚠  ALERT"
            text_color = ERR_TEXT

        html = (
            f'<p style="margin:8px 0 2px 0; color:{label_color}; '
            f'font-size:10px; font-family:{FONT}; letter-spacing:1px;">'
            f'{label}</p>'
            f'<p style="margin:0 0 4px 0; color:{text_color}; '
            f'font-size:14px; font-family:{FONT}; line-height:1.5;">'
            f'{text.replace(chr(10), "<br>")}</p>'
        )
        self._log.insertHtml(html)
        # Scroll to bottom
        sb = self._log.verticalScrollBar()
        sb.setValue(sb.maximum())

    # ── drag ──────────────────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, _event):
        self._drag_pos = None

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()
