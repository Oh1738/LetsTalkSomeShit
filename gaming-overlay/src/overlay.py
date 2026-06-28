"""
PySide6 overlay — Warhammer 40K: Rogue Trader UI match.
Black panels, red borders, gold trim, angular notched corners, large bold text.
"""
import threading
from typing import Callable

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QSizePolicy, QTextEdit,
)
from PySide6.QtCore import Qt, QPoint, QSize
from PySide6.QtGui import (
    QPainter, QColor, QFont, QPen, QBrush,
    QPolygon, QTextCursor,
)
from PySide6.QtCore import QPoint as Pt


# ── Rogue Trader colour palette ───────────────────────────────────────────────
BG          = "rgba(7, 4, 3, 252)"
BG_FIELD    = "rgba(4, 2, 1, 240)"
RED         = "#9b1010"      # border red
RED_LIT     = "#c41e1e"      # active/response border
GOLD        = "#c8a035"      # gold trim
GOLD_DIM    = "#6b5018"
WHITE       = "#f0ece0"      # main text
WHITE_DIM   = "#7a7060"      # secondary text
ERR         = "#d06060"
FONT        = "Georgia, 'Times New Roman', serif"
SZ          = "16px"
SZ_SM       = "11px"


# ── Frame with Rogue Trader–style notched corners ─────────────────────────────

class RTFrame(QWidget):
    """Dark panel with red border and 45° notched corners, gold inner line."""

    NOTCH = 10   # px cut from each corner

    def __init__(self, parent=None):
        super().__init__(parent)
        self._border_color = QColor(RED)

    def set_border(self, hex_color: str):
        self._border_color = QColor(hex_color)
        self.update()

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        N = self.NOTCH
        w, h = self.width() - 1, self.height() - 1

        # Fill
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor(7, 4, 3, 252)))
        poly = QPolygon([
            Pt(N, 0), Pt(w-N, 0),
            Pt(w, N), Pt(w, h-N),
            Pt(w-N, h), Pt(N, h),
            Pt(0, h-N), Pt(0, N),
        ])
        p.drawPolygon(poly)

        # Outer border — red
        pen = QPen(self._border_color, 1)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPolygon(poly)

        # Inner gold line — inset by 3px
        I = 3
        p.setPen(QPen(QColor(GOLD_DIM), 1))
        inner = QPolygon([
            Pt(N+I, I), Pt(w-N-I, I),
            Pt(w-I, N+I), Pt(w-I, h-N-I),
            Pt(w-N-I, h-I), Pt(N+I, h-I),
            Pt(I, h-N-I), Pt(I, N+I),
        ])
        p.drawPolygon(inner)

        # Corner accent ticks — gold
        p.setPen(QPen(QColor(GOLD), 1))
        for x, y in ((N, 0), (w-N, 0), (w, N), (w, h-N),
                     (w-N, h), (N, h), (0, h-N), (0, N)):
            p.drawPoint(x, y)


# ── Avatar ────────────────────────────────────────────────────────────────────

class AvatarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(44, 44)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Red outer circle
        p.setPen(QPen(QColor(RED_LIT), 1))
        p.setBrush(QBrush(QColor("#070403")))
        p.drawEllipse(1, 1, 42, 42)
        # Gold inner ring
        p.setPen(QPen(QColor(GOLD_DIM), 1))
        p.drawEllipse(5, 5, 34, 34)
        # Cross
        f = QFont("Georgia", 16, QFont.Weight.Bold)
        p.setFont(f)
        p.setPen(QColor(GOLD))
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "✠")


# ── Main Overlay ──────────────────────────────────────────────────────────────

