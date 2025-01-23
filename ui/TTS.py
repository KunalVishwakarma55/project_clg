import sys
import cv2
import os
import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
from moviepy.editor import VideoFileClip, concatenate_videoclips, ColorClip
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QPushButton, QFrame, 
                              QButtonGroup, QTextEdit, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap, QColor
from PySide6.QtMultimedia import QMediaPlayer,QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
import subprocess


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
    output_path = "combined.avi"
    
    # Try multiple times to remove the file with small delays
    for _ in range(3):
        try:
            if os.path.exists(output_path):
                os.remove(output_path)
            break
        except PermissionError:
            time.sleep(0.5)
            continue
    text = text.lower()
    text = re.sub('[^a-z]+', ' ', text)
    words = text.split()
    words = parse_string(text, dataset)
    words = remove_empty_values(words)
    words = flatten_lists(words)

    clips = []
    for i, word in enumerate(words):
        word = re.sub('[^a-z]+', '', word)
        video_path = os.path.join(videos_path, f"{word}.mp4")
        if os.path.exists(video_path):
            clip = VideoFileClip(video_path)
            clips.append(clip.subclip(0, clip.duration // 2))
            
            # Only add space clip if it's not the last word
            if i < len(words) - 1:
                # Create a shorter space clip with matching dimensions
                space_clip = ColorClip(
                    size=clip.size,
                    color=(255, 255, 255),
                    duration=0.2  # Reduced duration
                ).set_opacity(0.0)  # Make space clip transparent
                clips.append(space_clip)

    if clips:
        # Clean up any existing output file
        output_path = "combined.avi"
        if os.path.exists(output_path):
            os.remove(output_path)
            
        result_clip = concatenate_videoclips(clips, method='compose')
        result_clip.write_videofile(
            output_path,
            fps=30,
            codec='libx264',
            preset='medium',
            ffmpeg_params=['-crf', '23']
        )
        
        # Close all clips to free up resources
        for clip in clips:
            clip.close()
        result_clip.close()
        
        return output_path
    return None


class TTS(QMainWindow):
    # In the MainWindow class, add text_input_style before setup_ui()
    def __init__(self):
        super().__init__()
        
        
        self.audio_output = QAudioOutput()
        self.media_player = QMediaPlayer()
        self.media_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.5)  # 0.5 = 50% volume



        
        # Initialize dataset
        self.dataset_path = "C:/Users/Ravi/Desktop/College_project/text-to-sign/Dataset"
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
        

        self.create_main_content()

    def handle_navigation(self, button_text):
        target_file = self.pages[button_text]
        current_file = os.path.basename(__file__)
        
        if target_file != current_file:
            # Save any necessary state here
            
            # Launch the target Python file
            python_executable = sys.executable
            subprocess.Popen([python_executable, target_file])
            
            # Close the current window
            self.close()


    def create_main_content(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(40)  # Increased spacing between frames
        main_layout.setContentsMargins(50, 50, 50, 50)  # Larger margins for better spacing
        
        # Enhanced Left Frame
        left_frame = QFrame()
        left_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        # Add shadow effect to left frame
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        left_frame.setGraphicsEffect(shadow)
        
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(30, 30, 30, 30)  # Increased internal padding
        left_layout.setSpacing(25)  # More spacing between elements

        # Improved Input Section
        input_label = QLabel("Text Input")
        
        input_label.setStyleSheet("""
            font-size: 25px;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 15px;
            font-family: 'Segoe UI';
            border:none;
        """)

        # Enhanced Text Input
        self.text_input = QTextEdit()
        self.text_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #eef2f7;
                border-radius: 12px;
                font-size: 15px;
                font-family: 'Segoe UI';
                background-color: #f8fafc;
                color: #1a1a1a;
                line-height: 1.6;
            }
            QTextEdit:focus {
                border: 2px solid #2962ff;
                background-color: white;
            }
        """)
        self.text_input.setMinimumHeight(200)
        self.text_input.setPlaceholderText("Enter your text here...")

        # Improved Button Layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)

        # Enhanced Button Styles
        button_style = """
            QPushButton {
                background-color: #2962ff;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 600;
                font-family: 'Segoe UI';
                min-width: 100px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #1e88e5;
                margin-top: -1px;  /* Using margin instead of transform */
            }
            QPushButton:pressed {
                background-color: #1565c0;
                margin-top: 0px;
            }
        """

        # Enhanced Right Frame
        right_frame = QFrame()
        right_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        # Add shadow effect to right frame
        shadow2 = QGraphicsDropShadowEffect()
        shadow2.setBlurRadius(20)
        shadow2.setColor(QColor(0, 0, 0, 30))
        shadow2.setOffset(0, 4)
        right_frame.setGraphicsEffect(shadow2)

        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(30, 30, 30, 30)
        right_layout.setSpacing(25)

        video_label = QLabel("Video Output")
        video_label.setFixedHeight(70)
        video_label.setStyleSheet("""
            font-size: 25px;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 15px;
            font-family: 'Segoe UI';
            border:none;
        """)

        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(450, 350)
        self.video_widget.setStyleSheet("""
            background-color: #f8fafc;
            border-radius: 12px;
            border: 2px solid #eef2f7;
        """)
        self.media_player.setVideoOutput(self.video_widget)

        # Add after the video_widget in create_main_content method
        # Create video controls layout
        video_controls = QHBoxLayout()
        video_controls.setSpacing(10)

        # Create control buttons with icons
        self.play_pause_btn = QPushButton("Play")
        self.mute_btn = QPushButton("Unmute")

        # Style for control buttons
        # In create_main_content method, update the control button style:
        control_btn_style = """
            QPushButton {
                background-color: #2962ff;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                font-family: 'Segoe UI';
                min-width: 80px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #1e88e5;
                margin-top: -1px;
            }
            QPushButton:pressed {
                background-color: #1565c0;
                margin-top: 0px;
            }
        """

        # Create video controls with different colors
        self.play_pause_btn = QPushButton("Play")
        self.mute_btn = QPushButton("Unmute")

        # Set unique colors for each button
        self.play_pause_btn.setStyleSheet(control_btn_style.replace("#2962ff", "#00c853"))  # Green for play/pause
        self.mute_btn.setStyleSheet(control_btn_style.replace("#2962ff", "#ff1744"))        # Red for mute/unmute

        # Add hover effects
        video_controls.setSpacing(15)
        self.play_pause_btn.setCursor(Qt.PointingHandCursor)
        self.mute_btn.setCursor(Qt.PointingHandCursor)


        # Add buttons to controls layout
        video_controls.addWidget(self.play_pause_btn)
        video_controls.addWidget(self.mute_btn)
        video_controls.addStretch()

        # Connect button signals
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        self.mute_btn.clicked.connect(self.toggle_mute)

        # Add video controls to right layout
        right_layout.addLayout(video_controls)


        # Create and style buttons
        buttons = [
            ("Send", "#2962ff"),
            ("Clear", "#ff1744"),
            ("Copy", "#00c853"),
            ("Paste", "#6200ea")
        ]

        for text, color in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(button_style.replace("#2962ff", color))
            btn.setCursor(Qt.PointingHandCursor)
            buttons_layout.addWidget(btn)
            
            if text == "Send":
                btn.clicked.connect(self.send_text)
            elif text == "Clear":
                btn.clicked.connect(self.clear_text)
            elif text == "Copy":
                btn.clicked.connect(self.copy_text)
            elif text == "Paste":
                btn.clicked.connect(self.paste_text)

        # Add widgets to layouts
        left_layout.addWidget(input_label)
        left_layout.addWidget(self.text_input)
        left_layout.addLayout(buttons_layout)

        right_layout.addWidget(video_label)
        right_layout.addWidget(self.video_widget)

        main_layout.addWidget(left_frame, 1)
        main_layout.addWidget(right_frame, 1)

        self.main_layout.addWidget(main_widget)

    def toggle_play_pause(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.play_pause_btn.setText("Play")
        else:
            self.media_player.play()
            self.play_pause_btn.setText("Pause")

    def toggle_mute(self):
        if self.audio_output.isMuted():
            self.audio_output.setMuted(False)
            self.mute_btn.setText("Mute")
        else:
            self.audio_output.setMuted(True)
            self.mute_btn.setText("Unmute")



    def send_text(self):
        # Release the media player resources
        self.media_player.stop()
        self.media_player.setSource("")
        
        text = self.text_input.toPlainText()
        output_path = text_to_sign(text, self.video_names, self.dataset_path)
        
        if output_path and os.path.exists(output_path):
            self.media_player.setSource(output_path)
            self.media_player.play()
            self.play_pause_btn.setText("Pause")
            self.mute_btn.setText("Mute")




    def clear_text(self):
        self.text_input.clear()

    def copy_text(self):
        self.text_input.copy()

    def paste_text(self):
        self.text_input.paste()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TTS()
    window.show()
    sys.exit(app.exec())
