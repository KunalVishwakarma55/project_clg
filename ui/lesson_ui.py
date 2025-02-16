from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
from .lessons.beginner_mode import BeginnerMode
from .lessons.intermediate_mode import IntermediateMode
from .lessons.advanced_mode import AdvancedMode

class LessonUI(QWidget):
    def __init__(self):
        super().__init__()
        self.stacked_widget = QStackedWidget()
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        
        # Mode Selection Page
        self.mode_selection = QWidget()
        self.mode_layout = QVBoxLayout(self.mode_selection)
        
        # Header
        header = QLabel("ASL Learning Center")
        header.setStyleSheet("""
            font-size: 36px;
            color: #2c3e50;
            font-weight: bold;
            margin: 20px;
        """)
        header.setAlignment(Qt.AlignCenter)
        
        # Cards Container
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(30)
        cards_layout.setContentsMargins(20, 20, 20, 20)
        
        # Mode configurations
        self.create_mode_cards(cards_layout)
        
        self.mode_layout.addWidget(header)
        self.mode_layout.addLayout(cards_layout)
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.mode_selection)
        self.stacked_widget.addWidget(BeginnerMode())
        self.stacked_widget.addWidget(IntermediateMode())
        self.stacked_widget.addWidget(AdvancedMode())
        
        self.main_layout.addWidget(self.stacked_widget)

    def create_mode_cards(self, cards_layout):
        modes = [
            {
                "title": "Beginner Mode",
                "image": "assets/beginner.png",
                "description": "Start your ASL journey with alphabet basics",
                "features": ["Learn A-Z Signs", "Interactive Quizzes", "Progress Tracking"],
                "color": "#3498db"
            },
            {
                "title": "Intermediate Mode",
                "image": "assets/intermediate.png",
                "description": "Advance to common words and phrases",
                "features": ["Word Practice", "Video Lessons", "Performance Metrics"],
                "color": "#e67e22"
            },
            {
                "title": "Advanced Mode",
                "image": "assets/advanced.png",
                "description": "Master complex conversations and challenges",
                "features": ["Real-time Practice", "Sentence Building", "Time Challenges"],
                "color": "#27ae60"
            }
        ]
        
        for mode in modes:
            card = self.create_mode_card(mode)
            cards_layout.addWidget(card)

    def create_mode_card(self, mode_info):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 15px;
                padding: 20px;
                min-width: 300px;
                border: 2px solid {mode_info['color']};
            }}
            QFrame:hover {{
                background-color: #f8f9fa;
                transform: scale(1.02);
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        # Title
        title = QLabel(mode_info["title"])
        title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {mode_info['color']};
            padding: 10px;
        """)
        title.setAlignment(Qt.AlignCenter)
        
        # Image
        image = QLabel()
        pixmap = QPixmap(mode_info["image"])
        if not pixmap.isNull():
            image.setPixmap(pixmap.scaled(200, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        image.setAlignment(Qt.AlignCenter)
        
        # Description
        desc = QLabel(mode_info["description"])
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #7f8c8d; margin: 10px 0;")
        desc.setAlignment(Qt.AlignCenter)
        
        # Features
        features = QFrame()
        features_layout = QVBoxLayout(features)
        for feature in mode_info["features"]:
            feature_label = QLabel(f"✓ {feature}")
            feature_label.setStyleSheet("color: #34495e; margin: 5px;")
            features_layout.addWidget(feature_label)
        
        # Start Button
        start_btn = QPushButton("Start Learning")
        start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {mode_info['color']};
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {mode_info['color']}dd;
            }}
        """)
        start_btn.clicked.connect(lambda: self.start_mode(mode_info["title"]))
        
        layout.addWidget(title)
        layout.addWidget(image)
        layout.addWidget(desc)
        layout.addWidget(features)
        layout.addWidget(start_btn)
        
        return card

    def start_mode(self, mode_title):
        if mode_title == "Beginner Mode":
            self.stacked_widget.setCurrentIndex(1)
        elif mode_title == "Intermediate Mode":
            self.stacked_widget.setCurrentIndex(2)
        else:
            self.stacked_widget.setCurrentIndex(3)
