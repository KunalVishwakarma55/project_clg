import sys
import cv2
import pyttsx3
from googletrans import Translator
import numpy as np
import math
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QFrame
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap, QFont
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier


# Detection Logic Class
class SignLanguageDetector:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.cap = cv2.VideoCapture(0)
        self.detector = HandDetector(maxHands=1)
        self.classifier = Classifier("sign-to-text/Model/keras_model.h5", "sign-to-text/Model/labels.txt")
        self.offset = 20
        self.imgSize = 300
        self.labels = ["A", "B", "C", "D", "E", "F", "G", "H"]
        self.sentence = ""
        self.current_sign = ""

    def detect_sign(self):
        success, img = self.cap.read()
        if not success:
            return None, None

        imgOutput = img.copy()
        hands, img = self.detector.findHands(img)

        if hands:
            hand = hands[0]
            x, y, w, h = hand['bbox']
            imgWhite = np.ones((self.imgSize, self.imgSize, 3), np.uint8) * 255

            imgCrop = img[y - self.offset:y + h + self.offset, x - self.offset:x + w + self.offset]
            aspectRatio = h / w

            try:
                if aspectRatio > 1:
                    k = self.imgSize / h
                    wCal = math.ceil(k * w)
                    imgResize = cv2.resize(imgCrop, (wCal, self.imgSize))
                    wGap = math.ceil((self.imgSize - wCal) / 2)
                    imgWhite[:, wGap:wCal + wGap] = imgResize
                else:
                    k = self.imgSize / w
                    hCal = math.ceil(k * h)
                    imgResize = cv2.resize(imgCrop, (self.imgSize, hCal))
                    hGap = math.ceil((self.imgSize - hCal) / 2)
                    imgWhite[hGap:hCal + hGap, :] = imgResize

                prediction, index = self.classifier.getPrediction(imgWhite, draw=False)
                self.current_sign = self.labels[index]
            except:
                self.current_sign = ""
        else:
            self.current_sign = ""

        return imgOutput, self.current_sign

    def speak(self):
        if self.sentence:
            self.engine.say(self.sentence)
            self.engine.runAndWait()

    def translate_sentence(self, target_lang):
        translator = Translator()
        return translator.translate(self.sentence, src='en', dest=target_lang).text

    def release_resources(self):
        self.cap.release()


