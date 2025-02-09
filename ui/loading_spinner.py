from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen

class LoadingSpinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(100, 100)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.is_spinning = False
        self.dots = 8
        self.start_angle = 0
        self.rotation_angle = 45

    def start(self):
        self.show()
        self.is_spinning = True
        self.timer.start(80)

    def stop(self):
        self.is_spinning = False
        self.timer.stop()
        self.hide()

    def rotate(self):
        self.start_angle = (self.start_angle + self.rotation_angle) % 360
        self.update()

    def paintEvent(self, event):
        if not self.is_spinning:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = min(self.width(), self.height())
        center = width // 2
        outer_radius = (width - 1) * 0.5
        inner_radius = (width - 1) * 0.3

        painter.translate(center, center)
        painter.rotate(self.start_angle)

        color = QColor("#2962ff")
        for i in range(self.dots):
            color.setAlphaF(1.0 - (i / self.dots))
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            
            # Draw dot
            painter.drawEllipse(outer_radius - 10, -4, 10, 8)
            painter.rotate(360 / self.dots)