class OverlayWindow(QWidget):
    def __init__(self, config, signals, ai_worker, capture_fn: Callable):
        super().__init__()
        self._cfg       = config
        self._signals   = signals
        self._ai_worker = ai_worker
        self._capture   = capture_fn
        self._drag_pos: QPoint | None = None
        self._chat_vis  = True

        self._setup_window()
        self._build_ui()
        self._connect()

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumWidth(340)
        self.setMaximumWidth(440)
        from PySide6.QtWidgets import QApplication
        g = QApplication.primaryScreen().availableGeometry()
        self.move(g.right() - 460, g.top() + 24)

    # ── UI build ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)

        self._frame = RTFrame()
        outer.addWidget(self._frame)

        lay = QVBoxLayout(self._frame)
        lay.setContentsMargins(16, 12, 16, 14)
        lay.setSpacing(8)

        lay.addLayout(self._header())
        lay.addWidget(self._hline(RED))
        lay.addWidget(self._log_widget())
        lay.addWidget(self._hline(GOLD_DIM))
        lay.addWidget(self._vox_toggle())
        lay.addWidget(self._vox_panel())

    def _header(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)

        row.addWidget(AvatarWidget())

        col = QVBoxLayout()
        col.setSpacing(1)
        t1 = QLabel("ROGUE TRADER COGITATOR")
        t1.setStyleSheet(
            f"color:{GOLD}; font-family:{FONT}; font-size:12px;"
            f"font-weight:bold; letter-spacing:2px;"
        )
        t2 = QLabel(self._cfg.get("game_name","").upper())
        t2.setStyleSheet(
            f"color:{WHITE_DIM}; font-family:{FONT}; font-size:9px; letter-spacing:1px;"
        )
        col.addWidget(t1)
        col.addWidget(t2)
        row.addLayout(col, 1)

        self._dot = QLabel("●")
        self._dot.setStyleSheet(f"color:{RED_LIT}; font-size:9px;")
        row.addWidget(self._dot)

        for txt, fn, hov in (("—", self.showMinimized, WHITE_DIM), ("✕", self.close, ERR)):
            b = QPushButton(txt)
            b.setFixedSize(20, 20)
            b.setStyleSheet(
                f"QPushButton{{color:{GOLD_DIM};background:transparent;border:none;font-size:13px;}}"
                f"QPushButton:hover{{color:{hov};}}"
            )
            b.clicked.connect(fn)
            row.addWidget(b)
        return row

    def _hline(self, color: str) -> QWidget:
        f = QWidget()
        f.setFixedHeight(1)
        f.setStyleSheet(f"background:{color};")
        return f

    def _log_widget(self) -> QTextEdit:
        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setFixedHeight(220)
        self._log.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._log.setStyleSheet(
            f"QTextEdit{{background:{BG_FIELD};border:none;"
            f"color:{WHITE};font-family:{FONT};font-size:{SZ};padding:4px 6px;}}"
            f"QScrollBar:vertical{{background:#0a0604;width:7px;border:none;}}"
            f"QScrollBar::handle:vertical{{background:{RED};border-radius:3px;min-height:18px;}}"
            f"QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0;}}"
        )
        self._log.setHtml(
            f'<p style="color:{RED_LIT};font-family:{FONT};font-size:{SZ_SM};">'
            f'✠ &nbsp; FOR THE EMPEROR &nbsp; ✠</p>'
            f'<p style="color:{WHITE_DIM};font-family:{FONT};font-size:15px;">'
            f'Cogitator online. Watching…</p>'
        )
        return self._log

    def _vox_toggle(self) -> QPushButton:
        self._tog = QPushButton("▼  VOX CHANNEL")
        self._tog.setStyleSheet(
            f"QPushButton{{color:{RED};background:transparent;border:none;"
            f"font-family:{FONT};font-size:10px;letter-spacing:2px;"
            f"font-weight:bold;text-align:left;padding:4px 0;}}"
            f"QPushButton:hover{{color:{RED_LIT};}}"
        )
        self._tog.setCursor(Qt.CursorShape.PointingHandCursor)
        self._tog.clicked.connect(self._toggle_vox)
        return self._tog

    def _vox_panel(self) -> QWidget:
        self._vox = QWidget()
        row = QHBoxLayout(self._vox)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)

        self._inp = QLineEdit()
        self._inp.setPlaceholderText("Issue a command, Rogue Trader…")
        self._inp.setStyleSheet(
            f"QLineEdit{{background:{BG_FIELD};color:{WHITE};"
            f"border:1px solid {RED};border-radius:0px;"
            f"padding:6px 10px;font-family:{FONT};font-size:{SZ};}}"
            f"QLineEdit:focus{{border-color:{RED_LIT};}}"
        )
        self._inp.returnPressed.connect(self._send)
        row.addWidget(self._inp, 1)

        b = QPushButton("⚔")
        b.setFixedSize(36, 36)
        b.setStyleSheet(
            f"QPushButton{{background:{BG_FIELD};color:{GOLD};"
            f"border:1px solid {RED};font-size:17px;}}"
            f"QPushButton:hover{{border-color:{RED_LIT};color:{WHITE};}}"
        )
        b.clicked.connect(self._send)
        row.addWidget(b)
        return self._vox

    # ── signals ───────────────────────────────────────────────────────────────

    def _connect(self):
        self._signals.message_ready.connect(self._on_msg)
        self._signals.error_occurred.connect(self._on_err)
        self._signals.thinking_start.connect(lambda: self._dot.setStyleSheet(f"color:{GOLD};font-size:9px;"))
        self._signals.thinking_stop.connect(lambda: self._dot.setStyleSheet(f"color:{RED_LIT};font-size:9px;"))

    def _on_msg(self, text: str):
        self._frame.set_border(RED_LIT)
        self._add(text, role="ai")
        if self._cfg.get("voice_enabled"):
            from src.voice import speak
            threading.Thread(target=speak, args=(text,), daemon=True).start()

    def _on_err(self, text: str):
        self._add(text, role="err")

    # ── log ───────────────────────────────────────────────────────────────────

    def _add(self, text: str, role: str):
        if role == "ai":
            label, lc, tc = "✠  COGITATOR", RED_LIT, WHITE
        elif role == "you":
            label, lc, tc = "◈  YOU", GOLD_DIM, WHITE_DIM
        else:
            label, lc, tc = "⚠  ALERT", RED, ERR

        safe = text.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\n","<br>")
        html = (
            f'<p style="margin:10px 0 2px 0;color:{lc};font-family:{FONT};'
            f'font-size:{SZ_SM};letter-spacing:1px;font-weight:bold;">{label}</p>'
            f'<p style="margin:0 0 2px 0;color:{tc};font-family:{FONT};'
            f'font-size:16px;line-height:1.5;">{safe}</p>'
        )
        cur = self._log.textCursor()
        cur.movePosition(QTextCursor.MoveOperation.End)
        self._log.setTextCursor(cur)
        self._log.insertHtml(html)
        sb = self._log.verticalScrollBar()
        sb.setValue(sb.maximum())

    # ── chat ──────────────────────────────────────────────────────────────────

    def _send(self):
        t = self._inp.text().strip()
        if not t:
            return
        self._inp.clear()
        self._add(t, "you")
        b64 = None
        try:
            b64 = self._capture()
        except Exception:
            pass
        self._ai_worker.submit_user(t, b64)

    def _toggle_vox(self):
        self._chat_vis = not self._chat_vis
        self._vox.setVisible(self._chat_vis)
        self._tog.setText("▼  VOX CHANNEL" if self._chat_vis else "▶  VOX CHANNEL")
        self.adjustSize()

    # ── drag ──────────────────────────────────────────────────────────────────

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() & Qt.MouseButton.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, _e):
        self._drag_pos = None

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show(); self.raise_(); self.activateWindow()
