import pygame
import sys
import cv2
import os
import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QLabel, QFileDialog, QVBoxLayout, QWidget
from moviepy.editor import VideoFileClip, concatenate_videoclips

# Initialize NLTK components
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

# Helper functions (same as in your original code)
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
    else:
        return None

# PySide6 GUI application
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Urdu Text to Sign Language")
        
        self.layout = QVBoxLayout()

        # Input field
        self.input_label = QLabel("Enter text:")
        self.input_field = QLineEdit()
        self.layout.addWidget(self.input_label)
        self.layout.addWidget(self.input_field)

        # Generate button
        self.generate_button = QPushButton("Generate Video")
        self.generate_button.clicked.connect(self.generate_video)
        self.layout.addWidget(self.generate_button)

        # Set central widget
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        # Dataset
        self.dataset_path = "Dataset"
        self.videos = os.listdir(self.dataset_path)
        self.video_names = [os.path.splitext(video)[0].replace("-", " ").lower() for video in self.videos]

    def generate_video(self):
        text = self.input_field.text()
        output_path = text_to_sign(text, self.video_names, self.dataset_path)
        if output_path:
            # Use pygame to play the generated video
            pygame.init()
            screen = pygame.display.set_mode((640, 480))  # Set the display screen size
            clock = pygame.time.Clock()

            # Load the video using OpenCV
            cap = cv2.VideoCapture(output_path)

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                # Convert frame to RGB (pygame requires RGB format)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Convert the frame to a surface
                frame_surface = pygame.surfarray.make_surface(frame)

                # Display the surface
                screen.blit(frame_surface, (0, 0))
                pygame.display.update()

                # Limit frame rate (30 FPS)
                clock.tick(30)

            cap.release()
            pygame.quit()

# Main function
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
