import sys
import cv2
import pyttsx3
from googletrans import Translator
import numpy as np
import math
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap, QFont
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier

# Sign Detection Logic
class SignDetector:
    def __init__(self, model_path, labels_path, img_size=300, offset=20):
        self.detector = HandDetector(maxHands=1)
        self.classifier = Classifier(model_path, labels_path)
        self.img_size = img_size
        self.offset = offset
        self.labels = ["A", "B", "C", "D", "E", "F", "G", "H"]

    def detect(self, img):
        hands, img = self.detector.findHands(img)
        current_sign = ""

        if hands:
            hand = hands[0]
            x, y, w, h = hand['bbox']
            img_white = np.ones((self.img_size, self.img_size, 3), np.uint8) * 255

            img_crop = img[y - self.offset:y + h + self.offset, x - self.offset:x + w + self.offset]
            aspect_ratio = h / w

            try:
                if aspect_ratio > 1:
                    k = self.img_size / h
                    w_cal = math.ceil(k * w)
                    img_resize = cv2.resize(img_crop, (w_cal, self.img_size))
                    w_gap = math.ceil((self.img_size - w_cal) / 2)
                    img_white[:, w_gap:w_cal + w_gap] = img_resize
                else:
                    k = self.img_size / w
                    h_cal = math.ceil(k * h)
                    img_resize = cv2.resize(img_crop, (self.img_size, h_cal))
                    h_gap = math.ceil((self.img_size - h_cal) / 2)
                    img_white[h_gap:h_cal + h_gap, :] = img_resize

                prediction, index = self.classifier.getPrediction(img_white, draw=False)
                current_sign = self.labels[index]
            except:
                pass

        return current_sign, img

