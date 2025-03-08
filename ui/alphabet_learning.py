from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLineEdit, QGridLayout, QLabel, QFrame
)
from PySide6.QtCore import Qt, QSize, QUrl
from PySide6.QtGui import QIcon, QColor, QPixmap
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import QTimer
import os

class AlphabetLearning(QWidget):
    def __init__(self):
        super().__init__()
        self.current_letter_index = 0
        self.letters = []
        self.init_ui()
        self.setStyleSheet("background-color: #f5f6fa;")

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)

        # Header section
        header_frame = QFrame()
        header_frame.setStyleSheet("""
        QFrame {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2980b9, stop:1 #3498db);
            border-radius: 15px;
            padding: 15px;
        }
    """)
        header_layout = QHBoxLayout(header_frame)

        back_button = QPushButton()
        back_button.setIcon(QIcon("assets/back_arrow.png"))
        back_button.setIconSize(QSize(32, 32))
        back_button.setStyleSheet("""
        QPushButton {
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 10px;
            min-width: 40px;
            min-height: 40px;
        }
        QPushButton:hover {
            background-color: rgba(255, 255, 255, 0.3);
        }
    """)
        back_button.clicked.connect(self.go_back)

        header_label = QLabel("Learn ASL Alphabets")
        header_label.setStyleSheet("""
        font-size: 32px;
        font-weight: bold;
        color: white;
        margin-left: 20px;
    """)
        header_layout.addWidget(back_button)
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        main_layout.addWidget(header_frame)

        # Name input section with card style
        input_frame = QFrame()
        input_frame.setStyleSheet("""
        QFrame {
            background-color: white;
            border-radius: 15px;
            padding: 25px;
            border: 1px solid #e0e0e0;
        }
    """)
        input_layout = QVBoxLayout(input_frame)

        input_label = QLabel("Practice Name in Sign Language")
        input_label.setStyleSheet("""
            font-size: 18px;
            color: #34495e;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        input_layout.addWidget(input_label)

        input_row = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Type any name here...")
        self.name_input.setStyleSheet("""
        QLineEdit {
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            font-size: 16px;
            color: #2c3e50;
            background-color: #f8f9fa;
        }
        QLineEdit:focus {
            border-color: #3498db;
            background-color: white;
            box-shadow: 0 0 5px rgba(52, 152, 219, 0.3);
        }
    """)

        learn_button = QPushButton("Start Practice")
        learn_button.setIcon(QIcon("assets/play_icon.png"))
        learn_button.setIconSize(QSize(20, 20))
        learn_button.setStyleSheet("""
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2980b9, stop:1 #3498db);
            color: white;
            padding: 15px 30px;
            border-radius: 12px;
            font-weight: bold;
            font-size: 16px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2473a7, stop:1 #2980b9);
        }
    """)
        learn_button.clicked.connect(self.start_learning)

        input_row.addWidget(self.name_input)
        input_row.addWidget(learn_button)
        input_layout.addLayout(input_row)
        main_layout.addWidget(input_frame)

        # Alphabet grid in a card
        grid_frame = QFrame()
        grid_frame.setStyleSheet("""
        QFrame {
            background-color: white;
            border-radius: 15px;
            padding: 30px;
            border: 1px solid #e0e0e0;
        }
    """)
        grid_layout = QGridLayout(grid_frame)
        grid_layout.setSpacing(12)

        alphabets = [chr(i) for i in range(65, 91)]
        for i, letter in enumerate(alphabets):
            button = QPushButton(letter)
            button.setFixedSize(70, 70)
                        # Update the alphabet button style
            button.setStyleSheet("""
                QPushButton {
                    border: none;
                    border-radius: 35px;
                    color: #3498db;
                    font-size: 26px;
                    font-weight: bold;
                    background-color: #f8f9fa;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2980b9, stop:1 #3498db);
                    color: white;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2473a7, stop:1 #2980b9);
                }
            """)
            # Modified button connection
            button.clicked.connect(lambda checked, l=letter: self.show_sign(l))
            grid_layout.addWidget(button, i // 6, i % 6)

        main_layout.addWidget(grid_frame)

    def go_back(self):
        main_window = self.window()
        main_window.content_area.setCurrentIndex(4)  # Return to learning section

    def start_learning(self):
        name = self.name_input.text().strip().upper()
        if name:
            self.letters = [letter for letter in name if letter.isalpha()]
            self.current_letter_index = 0
            # Create a single video display for the entire name
            self.create_name_display()
            self.play_next_letter()



    def show_sign(self, letter):
    # First close any existing video display
        if hasattr(self, 'sign_display') and self.sign_display:
            self.close_video()
        
        letter = str(letter)
        self.letters = [letter]  # Set single letter as the current sequence
        self.current_letter_index = 0
        
        # Create display and start playing
        self.create_name_display()
        self.play_next_letter()


    def create_name_display(self):
        self.sign_display = QFrame(self)
        self.sign_display.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 20px;
                border: none;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
        """)
        
        layout = QVBoxLayout(self.sign_display)
        
        # Name label
        name_label = QLabel(f"Learning: {self.name_input.text().upper()}")
        name_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin: 10px;
        """)
        name_label.setAlignment(Qt.AlignCenter)
        
        # Progress label
        self.progress_label = QLabel()
        self.progress_label.setStyleSheet("""
            font-size: 16px;
            color: #2c3e50;
            margin: 5px;
        """)
        self.progress_label.setAlignment(Qt.AlignCenter)
        
        # Video widget
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(400, 400)
        
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setAudioOutput(self.audio_output)
        
        # Control buttons
        control_layout = QHBoxLayout()

        close_button = QPushButton("Close")
        close_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e74c3c, stop:1 #c0392b);
                color: white;
                padding: 12px 25px;
                border-radius: 12px;
                font-weight: bold;
                font-size: 16px;
                margin: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #c0392b, stop:1 #a93226);
            }
        """)
        close_button.clicked.connect(self.close_video)

        control_layout.addWidget(close_button)
        
        # Add widgets to layout
        layout.addWidget(name_label)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.video_widget)
        layout.addLayout(control_layout)
        
        # Position and show the popup
        self.sign_display.setFixedSize(500, 600)
        self.sign_display.move(
            self.width()//2 - self.sign_display.width()//2,
            self.height()//2 - self.sign_display.height()//2
        )
        self.sign_display.show()
    def replay_video(self):
        self.media_player.setPosition(0)
        self.media_player.play()

    def close_video(self):
        if hasattr(self, 'media_player'):
            self.media_player.stop()
        
        if hasattr(self, 'sign_display') and self.sign_display:
            if not self.sign_display.isHidden():
                self.sign_display.deleteLater()
                self.sign_display = None

    
    def play_next_letter(self):
        if hasattr(self, 'sign_display') and self.sign_display and not self.sign_display.isHidden():
            letter = self.letters[self.current_letter_index]
            if hasattr(self, 'progress_label') and self.progress_label:
                self.progress_label.setText(f"Playing {self.current_letter_index + 1} of {len(self.letters)}: {letter}")
            
            video_path = self.get_video_path(letter)
            if video_path:
                self.media_player.setSource(QUrl.fromLocalFile(video_path))
                self.media_player.play()
                self.media_player.mediaStatusChanged.connect(self.handle_media_status)


    def get_video_path(self, letter):
        possible_paths = [
            os.path.abspath(f"assets/asl_videos/{letter}.mp4"),
            os.path.abspath(f"assets/asl_videos/{letter.lower()}.mp4"),
            os.path.abspath(f"assets/asl_videos/{letter.upper()}.mp4")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        self.show_error_popup(f"Video for letter {letter} not found")
        return None

    def replay_name(self):
        self.current_letter_index = 0
        self.play_next_letter()

    def handle_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.media_player.mediaStatusChanged.disconnect(self.handle_media_status)
            self.current_letter_index += 1
            
            # If we reach the end of the sequence, start over
            if self.current_letter_index >= len(self.letters):
                self.current_letter_index = 0
                
            # Continue playing next letter
            QTimer.singleShot(500, self.play_next_letter)



    def handle_media_error(self, error, error_string):
        print(f"Media Player Error: {error_string}")
        self.show_error_message(f"Error playing video: {error_string}")

    def show_error_popup(self, message):
        error_popup = QFrame(self)
        error_popup.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 2px solid #e74c3c;
            }
        """)
        
        layout = QVBoxLayout(error_popup)
        
        error_label = QLabel(message)
                # Error popup with modern design
        error_popup.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: none;
                box-shadow: 0 4px 6px rgba(231, 76, 60, 0.2);
            }
        """)


        error_label.setAlignment(Qt.AlignCenter)
        
        ok_button = QPushButton("OK")
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        ok_button.clicked.connect(error_popup.deleteLater)
        
        layout.addWidget(error_label)
        layout.addWidget(ok_button)
        
        error_popup.setFixedSize(300, 150)
        error_popup.move(
            self.width()//2 - error_popup.width()//2,
            self.height()//2 - error_popup.height()//2
        )
        error_popup.show()

