import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QPushButton, QFrame, QComboBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QUrl
import random
import os

class LessonUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ASL Letter Learning")
        self.setMinimumSize(1200, 800)
        
        # Initialize difficulty levels
        self.difficulty_levels = {
            'Beginner': ['A', 'B', 'C', 'D', 'E'],
            'Intermediate': ['F', 'G', 'H', 'I', 'J'],
            'Advanced': ['K', 'L', 'M', 'N', 'O']
        }
        self.current_difficulty = 'Beginner'
        self.letters = self.difficulty_levels[self.current_difficulty]
        
        # Initialize paths and variables
        self.sounds_path = os.path.join("assets", "sounds")
        self.images_path = os.path.join("assets", "asl_images")
        self.current_letter = None
        self.score = 0
        
        # Setup sounds
        self.setup_sounds()
        
        # Setup UI
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QVBoxLayout(main_widget)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        
        self.setup_ui()
        self.load_new_question()

    def setup_sounds(self):
        self.correct_sound = QSoundEffect()
        self.correct_sound.setSource(QUrl.fromLocalFile(os.path.join(self.sounds_path, "correct.wav")))
        self.correct_sound.setVolume(0.5)
        
        self.incorrect_sound = QSoundEffect()
        self.incorrect_sound.setSource(QUrl.fromLocalFile(os.path.join(self.sounds_path, "incorrect.wav")))
        self.incorrect_sound.setVolume(0.5)
        
        self.button_click_sound = QSoundEffect()
        self.button_click_sound.setSource(QUrl.fromLocalFile(os.path.join(self.sounds_path, "click.wav")))
        self.button_click_sound.setVolume(0.3)

    def setup_ui(self):
        # Title
        title_label = QLabel("Learn ASL Letters")
        title_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #2d3436;
            padding: 20px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(title_label)

        # Difficulty selector
        # In the setup_ui method, update the difficulty selector styling:
        difficulty_container = QHBoxLayout()
        difficulty_label = QLabel("Difficulty Level:")
        difficulty_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2d3436;
            margin-right: 10px;
        """)

        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(self.difficulty_levels.keys())
        self.difficulty_combo.setStyleSheet("""
            QComboBox {
                font-size: 18px;
                padding: 8px 15px;
                border: 2px solid #6c5ce7;
                border-radius: 8px;
                min-width: 200px;
                background-color: white;
                color: #2d3436;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 20px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #2d3436;
                selection-background-color: #6c5ce7;
                selection-color: white;
                padding: 8px;
                border: 2px solid #6c5ce7;
                border-radius: 8px;
            }
            QComboBox QAbstractItemView::item {
                min-height: 30px;
                padding: 5px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #e6e1ff;
                color: #2d3436;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #6c5ce7;
                color: white;
            }
        """)



        self.difficulty_combo.currentTextChanged.connect(self.change_difficulty)
        
        difficulty_container.addStretch()
        difficulty_container.addWidget(difficulty_label)
        difficulty_container.addWidget(self.difficulty_combo)
        difficulty_container.addStretch()
        
        self.main_layout.addLayout(difficulty_container)

        # Score Display
        self.score_label = QLabel(f"Score: {self.score}")
        self.score_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #00b894;
            padding: 10px;
        """)
        self.score_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.score_label)

        # Image Container
        self.image_frame = QFrame()
        self.image_frame.setFixedSize(600, 600)
        self.image_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 20px;
                padding: 20px;
                border: 2px solid #dfe6e9;
            }
        """)
        
        image_layout = QVBoxLayout(self.image_frame)
        image_layout.setContentsMargins(10, 10, 10, 10)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(500, 500)
        image_layout.addWidget(self.image_label)
        
        image_container = QHBoxLayout()
        image_container.addStretch()
        image_container.addWidget(self.image_frame)
        image_container.addStretch()
        self.main_layout.addLayout(image_container)

        # Options Buttons
        self.options_frame = QFrame()
        self.options_layout = QHBoxLayout(self.options_frame)
        self.options_layout.setSpacing(20)
        self.update_option_buttons()
        self.main_layout.addWidget(self.options_frame)

        # Next Button
        self.next_button = QPushButton("Next Question →")
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: #00b894;
                color: white;
                border-radius: 15px;
                padding: 20px 40px;
                font-size: 24px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #00a885;
            }
        """)
        self.next_button.setCursor(Qt.PointingHandCursor)
        self.next_button.clicked.connect(self.load_new_question)
        self.main_layout.addWidget(self.next_button)

    def change_difficulty(self, difficulty):
        self.current_difficulty = difficulty
        self.letters = self.difficulty_levels[difficulty]
        self.update_option_buttons()
        self.load_new_question()

    def update_option_buttons(self):
        # Clear existing buttons
        for i in reversed(range(self.options_layout.count())): 
            self.options_layout.itemAt(i).widget().setParent(None)
        
        button_style = """
            QPushButton {
                background-color: #6c5ce7;
                color: white;
                border-radius: 15px;
                padding: 20px 40px;
                font-size: 24px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #5f48e6;
            }
            QPushButton:pressed {
                background-color: #4834d4;
            }
        """
        
        for letter in self.letters:
            btn = QPushButton(letter)
            btn.setStyleSheet(button_style)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, l=letter: self.check_answer(l))
            self.options_layout.addWidget(btn)

    def load_new_question(self):
        available_letters = [letter for letter in self.letters if letter != self.current_letter]
        self.current_letter = random.choice(available_letters)
        self.button_click_sound.play()
        
        image_path = os.path.join(self.images_path, f"{self.current_letter}.png")
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.setText("Image not found!")

    def check_answer(self, selected_letter):
        if selected_letter == self.current_letter:
            self.score += 1
            self.score_label.setText(f"Score: {self.score}")
            self.correct_sound.play()
            self.show_feedback(True)
        else:
            self.incorrect_sound.play()
            self.show_feedback(False)
        
        QTimer.singleShot(1000, self.load_new_question)

    def show_feedback(self, correct):
        feedback = QLabel("✓ Correct!" if correct else "✗ Incorrect!")
        feedback.setStyleSheet(f"""
            font-size: 24px;
            color: {'#00b894' if correct else '#ff7675'};
            font-weight: bold;
            padding: 10px;
            background-color: white;
            border-radius: 10px;
        """)
        feedback.setAlignment(Qt.AlignCenter)
        self.main_layout.insertWidget(1, feedback)
        QTimer.singleShot(1000, lambda: feedback.deleteLater())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LessonUI()
    window.show()
    sys.exit(app.exec())
