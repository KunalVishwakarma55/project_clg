from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QGridLayout, QLabel, QFrame, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QSize, QUrl
from PySide6.QtGui import QIcon, QColor, QFont
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
import os

class MonthsLearning(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setStyleSheet("background-color: #EEF2F7;")

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 20, 40, 20)
        main_layout.setSpacing(20)

        # Header section
        header_frame = QFrame()
        header_frame.setFixedHeight(170)  # Set a fixed height for the header
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #4B79A1, stop:1 #283E51);
                border-radius: 20px;
                padding: 20px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # Back button
        back_button = QPushButton()
        back_button.setIcon(QIcon("assets/back_arrow.png"))
        back_button.setIconSize(QSize(24, 24))
        back_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15);
                border-radius: 15px;
                padding: 12px;
                min-width: 45px;
                min-height: 45px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        back_button.clicked.connect(self.go_back)

        # Header title
        header_label = QLabel("Months")
        header_label.setFont(QFont("Segoe UI", 36, QFont.Bold))
        header_label.setStyleSheet("""
            color: white;
            margin-left: 20px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        """)
        
        header_layout.addWidget(back_button)
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        main_layout.addWidget(header_frame)

        # Months grid container
        grid_frame = QFrame()
        grid_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 25px;
                padding: 20px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 5)
        grid_frame.setGraphicsEffect(shadow)

        grid_layout = QGridLayout(grid_frame)
        grid_layout.setSpacing(15)

        months_data = [
            ["JAN", "FEB", "MAR", "APR"],
            ["MAY", "JUN", "JUL", "AUG"],
            ["SEP", "OCT", "NOV", "DEC"]
        ]

        for row, months in enumerate(months_data):
            for col, month in enumerate(months):
                button = self.create_month_button(month)
                grid_layout.addWidget(button, row, col)

        main_layout.addWidget(grid_frame)

    def create_month_button(self, month):
        button = QPushButton(month)
        button.setFixedSize(300, 150)
        button.setFont(QFont("Segoe UI", 16, QFont.Bold))
        button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 2px solid #e8e8e8;
                border-radius: 20px;
                color: #2c3e50;
                padding: 15px;
                text-align: center;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #4B79A1, stop:1 #283E51);
                color: white;
                border: none;
            }
            QPushButton:pressed {
                background-color: #2c3e50;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, 4)
        button.setGraphicsEffect(shadow)
        
        button.clicked.connect(lambda: self.show_sign(month))
        return button

    def go_back(self):
        main_window = self.window()
        main_window.content_area.setCurrentIndex(4)

    def show_sign(self, month):
        # Close any existing video display
        if hasattr(self, 'sign_display') and self.sign_display:
            self.close_video()
        
        # Create the video display pop-up
        self.create_video_display(month)

    def create_video_display(self, month):
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
        
        # Month label
        month_label = QLabel(f"Learning: {month}")
        month_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin: 10px;
        """)
        month_label.setAlignment(Qt.AlignCenter)
        
        # Video widget
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(400, 400)
        
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setAudioOutput(self.audio_output)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        replay_button = QPushButton("Replay")
        replay_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2980b9, stop:1 #3498db);
                color: white;
                padding: 12px 25px;
                border-radius: 12px;
                font-weight: bold;
                font-size: 16px;
                margin: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2473a7, stop:1 #2980b9);
            }
        """)
        replay_button.clicked.connect(self.replay_video)
        
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
        
        control_layout.addWidget(replay_button)
        control_layout.addWidget(close_button)
        
        # Add widgets to layout
        layout.addWidget(month_label)
        layout.addWidget(self.video_widget)
        layout.addLayout(control_layout)
        
        # Position and show the pop-up
        self.sign_display.setFixedSize(500, 600)
        self.sign_display.move(
            self.width()//2 - self.sign_display.width()//2,
            self.height()//2 - self.sign_display.height()//2
        )
        self.sign_display.show()

        # Play the video for the selected month
        self.play_video(month)

    def get_video_path(self, month):
        # Map the button text to the full month name
        month_mapping = {
            "JAN": "january",
            "FEB": "february",
            "MAR": "march",
            "APR": "april",
            "MAY": "may",
            "JUN": "june",
            "JUL": "july",
            "AUG": "august",
            "SEP": "september",
            "OCT": "october",
            "NOV": "november",
            "DEC": "december"
        }
        
        # Get the full month name from the mapping
        full_month_name = month_mapping.get(month, "").lower()
        
        if not full_month_name:
            return None  # If no mapping is found, return None
        
        # Define the video path
        video_path = os.path.abspath(f"assets/months_videos/{full_month_name}.mp4")
        
        # Check if the video file exists
        if os.path.exists(video_path):
            return video_path
        
        # If no video is found, return None
        return None

    def play_video(self, month):
        video_path = self.get_video_path(month)
        if video_path:
            self.media_player.setSource(QUrl.fromLocalFile(video_path))
            self.media_player.play()
        else:
            self.show_error_popup(f"Video for {month} not found")

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

    def show_error_popup(self, message):
        error_popup = QFrame(self)
        error_popup.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: none;
                box-shadow: 0 4px 6px rgba(231, 76, 60, 0.2);
            }
        """)
        
        layout = QVBoxLayout(error_popup)
        
        error_label = QLabel(message)
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