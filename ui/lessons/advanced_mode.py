from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
class AdvancedMode(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        back_btn = QPushButton("← Back to Modes")
        back_btn.clicked.connect(lambda: self.parent().setCurrentIndex(0))
        
        content = QLabel("Advanced Mode Content")
        
        layout.addWidget(back_btn)
        layout.addWidget(content)