# UI Class
class SignLanguageApp(QWidget):
    def __init__(self):
        super().__init__()
        self.detector = SignLanguageDetector()
        self.init_ui()
        self.detecting = False

    def init_ui(self):
        self.setWindowTitle("Sign Language To Text Conversion")
        self.setGeometry(0, 0, 1920, 1080)

        # Main Layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Navbar
        self.create_navbar()

        # Video and Detection
        self.video_label = QLabel()
        self.video_label.setFixedSize(640, 480)
        self.video_label.setStyleSheet("border: 5px solid #2980b9; background-color: rgba(0, 0, 0, 0.6);")
        self.main_layout.addWidget(self.video_label)

        self.detected_sign_label = QLabel("Character: ")
        self.detected_sign_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.detected_sign_label.setStyleSheet("color: #ecf0f1; background-color: rgba(44, 62, 80, 0.7); padding: 10px;")
        self.main_layout.addWidget(self.detected_sign_label)

        self.sentence_label = QLabel("Sentence: ")
        self.sentence_label.setFont(QFont("Arial", 18))
        self.sentence_label.setStyleSheet("color: #ecf0f1; background-color: rgba(44, 62, 80, 0.7); padding: 10px;")
        self.main_layout.addWidget(self.sentence_label)

        # Control Buttons
        self.create_controls()

        # Translation
        self.create_translation_controls()

        # Timer for detection
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)

    def create_navbar(self):
        navbar = QFrame()
        navbar.setStyleSheet("""
            QFrame {
                background-color: white;
                min-height: 50px;
                max-height: 50px;
            }
        """)
        navbar_layout = QHBoxLayout(navbar)
        self.main_layout.addWidget(navbar)

        logo_label = QLabel()
        logo_pixmap = QPixmap("C:/Users/Ravi/Desktop/College_project/assets/logo.png")
        scaled_logo = logo_pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(scaled_logo)
        navbar_layout.addWidget(logo_label)

        title_label = QLabel("Sign Interpreter")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        navbar_layout.addWidget(title_label)

    def create_controls(self):
        controls_layout = QHBoxLayout()

        button_style = "font: 14px Arial; background-color: #2980b9; color: white; padding: 10px; border-radius: 5px;"

        save_button = QPushButton("Save Sign")
        save_button.setStyleSheet(button_style)
        save_button.clicked.connect(self.save_sign)
        controls_layout.addWidget(save_button)

        space_button = QPushButton("Space")
        space_button.setStyleSheet(button_style)
        space_button.clicked.connect(self.add_space)
        controls_layout.addWidget(space_button)

        remove_button = QPushButton("Remove Last")
        remove_button.setStyleSheet(button_style)
        remove_button.clicked.connect(self.remove_last)
        controls_layout.addWidget(remove_button)

        clear_button = QPushButton("Clear")
        clear_button.setStyleSheet(button_style)
        clear_button.clicked.connect(self.clear_sentence)
        controls_layout.addWidget(clear_button)

        speak_button = QPushButton("Speak")
        speak_button.setStyleSheet(button_style)
        speak_button.clicked.connect(self.speak_sentence)
        controls_layout.addWidget(speak_button)

        start_button = QPushButton("Start")
        start_button.setStyleSheet(button_style)
        start_button.clicked.connect(self.start_detection)
        controls_layout.addWidget(start_button)

        stop_button = QPushButton("Stop")
        stop_button.setStyleSheet(button_style)
        stop_button.clicked.connect(self.stop_detection)
        stop_button.setDisabled(True)
        controls_layout.addWidget(stop_button)

        self.main_layout.addLayout(controls_layout)

    def create_translation_controls(self):
        translate_layout = QVBoxLayout()

        self.language_combobox = QComboBox()
        self.language_combobox.addItem("Select Language")
        self.language_combobox.addItem("Hindi")
        self.language_combobox.addItem("Marathi")
        self.language_combobox.setStyleSheet("font: 14px Arial; background-color: rgba(44, 62, 80, 0.7); color: #ecf0f1;")
        translate_layout.addWidget(self.language_combobox)

        self.translated_sentence_label = QLabel("Translated Sentence: ")
        self.translated_sentence_label.setFont(QFont("Arial", 18))
        self.translated_sentence_label.setStyleSheet("color: #ecf0f1; background-color: rgba(44, 62, 80, 0.7); padding: 10px;")
        translate_layout.addWidget(self.translated_sentence_label)

        translate_button = QPushButton("Translate")
        translate_button.setStyleSheet("font: 14px Arial; background-color: #2980b9; color: white; padding: 10px; border-radius: 5px;")
        translate_button.clicked.connect(self.translate_sentence)
        translate_layout.addWidget(translate_button)

        self.main_layout.addLayout(translate_layout)

    def update_frame(self):
        if self.detecting:
            img, sign = self.detector.detect_sign()
            if img is not None:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                h, w, c = img.shape
                bytes_per_line = c * w
                q_image = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_image)
                self.video_label.setPixmap(pixmap)

            self.detected_sign_label.setText(f"Character: {sign}")

    def save_sign(self):
        if self.detector.current_sign:
            self.detector.sentence += self.detector.current_sign
            self.sentence_label.setText(f"Sentence: {self.detector.sentence}")

    def add_space(self):
        self.detector.sentence += " "
        self.sentence_label.setText(f"Sentence: {self.detector.sentence}")

    def remove_last(self):
        self.detector.sentence = self.detector.sentence[:-1]
        self.sentence_label.setText(f"Sentence: {self.detector.sentence}")

    def clear_sentence(self):
        self.detector.sentence = ""
        self.sentence_label.setText("Sentence: ")

    def speak_sentence(self):
        self.detector.speak()

    def translate_sentence(self):
        target_language = self.language_combobox.currentText()
        if target_language in ["Hindi", "Marathi"]:
            lang_code = "hi" if target_language == "Hindi" else "mr"
            translated = self.detector.translate_sentence(lang_code)
            self.translated_sentence_label.setText(f"Translated Sentence: {translated}")
        else:
            self.translated_sentence_label.setText("Select a valid language!")

    def start_detection(self):
        self.detecting = True

    def stop_detection(self):
        self.detecting = False


# Main App
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SignLanguageApp()
    window.show()
    app.exec()