# PySide6 UI
class SignLanguageApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sign Language To Text Conversion")
        self.setGeometry(0, 0, 1920, 1080)

        # Initialize components
        self.engine = pyttsx3.init()
        self.translator = Translator()
        self.cap = cv2.VideoCapture(0)
        self.detector = SignDetector("Model/keras_model.h5", "Model/labels.txt")

        self.sentence = ""
        self.current_sign = ""
        self.detecting = False

        # Layouts
        self.main_layout = QVBoxLayout()
        self.video_layout = QVBoxLayout()
        self.controls_layout = QHBoxLayout()
        self.translate_layout = QVBoxLayout()

        self.init_ui()

        # Timer for video feed
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_video_feed)
        self.timer.start(10)

    def init_ui(self):
        # Video Feed
        self.video_label = QLabel()
        self.video_label.setFixedSize(640, 480)
        self.video_label.setStyleSheet("border: 5px solid #2980b9; background-color: rgba(0, 0, 0, 0.6);")
        self.video_layout.addWidget(self.video_label)

        # Detected Character
        self.detected_sign_label = QLabel("Character: ")
        self.detected_sign_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.detected_sign_label.setStyleSheet("color: #ecf0f1; background-color: rgba(44, 62, 80, 0.7); padding: 10px;")
        self.main_layout.addWidget(self.detected_sign_label)

        # Sentence Label
        self.sentence_label = QLabel("Sentence: ")
        self.sentence_label.setFont(QFont("Arial", 18))
        self.sentence_label.setStyleSheet("color: #ecf0f1; background-color: rgba(44, 62, 80, 0.7); padding: 10px;")
        self.main_layout.addWidget(self.sentence_label)

        # Language Dropdown
        self.language_combobox = QComboBox()
        self.language_combobox.addItem("Select Language")
        self.language_combobox.addItem("Hindi")
        self.language_combobox.addItem("Marathi")
        self.language_combobox.setStyleSheet("font: 14px Arial; background-color: rgba(44, 62, 80, 0.7); color: #ecf0f1;")
        self.translate_layout.addWidget(self.language_combobox)

        # Translated Sentence
        self.translated_sentence_label = QLabel("Translated Sentence: ")
        self.translated_sentence_label.setFont(QFont("Arial", 18))
        self.translated_sentence_label.setStyleSheet("color: #ecf0f1; background-color: rgba(44, 62, 80, 0.7); padding: 10px;")
        self.translate_layout.addWidget(self.translated_sentence_label)

        # Buttons
        button_style = "font: 14px Arial; background-color: #2980b9; color: white; padding: 10px; border-radius: 5px;"

        save_button = QPushButton("Save Sign")
        save_button.setStyleSheet(button_style)
        save_button.clicked.connect(self.save_sign)
        self.controls_layout.addWidget(save_button)

        space_button = QPushButton("Space")
        space_button.setStyleSheet(button_style)
        space_button.clicked.connect(self.add_space)
        self.controls_layout.addWidget(space_button)

        remove_button = QPushButton("Remove Last")
        remove_button.setStyleSheet(button_style)
        remove_button.clicked.connect(self.remove_last)
        self.controls_layout.addWidget(remove_button)

        clear_button = QPushButton("Clear")
        clear_button.setStyleSheet(button_style)
        clear_button.clicked.connect(self.clear_sentence)
        self.controls_layout.addWidget(clear_button)

        speak_button = QPushButton("Speak")
        speak_button.setStyleSheet(button_style)
        speak_button.clicked.connect(self.speak_sentence)
        self.controls_layout.addWidget(speak_button)

        translate_button = QPushButton("Translate")
        translate_button.setStyleSheet(button_style)
        translate_button.clicked.connect(self.translate)
        self.controls_layout.addWidget(translate_button)

        start_button = QPushButton("Start")
        start_button.setStyleSheet(button_style)
        start_button.clicked.connect(self.start_detection)
        self.controls_layout.addWidget(start_button)

        stop_button = QPushButton("Stop")
        stop_button.setStyleSheet(button_style)
        stop_button.clicked.connect(self.stop_detection)
        self.controls_layout.addWidget(stop_button)
        stop_button.setDisabled(True)

        # Add layouts to main layout
        self.main_layout.addLayout(self.video_layout)
        self.main_layout.addLayout(self.controls_layout)
        self.main_layout.addLayout(self.translate_layout)

        # Set main layout
        self.setLayout(self.main_layout)

    def update_video_feed(self):
        if not self.detecting:
            return

        success, img = self.cap.read()
        if success:
            self.current_sign, processed_img = self.detector.detect(img)
            h, w, c = processed_img.shape
            bytes_per_line = c * w
            q_image = QImage(processed_img.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.video_label.setPixmap(pixmap)

            self.detected_sign_label.setText(f"Character: {self.current_sign}")

    def save_sign(self):
        if self.current_sign:
            self.sentence += self.current_sign
            self.sentence_label.setText(f"Sentence: {self.sentence}")

    def add_space(self):
        self.sentence += " "
        self.sentence_label.setText(f"Sentence: {self.sentence}")

    def remove_last(self):
        self.sentence = self.sentence[:-1]
        self.sentence_label.setText(f"Sentence: {self.sentence}")

    def clear_sentence(self):
        self.sentence = ""
        self.sentence_label.setText("Sentence: ")

    def speak_sentence(self):
        if self.sentence:
            self.engine.say(self.sentence)
            self.engine.runAndWait()

    def translate(self):
        selected_language = self.language_combobox.currentText()
        if self.sentence:
            if selected_language == "Hindi":
                translated = self.translator.translate(self.sentence, src='en', dest='hi')
                self.translated_sentence_label.setText(f"Translated Sentence (Hindi): {translated.text}")
            elif selected_language == "Marathi":
                translated = self.translator.translate(self.sentence, src='en', dest='mr')
                self.translated_sentence_label.setText(f"Translated Sentence (Marathi): {translated.text}")
            else:
                self.translated_sentence_label.setText("Please select a language")

    def start_detection(self):
        self.detecting = True

    def stop_detection(self):
        self.detecting = False

# Main
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SignLanguageApp()
    window.show()
    sys.exit(app.exec())
