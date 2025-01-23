import sys
import cv2
import os
import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
from moviepy.editor import VideoFileClip, concatenate_videoclips
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QPushButton, QFrame, 
                              QButtonGroup, QTextEdit, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap, QColor
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget

# Initialize NLTK components
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

# Helper functions
def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

def parse_string(string, dataset):
    parsed_list = []
    start = 0
    end = len(string)
    while start < end:
        max_chunk = ""
        max_length = 0
        for chunk in dataset:
            if string.startswith(chunk.lower(), start) and len(chunk) > max_length:
                max_chunk = chunk
                max_length = len(chunk)
        if max_chunk:
            parsed_list.append(max_chunk)
            start += len(max_chunk)
        else:
            start += 1
    return parsed_list

def remove_empty_values(lst):
    return [x for x in lst if x]

def flatten_lists(lst):
    flat_list = []
    for i in lst:
        if isinstance(i, list):
            flat_list.extend(flatten_lists(i))
        else:
            flat_list.append(i)
    return flat_list

def text_to_sign(text, dataset, videos_path):
    text = text.lower()
    text = re.sub('[^a-z]+', ' ', text)
    words = parse_string(text, dataset)
    words = remove_empty_values(words)
    words = flatten_lists(words)

    clips = []
    for word in words:
        video_path = os.path.join(videos_path, f"{word}.mp4")
        if os.path.exists(video_path):
            clip = VideoFileClip(video_path)
            clips.append(clip.subclip(0, clip.duration // 2))

    if clips:
        result_clip = concatenate_videoclips(clips, method='compose')
        output_path = "combined.mp4"
        result_clip.write_videofile(output_path, fps=30)
        return output_path
    return None

class MainWindow(QMainWindow):
    # In the MainWindow class, add text_input_style before setup_ui()
    def __init__(self):
        super().__init__()
        
        # Initialize dataset
        self.dataset_path = "Dataset"
        self.videos = os.listdir(self.dataset_path)
        self.video_names = [os.path.splitext(video)[0].replace("-", " ").lower() for video in self.videos]
        
        # Modern color palette
        self.colors = {
            'primary': '#2962ff',
            'secondary': '#f0f2f5',
            'accent': '#1e88e5',
            'text': '#1a1a1a',
            'light_text': '#757575',
            'white': '#ffffff',
            'border': '#e0e0e0',
            'hover': '#f5f5f5',
            'success': '#4caf50',
        }
        
        # UI Setup
        self.setWindowTitle("Sign Language Interpreter")
        self.setMinimumSize(1091, 672)
        self.setFont(QFont("Segoe UI", 15))
        self.setStyleSheet(f"background-color: {self.colors['secondary']};")
        
        # Define all styles
        self.text_input_style = f"""
            QTextEdit {{
                border: 2px solid {self.colors['border']};
                border-radius: 10px;
                padding: 15px;
                font-size: 14px;
                font-family: 'Segoe UI';
                background-color: {self.colors['white']};
            }}
            QTextEdit:focus {{
                border: 2px solid {self.colors['primary']};
            }}
        """
        
        self.nav_button_style = f"""
            QPushButton {{
                background-color: transparent;
                color: {self.colors['text']};
                border: none;
                padding: 12px 24px;
                font-size: 15px;
                font-weight: 600;
                font-family: 'Segoe UI';
            }}
            QPushButton:hover {{
                color: {self.colors['primary']};
                background-color: {self.colors['hover']};
                border-radius: 6px;
            }}
            QPushButton:checked {{
                color: {self.colors['primary']};
                border-bottom: 3px solid {self.colors['primary']};
                font-weight: 700;
            }}
        """
        
        self.button_style = f"""
            QPushButton {{
                background-color: {self.colors['primary']};
                color: {self.colors['white']};
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                font-family: 'Segoe UI';
            }}
            QPushButton:hover {{
                background-color: {self.colors['accent']};
            }}
            QPushButton:pressed {{
                background-color: {self.colors['primary']};
            }}
        """
        
        self.frame_style = f"""
            QFrame {{
                background-color: {self.colors['white']};
                border-radius: 10px;
            }}
        """
        
        self.setup_ui()

        
    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.create_nav_bar()
        self.create_main_content()

    # Keep your existing create_nav_bar method
    def create_nav_bar(self):
        # Keeping your existing navbar code...
        navbar = QWidget()
        navbar.setFixedHeight(70)
        navbar.setStyleSheet("""
            QWidget {
                background-color: white;
                border-bottom: 1px solid #e0e0e0;
            }
        """)
        
        navbar_layout = QHBoxLayout(navbar)
        navbar_layout.setContentsMargins(20, 0, 20, 0)
        
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/logo.png")
        logo_label.setPixmap(logo_pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        app_label = QLabel("Sign Interpreter")
        app_label.setStyleSheet("""
            color: #1a1a1a;
            font-size: 24px;
            font-weight: 700;
            font-family: 'Segoe UI';
            margin-left: 10px;
        """)
        
        left_section = QHBoxLayout()
        left_section.addWidget(logo_label)
        left_section.addWidget(app_label)
        left_section.addStretch()
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        buttons = ["Home", "Sign to Text", "Text to Sign", "Blog"]
        
        button_group = QButtonGroup(self)
        button_group.setExclusive(True)
        
        for text in buttons:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setStyleSheet(self.nav_button_style)
            if text == "Home":
                btn.setChecked(True)
            button_group.addButton(btn)
            button_layout.addWidget(btn)
        
        navbar_layout.addLayout(left_section)
        navbar_layout.addLayout(button_layout)
        navbar_layout.addStretch()
        
        self.main_layout.addWidget(navbar)

    def create_main_content(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Left Frame
        left_frame = QFrame()
        left_frame.setStyleSheet(self.frame_style)
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(20)
        
        # Input Section
        input_label = QLabel("Text Input")
        input_label.setStyleSheet("""
            font-size: 20px;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 10px;
            font-family: 'Segoe UI';
        """)
        
        # Text Input with visible styling
        self.text_input = QTextEdit()
        self.text_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding: 15px;
                font-size: 14px;
                font-family: 'Segoe UI';
                background-color: white;
                color: #1a1a1a;
            }
            QTextEdit:focus {
                border: 2px solid #2962ff;
            }
        """)
        self.text_input.setMinimumHeight(150)
        self.text_input.setPlaceholderText("Enter your text here...")
        
        # Buttons with visible styling
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        # Create buttons with enhanced visibility
        send_btn = QPushButton("Send")
        clear_btn = QPushButton("Clear")
        copy_btn = QPushButton("Copy")
        paste_btn = QPushButton("Paste")
        
        button_style = """
            QPushButton {
                background-color: #2962ff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                font-family: 'Segoe UI';
                min-width: 80px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #1e88e5;
            }
            QPushButton:pressed {
                background-color: #1565c0;
            }
        """
        
        for btn in [send_btn, clear_btn, copy_btn, paste_btn]:
            btn.setStyleSheet(button_style)
            btn.setCursor(Qt.PointingHandCursor)
            buttons_layout.addWidget(btn)
        
        # Connect button signals
        send_btn.clicked.connect(self.send_text)
        clear_btn.clicked.connect(self.clear_text)
        copy_btn.clicked.connect(self.copy_text)
        paste_btn.clicked.connect(self.paste_text)
        
        # Add widgets to left layout
        left_layout.addWidget(input_label)
        left_layout.addWidget(self.text_input)
        left_layout.addLayout(buttons_layout)
        
        # Right Frame setup remains the same
        right_frame = QFrame()
        right_frame.setStyleSheet(self.frame_style)
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(20)
        
        video_label = QLabel("Video Output")
        video_label.setStyleSheet("""
            font-size: 20px;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 10px;
            font-family: 'Segoe UI';
        """)
        
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(400, 300)
        self.video_widget.setStyleSheet("""
            background-color: #f0f2f5;
            border-radius: 10px;
            border: 2px solid #e0e0e0;
        """)
        
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)
        
        right_layout.addWidget(video_label)
        right_layout.addWidget(self.video_widget)
        
        # Add frames to main layout
        main_layout.addWidget(left_frame, 1)
        main_layout.addWidget(right_frame, 1)
        
        self.main_layout.addWidget(main_widget)


    def send_text(self):
        text = self.text_input.toPlainText()
        output_path = text_to_sign(text, self.video_names, self.dataset_path)
        if output_path:
            # Play the video using QMediaPlayer
            self.media_player.setSource(output_path)
            self.media_player.play()

    def clear_text(self):
        self.text_input.clear()

    def copy_text(self):
        self.text_input.copy()

    def paste_text(self):
        self.text_input.paste()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
