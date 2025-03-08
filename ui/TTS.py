# Standard library imports
import sys
import os
import re
import subprocess
from typing import List, Optional

# Third-party imports
import cv2
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
from moviepy.editor import VideoFileClip, concatenate_videoclips, ColorClip
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QButtonGroup, QTextEdit,
    QGraphicsDropShadowEffect, QSlider
)
from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtGui import QFont, QPixmap, QColor, QMovie
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
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
    dataset_lower = [d.lower() for d in dataset]
    case_mapping = dict(zip(dataset_lower, dataset))
    
    # Identify sentence type
    sentence_type = 'statement'
    if '?' in string:
        sentence_type = 'question'
    elif '!' in string:
        sentence_type = 'exclamation'
    
    # Clean and normalize input
    string = string.lower().strip()
    
    # Split into words and process each word
    words = string.split()
    result = []
    i = 0
    
    # Add sentence type indicator
    if sentence_type == 'question' and 'question' in dataset_lower:
        result.append(case_mapping['question'])
    elif sentence_type == 'exclamation' and 'exclamation' in dataset_lower:
        result.append(case_mapping['exclamation'])
    
    while i < len(words):
        # Check if the word is a number
        if words[i].isdigit() and int(words[i]) < 10:
            result.append(words[i])  # Directly use the number for video filename
            i += 1
            continue
            
        # Try matching phrases
        phrase_found = False
        for j in range(len(words), i, -1):
            phrase = ' '.join(words[i:j])
            clean_phrase = phrase.replace('?', '').replace('!', '')
            if clean_phrase in dataset_lower:
                result.append(case_mapping[clean_phrase])
                i = j
                phrase_found = True
                break
        
        if not phrase_found:
            # Handle individual words or letters
            word = words[i].replace('?', '').replace('!', '')
            if word in dataset_lower:
                result.append(case_mapping[word])
            else:
                # Break into individual letters
                for letter in word:
                    if letter in dataset_lower:
                        result.append(case_mapping[letter])
            i += 1
    
    return result

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

def text_to_sign(text: str, dataset: List[str], videos_path: str) -> Optional[str]:
    output_path = "combined.avi"
    standard_size = (640, 480)
    clips = []
    
    try:
        if os.path.exists(output_path):
            os.remove(output_path)
            
        text = text.lower().strip()
        text = re.sub('[^a-z0-9\s]+', ' ', text)
        words = parse_string(text, dataset)
        words = remove_empty_values(words)
        words = flatten_lists(words)
        
        for i, word in enumerate(words):
            # Try different filename formats
            possible_filenames = [
                f"{word}.mp4",
                f"{word.replace(' ', '-')}.mp4",
                f"{word.replace(' ', '')}.mp4"
            ]
            
            video_path = None
            for filename in possible_filenames:
                temp_path = os.path.join(videos_path, filename)
                if os.path.exists(temp_path):
                    video_path = temp_path
                    break
            
            if not video_path:
                print(f"Warning: Video for '{word}' not found")
                continue
                
            clip = VideoFileClip(video_path)
            clips.append(clip.resize(standard_size))
            
            if i < len(words) - 1:
                space_clip = ColorClip(
                    size=standard_size,
                    color=(255, 255, 255),
                    duration=0.3
                ).set_opacity(0.0)
                clips.append(space_clip)
                
        if not clips:
            return None
            
        final_clip = concatenate_videoclips(clips, method='compose')
        final_clip.write_videofile(
            output_path,
            fps=30,
            codec='libx264',
            preset='medium',
            ffmpeg_params=['-crf', '23']
        )
        
        return output_path
        
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        return None
        
    finally:
        for clip in clips:
            clip.close()
        if 'final_clip' in locals():
            final_clip.close()

