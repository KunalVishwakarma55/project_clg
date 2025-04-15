from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QScrollArea, QGridLayout, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon, QColor, QPalette, QLinearGradient, QBrush, QFont
import os
from .alphabet_learning import AlphabetLearning
from .days_learning import DaysLearning
from .colors_learning import ColorsLearning
from .numbers_learning import NumbersLearning
from .months_learning import MonthsLearning
from .greetings_learning import GreetingsLearning

class LearningSection(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # Header Section
        self.header = self.create_header()
        self.main_layout.addWidget(self.header)

        # Scrollable content
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 12px;
                background: #f0f0f0;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 6px;
            }
        """)
        
        # Container for cards
        self.container = QWidget()
        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setContentsMargins(20, 20, 20, 20)
        
        # Define categories with local image paths
        self.categories = [
            ("", "assets/cards_image/alphabet.jpg", "", "#FF6B6B"),
            ("", "assets/cards_image/greetings.jpg", "", "#4ECDC4"), 
            ("", "assets/cards_image/numbers.jpg", "", "#45B7D1"),
            ("", "assets/cards_image/days.jpg", "", "#96CEB4"),
            ("", "assets/cards_image/colours.jpeg", "", "#D4A5A5"),
            ("", "assets/cards_image/month.jpg", "", "#9B89B3")
        ]
        
        # Arrange cards in a grid
        self.update_card_layout()
        
        self.scroll.setWidget(self.container)
        self.main_layout.addWidget(self.scroll)

    def create_header(self):
        header = QFrame()
        header.setStyleSheet("border-radius: 20px;")
        header.setFixedHeight(150)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(20, 20, 20, 20)
        
        # Gradient background for header
        gradient = QLinearGradient(0, 0, 0, 150)
        gradient.setColorAt(0, QColor("#1a237e"))
        gradient.setColorAt(1, QColor("#3949ab"))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(gradient))
        header.setPalette(palette)
        header.setAutoFillBackground(True)
        
        # Add a subtle shadow effect to the header
        header.setGraphicsEffect(self.create_shadow_effect())
        
        self.title = QLabel("Learn Sign Language")
        self.title.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            color: white;
            margin: 0;
        """)
        self.title.setAlignment(Qt.AlignCenter)
        
        self.subtitle = QLabel("Master ASL with our comprehensive learning modules")
        self.subtitle.setStyleSheet("""
            font-size: 18px; 
            color: black;
            margin: 0;
            font-weight:bold;
        """)
        self.subtitle.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(self.title)
        header_layout.addWidget(self.subtitle)
        return header

    def update_card_layout(self):
        window_width = self.width()
        columns = max(2, min(3, window_width // 450))  # Updated from 400 to 450
        
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)
        
        for index, (title, image_path, description, color) in enumerate(self.categories):
            card = self.create_category_card(title, image_path, description, color)
            self.grid_layout.addWidget(card, index // columns, index % columns)

    def create_category_card(self, title, image_path, description, color):
        card = QFrame()
        card.setFixedSize(450, 550)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 20px;
                padding: 0;
                border: none;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            QFrame:hover {{
                transform: scale(1.02);
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setSpacing(5)  # Add spacing between elements
        layout.setContentsMargins(0, 0, 0, 5)  # Add bottom margin
        
        # Image container
        image_container = QFrame()
        image_container.setStyleSheet(f"""
            background-color: {color};
            border-radius: 20px 20px 0 0;
            padding: 0;
        """)
        image_layout = QVBoxLayout(image_container)
        image_layout.setSpacing(0)
        image_layout.setContentsMargins(0, 0, 0, 0)
        
        image = QLabel()
        image.setAlignment(Qt.AlignCenter)
        self.load_local_image(image, image_path)
        image_layout.addWidget(image)
        
        layout.addWidget(image_container)
        
        learn_btn = QPushButton("Start Learning")
        learn_btn.setIcon(QIcon("assets/play_icon.png"))  # Add play icon
        learn_btn.setFixedSize(450, 60)  # Match card width
        learn_btn.setIconSize(QSize(24, 24))  # Icon size
        button_color = ""
        if "alphabet" in image_path:
            button_color = "#FF7777"  # Salmon Red
        elif "greetings" in image_path:
            button_color = "#4DC5C9"  # Cyan Blue
        elif "numbers" in image_path:
            button_color = "#3FACD0"  # Sky Blue
        elif "days" in image_path:
            button_color = "#A2C6C1"  # Soft Teal
        elif "colours" in image_path:
            button_color = "#CBAEA9"  # Muted Rose
        elif "month" in image_path:
            button_color = "#927CA3"  # Dusty Purple
        learn_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {button_color};
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 30px;
                padding: 10px 20px;
                text-align: center;
                border: none;
                box-shadow: 0 3px 6px rgba(0,0,0,0.16);
            }}
            QPushButton:hover {{
                background-color: {button_color}dd;
                box-shadow: 0 4px 8px rgba(0,0,0,0.22);
            }}
            QPushButton:pressed {{
                background-color: {button_color}ee;
                box-shadow: 0 2px 4px rgba(0,0,0,0.12);
            }}
        """)
        learn_btn.setCursor(Qt.PointingHandCursor)
        
        # Button connections based on image path
        if "alphabet" in image_path:
            learn_btn.clicked.connect(self.open_alphabet_learning)
        elif "days" in image_path:
            learn_btn.clicked.connect(self.open_days_learning)
        elif "colours" in image_path:
            learn_btn.clicked.connect(self.open_colors_learning)
        elif "numbers" in image_path:
            learn_btn.clicked.connect(self.open_numbers_learning)
        elif "month" in image_path:
            learn_btn.clicked.connect(self.open_months_learning)
        elif "greetings" in image_path:
            learn_btn.clicked.connect(self.open_greetings_learning)
        else:
            learn_btn.clicked.connect(lambda: self.open_video_player(title))
        layout.addWidget(learn_btn)
        
        return card

    def open_alphabet_learning(self):
        self.alphabet_section = AlphabetLearning()
        self.switch_to_section(self.alphabet_section)

    def open_days_learning(self):
        self.days_section = DaysLearning()
        self.switch_to_section(self.days_section)

    def open_colors_learning(self):
        self.colors_section = ColorsLearning()
        self.switch_to_section(self.colors_section)

    def open_numbers_learning(self):
        self.numbers_section = NumbersLearning()
        self.switch_to_section(self.numbers_section)

    def open_months_learning(self):
        self.months_section = MonthsLearning()
        self.switch_to_section(self.months_section)

    def open_greetings_learning(self):
        self.greetings_section = GreetingsLearning()
        self.switch_to_section(self.greetings_section)
    
    def switch_to_section(self, section):
        # Get the main window
        main_window = self.window()
        
        # Add the new section to the content area
        main_window.content_area.addWidget(section)
        
        # Set the current widget to the new section
        main_window.content_area.setCurrentWidget(section)
        
        # Ensure the navigation bar connections are maintained
        # This is important to reconnect or update any navigation bar functionality
        if hasattr(main_window, 'update_navigation'):
            main_window.update_navigation()

    def load_local_image(self, image_label, image_path):
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            image_label.setPixmap(pixmap.scaled(450, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            image_label.setText("Image not available")
            image_label.setStyleSheet("font-size: 16px; color: #555;")

    def create_shadow_effect(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 5)
        return shadow

    def resizeEvent(self, event):
        # Update the card layout when the window is resized
        self.update_card_layout()
        super().resizeEvent(event)
