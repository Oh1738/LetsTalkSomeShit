from PySide6.QtCore import QObject, Signal


class AppSignals(QObject):
    """Hub for all cross-thread Qt signals. Instantiate once; pass everywhere."""

    message_ready = Signal(str)    # New AI text to display in the bubble
    error_occurred = Signal(str)   # Error text (shown in red bubble)
    thinking_start = Signal()      # Status dot → amber
    thinking_stop = Signal()       # Status dot → green