class TTS(QMainWindow):
    def __init__(self):
        super().__init__()

        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(25)
        self.speed_slider.setMaximum(200)
        self.speed_slider.setValue(100)
        
        # Connect the slider signal to the slot
        self.speed_slider.valueChanged.connect(self.update_speed)
        # Add this line for processing state
        self.is_processing = False

        self.audio_output = QAudioOutput()
        self.media_player = QMediaPlayer()

        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(450, 350)
        self.video_widget.setStyleSheet("""
            background-color: white;
            border-radius: 12px;
            border: 2px solid #eef2f7;
        """)
        self.media_player.mediaStatusChanged.connect(self.handle_media_status)
        
        # Initialize loading spinner with a light color
        self.loading_spinner = QLabel(self)
        gif_path = os.path.abspath("assets/loa.svg")
        self.loading_movie = QMovie(gif_path)
        
        # Debugging: Check if the GIF is loaded successfully
        if not self.loading_movie.isValid():
            print(f"Error: GIF file not found or invalid at path: {gif_path}")
        else:
            print("GIF loaded successfully")

        self.loading_spinner.setMovie(self.loading_movie)
        self.loading_movie.start()

        if self.loading_movie.state() == QMovie.Running:
            print("GIF is playing")
        else:
            print("GIF is not playing")

        self.loading_spinner.setMovie(self.loading_movie)
        self.loading_spinner.setFixedSize(200, 200)
        self.loading_spinner.setStyleSheet("background-color: transparent;")
        self.loading_spinner.hide()

        self.is_loading = False

    # Add a timer to delay hiding the loading animation
        self.hide_animation_timer = QTimer()
        self.hide_animation_timer.setSingleShot(True)  # Only trigger once
        self.hide_animation_timer.timeout.connect(self.hide_loading_animation)
        
        # Animation text for loading
        self.animation_label = QLabel(self)
        self.animation_label.setAlignment(Qt.AlignCenter)
        self.animation_label.setStyleSheet("color: white; font-size: 16px; background-color: rgba(0, 0, 0, 150); border-radius: 10px;")
        self.animation_label.hide()

        self.animation_text = ["Generating video", "Generating video ⚫", "Generating video ⚫⚫", "Generating video ⚫⚫⚫"]
        self.animation_index = 0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)

        self.media_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.5)  # 0.5 = 50% volume

        # Initialize dataset
        self.dataset_path = "text-to-sign/Dataset/simplified_dataset"
        self.videos = os.listdir(self.dataset_path)
        self.video_names = [os.path.splitext(video)[0].replace('-', ' ').lower() for video in self.videos]
        
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

    def create_main_content(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(40)
        main_layout.setContentsMargins(50, 50, 50, 50)

        # Left Frame Setup
        left_frame = QFrame()
        left_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        left_frame.setGraphicsEffect(shadow)
        
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(30, 30, 30, 30)
        left_layout.setSpacing(25)

        # Input Section
        input_label = QLabel("Text Input")
        input_label.setStyleSheet("""
            font-size: 25px;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 15px;
            font-family: 'Segoe UI';
            border: none;
        """)

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

        # Right Frame Setup
        right_frame = QFrame()
        right_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 15px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        shadow2 = QGraphicsDropShadowEffect()
        shadow2.setBlurRadius(20)
        shadow2.setColor(QColor(0, 0, 0, 30))
        shadow2.setOffset(0, 4)
        right_frame.setGraphicsEffect(shadow2)

        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(30, 30, 30, 30)
        right_layout.setSpacing(20)

        # Video Section
        video_label = QLabel("Video Output")
        video_label.setStyleSheet("""
            font-size: 25px;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 10px;
            font-family: 'Segoe UI';
            border: none;
            padding-bottom: 5px;
            border-bottom: 2px solid #eef2f7;
            background-color: #ffffff;

        """)

        # Video Controls
        video_controls = QHBoxLayout()
        video_controls.setSpacing(15)
        video_controls.setContentsMargins(0, 0, 0, 15)

        control_btn_style = """
            QPushButton {
                background-color: #2962ff;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                font-family: 'Segoe UI';
                min-width: 100px;
                min-height: 38px;
                padding: 8px 16px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            QPushButton:hover {
                background-color: #1e88e5;
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }
            QPushButton:pressed {
                background-color: #1565c0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
        """

        self.play_pause_btn = QPushButton("▶ Play")
        self.play_pause_btn.setStyleSheet(control_btn_style.replace("#2962ff", "#00c853"))
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        
        video_controls.addWidget(self.play_pause_btn)
        video_controls.addStretch()

        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(450, 350)
        self.video_widget.setStyleSheet("""
            background-color: #ffffff;
            border-radius: 12px;
            border: 2px solid #eef2f7;
        """)
        self.media_player.setVideoOutput(self.video_widget)

        # Enhanced Speed Controls with better responsive design
        speed_control_layout = QHBoxLayout()
        speed_control_layout.setSpacing(20)
        speed_control_layout.setContentsMargins(0, 15, 0, 15)

        # Modern slider container frame
        slider_frame = QFrame()
        slider_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 12px;
                padding: 10px;
                border: 1px solid #eef2f7;
            }
        """)
        slider_layout = QHBoxLayout(slider_frame)
        slider_layout.setContentsMargins(15, 5, 15, 5)
        slider_layout.setSpacing(15)

        # Enhanced slider styling
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(25)
        self.speed_slider.setMaximum(200)
        self.speed_slider.setValue(100)
        self.speed_slider.setFixedWidth(250)  # Fixed width for consistency
        self.speed_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: none;
                height: 8px;
                background: #e0e0e0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #2962ff;
                border: 3px solid #ffffff;
                width: 22px;
                height: 22px;
                margin: -7px 0;
                border-radius: 12px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }
            QSlider::handle:horizontal:hover {
                background: #1e88e5;
                border: 3px solid #f5f5f5;
                box-shadow: 0 3px 7px rgba(0,0,0,0.3);
            }
            QSlider::sub-page:horizontal {
                background: #2962ff;
                border-radius: 4px;
            }
        """)

        self.speed_slider.valueChanged.connect(self.update_speed)

        # Modern speed labels
        speed_label_style = """
            QLabel {
                color: #424242;
                font-size: 14px;
                font-weight: 600;
                font-family: 'Segoe UI';
                padding: 5px 10px;
                background: #ffffff;
                border-radius: 8px;
                border: 1px solid #eef2f7;
            }
        """

        slow_label = QLabel("🐌 0.25x")  # Snail for slow
        fast_label = QLabel("🚀 2.00x")  # Rocket for fast
        slow_label.setStyleSheet(speed_label_style)
        fast_label.setStyleSheet(speed_label_style)

        self.speed_label = QLabel("⚡ 1.00x")
        self.speed_label.setStyleSheet("""
            QLabel {
                color: #2962ff;
                font-size: 14px;
                font-weight: 600;
                font-family: 'Segoe UI';
                min-width: 70px;
                padding: 5px 15px;
                background: #ffffff;
                border: 2px solid #2962ff;
                border-radius: 8px;
                text-align: center;
            }
        """)

        # Assemble slider components
        slider_layout.addWidget(slow_label)
        slider_layout.addWidget(self.speed_slider)
        slider_layout.addWidget(fast_label)
        slider_layout.addWidget(self.speed_label)

        speed_control_layout.addWidget(slider_frame)

        # Action Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)

        button_style = """
            QPushButton {
                background-color: #2962ff;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 600;
                font-family: 'Segoe UI';
                min-width: 120px;
                min-height: 40px;
                padding-left: 15px;
                padding-right: 15px;
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

        # Define buttons with icons
        buttons = [
            ("▶ Send", "#2962ff", self.send_text),
            ("🗑️ Clear", "#ff1744", self.clear_text), 
            ("📋 Copy", "#00c853", self.copy_text),
            ("📎 Paste", "#6200ea", self.paste_text)
        ]

        for text, color, callback in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(button_style.replace("#2962ff", color))
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(callback)
            buttons_layout.addWidget(btn)
                    
            if text == "Send":
                btn.clicked.connect(self.send_text)
            elif text == "Clear":
                btn.clicked.connect(self.clear_text)
            elif text == "Copy":
                btn.clicked.connect(self.copy_text)
            elif text == "Paste":
                btn.clicked.connect(self.paste_text)

        # Assembling Layouts
        left_layout.addWidget(input_label)
        left_layout.addWidget(self.text_input)
        left_layout.addLayout(buttons_layout)

        right_layout.addWidget(video_label)
        right_layout.addLayout(video_controls)
        right_layout.addWidget(self.video_widget)
        right_layout.addLayout(speed_control_layout)

        main_layout.addWidget(left_frame, 1)
        main_layout.addWidget(right_frame, 1)

        self.main_layout.addWidget(main_widget)

    def toggle_play_pause(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.play_pause_btn.setText("▶ Play")
        else:
            self.media_player.play()
            self.play_pause_btn.setText("⏸ Pause")

    def update_speed(self):
        speed = self.speed_slider.value() / 100.0
        self.speed_label.setText(f"⚡ {speed:.2f}x")
        self.media_player.setPlaybackRate(speed)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.loading_spinner:
            video_rect = self.video_widget.geometry()
            spinner_x = video_rect.x() + (video_rect.width() - self.loading_spinner.width()) // 2
            spinner_y = video_rect.y() + (video_rect.height() - self.loading_spinner.height()) // 2
            self.loading_spinner.move(spinner_x, spinner_y)
            self.animation_label.move(spinner_x, spinner_y + self.loading_spinner.height() + 10)

    def show_loading_animation(self):
        if not self.loading_movie.isValid():
            print("Error: Loading GIF is not valid or not found.")
            return

        # Center the spinner on the video widget
        video_rect = self.video_widget.geometry()
        spinner_x = video_rect.x() + (video_rect.width() - self.loading_spinner.width()) // 2
        spinner_y = video_rect.y() + (video_rect.height() - self.loading_spinner.height()) // 2
        self.loading_spinner.move(spinner_x, spinner_y)
        
        # Ensure the spinner is visible and on top
        self.loading_spinner.setStyleSheet("background-color: transparent;")
        self.loading_spinner.raise_()  # Bring to the front
        self.loading_spinner.show()
        self.loading_movie.start()
        
        # Debugging: Check if the GIF is playing
        if self.loading_movie.state() == QMovie.Running:
            print("GIF is playing")
        else:
            print("GIF is not playing")
        
        # Start the animation text timer
        self.animation_timer.start(500)
        print("Loading animation shown")

    def hide_loading_animation(self):
        if self.loading_spinner.isVisible():  # Only hide if currently visible
            self.loading_movie.stop()
            self.loading_spinner.hide()
            self.animation_timer.stop()
            print("Loading animation hidden")

    def update_animation(self):
        self.animation_index = (self.animation_index + 1) % len(self.animation_text)
        self.animation_label.setText(self.animation_text[self.animation_index])

    def handle_media_status(self, status):
        # Debugging: Print the media status
        print(f"Media status: {status}")

        if status == QMediaPlayer.MediaStatus.LoadingMedia:
            if not self.is_loading:  # Only show if not already loading
                self.is_loading = True
                self.show_loading_animation()
        elif status in [QMediaPlayer.MediaStatus.LoadedMedia, QMediaPlayer.MediaStatus.BufferedMedia]:
            if self.is_loading:  # Only hide if currently loading
                # Delay hiding the animation by 1 second
                self.hide_animation_timer.start(1000)  # 1000 ms = 1 second
                self.is_loading = False

    def send_text(self):
        if self.is_processing:
            return
            
        self.is_processing = True
        self.show_loading_animation()
        
        # Stop current playback
        self.media_player.stop()
        self.media_player.setSource("")
        
        # Process in background
        QTimer.singleShot(0, self._process_text)

    def _process_text(self):
        try:
            text = self.text_input.toPlainText()
            if not text.strip():
                return
                
            output_path = text_to_sign(text, self.video_names, self.dataset_path)
            
            if output_path and os.path.exists(output_path):
                video_url = QUrl.fromLocalFile(os.path.abspath(output_path))
                self.media_player.setSource(video_url)
                self.media_player.play()
                self.play_pause_btn.setText("⏸ Pause")
        finally:
            self.is_processing = False
            self.hide_loading_animation()

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