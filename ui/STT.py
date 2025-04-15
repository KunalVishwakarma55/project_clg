import sys
import cv2
import pyttsx3
import numpy as np
import math
from googletrans import Translator
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QLabel, QPushButton, QFrame, QComboBox, QButtonGroup)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QFont, QPixmap, QImage
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier

class SignLanguageDetector:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.cap = cv2.VideoCapture(0)
        self.detector = HandDetector(maxHands=1)
        self.classifier = Classifier("sign-to-text/Model/keras_model.h5", "sign-to-text/Model/labels.txt")
        self.offset = 20
        self.imgSize = 300
        self.labels = ["A", "B", "C", "D", "E", "F", "G", "H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
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

class STT(QMainWindow):
    def __init__(self):
        super().__init__()
        self.detector = SignLanguageDetector()
        self.detecting = False
        
        # UI Setup
        self.setWindowTitle("Sign Language Interpreter")
        self.setMinimumSize(1091, 672)
        self.setFont(QFont("Segoe UI", 15))
        self.setStyleSheet("background-color: #f0f2f5;")
        
        # Style definitions
        self.nav_button_style = """
            QPushButton {
                background-color: transparent;
                color: #1a1a1a;
                border: none;
                padding: 12px 24px;
                font-size: 15px;
                font-weight: 600;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                color: #2962ff;
                background-color: #f5f5f5;
                border-radius: 6px;
            }
            QPushButton:checked {
                color: #2962ff;
                border-bottom: 3px solid #2962ff;
                font-weight: 700;
            }
        """

        self.button_style = """
            QPushButton {
                background-color: #2962ff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                font-family: 'Segoe UI';
            }
            QPushButton:hover {
                background-color: #1e88e5;
            }
            QPushButton:pressed {
                background-color: #1565c0;
            }
        """

        self.frame_style = """
            QFrame {
                background-color: white;
                border-radius: 10px;
            }
        """
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        
        self.create_main_content()
        
        # Setup detection timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)

     

    def create_main_content(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # Left frame (Camera section)
        left_frame = QFrame()
        left_frame.setStyleSheet(self.frame_style)
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(20)

        # Camera header
        camera_header = QHBoxLayout()
        camera_icon = QLabel("📹")
        camera_icon.setStyleSheet("font-size: 30px; color: #2962ff;")
        camera_label = QLabel("Live Camera Feed")
        camera_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a1a1a; margin-left: 10px;")
        camera_label.setFixedHeight(50)
        camera_header.addWidget(camera_icon)
        camera_header.addWidget(camera_label)
        camera_header.addStretch()

        # Camera feed
        self.camera_feed = QLabel()
        self.camera_feed.setObjectName("camera_feed")
        self.camera_feed.setMinimumSize(480, 330)
        self.camera_feed.setMaximumSize(800, 500)
        self.camera_feed.setStyleSheet("""
            background-color: #f0f2f5;
            border: 2px solid #ccc;
            border-radius: 8px;
            color: #666;
            font-size: 18px;
            text-align: center;
        """)
        self.camera_feed.setAlignment(Qt.AlignCenter)

        # Camera controls
        camera_buttons = QHBoxLayout()
        camera_buttons.setSpacing(20)

        start_btn = QPushButton("▶ Start Camera")
        stop_btn = QPushButton("⏹ Stop Camera")
        
        start_btn.setStyleSheet(self.button_style)
        stop_btn.setStyleSheet(self.button_style.replace("#2962ff", "#dc3545"))
        
        start_btn.setFixedWidth(180)
        stop_btn.setFixedWidth(180)
        
        start_btn.clicked.connect(self.start_camera)
        
        stop_btn.clicked.connect(self.stop_camera)

        camera_buttons.addStretch()
        camera_buttons.addWidget(start_btn)
        camera_buttons.addWidget(stop_btn)
        camera_buttons.addStretch()

        left_layout.addLayout(camera_header)
        left_layout.addWidget(self.camera_feed)
        left_layout.addLayout(camera_buttons)

        # Right frame
        right_frame = QFrame()
        right_frame.setStyleSheet(self.frame_style)
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(20)

        # Character, Sentence, and Translated sections
        sections = [
            ("Character", "🔤", "char_content"),
            ("Sentence", "📝", "sentence_content"),
            ("Translated Sentence", "🌐", "translated_content")
        ]

        for section, icon, content_name in sections:
            frame = QFrame()
            frame.setStyleSheet("""
                QFrame {
                    background-color: #f0f0f0;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            
            section_layout = QVBoxLayout(frame)
            header = QHBoxLayout()
            
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 20px;")
            
            title = QLabel(section)
            title.setStyleSheet("font-size: 16px; font-weight: 600; color: #1a1a1a;")
            
            header.addWidget(icon_label)
            header.addWidget(title)
            header.addStretch()

            content = QLabel("")
            content.setObjectName(content_name)
            content.setStyleSheet("""
                color: #495057;
                min-height: 50px;
                background-color: #f0f0f0;
                border-radius: 6px;
                padding: 10px;
            """)
            
            section_layout.addLayout(header)
            section_layout.addWidget(content)
            right_layout.addWidget(frame)

        # Control buttons
        control_buttons = QHBoxLayout()
        buttons = [
            ("💾 Save", "#2962ff", self.save_sign),
            ("⌨️ Space", "#2962ff", self.add_space),
            ("⌫ Backspace", "#ff5722", self.remove_last),
            ("🗑️ Clear", "#dc3545", self.clear_sentence),
            ("🔄 Translate", "#2962ff", self.translate_text)
        ]

        for text, color, callback in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(self.button_style.replace("#2962ff", color))
            btn.clicked.connect(callback)
            control_buttons.addWidget(btn)

        # Language selection
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Select Language", "Hindi", "Marathi"])
        # Replace the existing lang_combo styling with this:
        self.lang_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 2px solid #2962ff;
                border-radius: 6px;
                padding: 8px;
                min-width: 150px;
                font-weight: 600;
                color: #1a1a1a;  /* Changed from #2962ff to #1a1a1a for better visibility */
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
                image: url(down-arrow.png);  /* You can add a custom arrow image */
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 2px solid #2962ff;
                border-radius: 6px;
                selection-background-color: #2962ff;
                selection-color: white;
                color: #1a1a1a;  /* Text color for dropdown items */
                padding: 4px;
            }
        """)

        control_buttons.addWidget(self.lang_combo)

        right_layout.addLayout(control_buttons)

        main_layout.addWidget(left_frame, 1)
        main_layout.addWidget(right_frame, 1)
        self.main_layout.addWidget(main_widget)

    def update_frame(self):
        if self.detecting:
            img, sign = self.detector.detect_sign()
            if img is not None:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                h, w, c = img.shape
                bytes_per_line = c * w
                q_image = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_image)
                self.camera_feed.setPixmap(pixmap.scaled(self.camera_feed.size(), Qt.KeepAspectRatio))
                
                char_label = self.findChild(QLabel, "char_content")
                if char_label:
                    char_label.setText(sign)

    def start_camera(self):
        print("Starting camera...")
        if not self.detector.cap.isOpened():
            self.detector.cap = cv2.VideoCapture(0)
            if not self.detector.cap.isOpened():
                print("Failed to open camera")
                return
        print("Camera opened successfully")
        self.detecting = True


    def stop_camera(self):
        self.detecting = False

    def save_sign(self):
        if self.detector.current_sign:
            self.detector.sentence += self.detector.current_sign
            sentence_label = self.findChild(QLabel, "sentence_content")
            if sentence_label:
                sentence_label.setText(self.detector.sentence)

    def add_space(self):
        self.detector.sentence += " "
        sentence_label = self.findChild(QLabel, "sentence_content")
        if sentence_label:
            sentence_label.setText(self.detector.sentence)

    def remove_last(self):
        self.detector.sentence = self.detector.sentence[:-1]
        sentence_label = self.findChild(QLabel, "sentence_content")
        if sentence_label:
            sentence_label.setText(self.detector.sentence)

    def clear_sentence(self):
        self.detector.sentence = ""
        sentence_label = self.findChild(QLabel, "sentence_content")
        translated_label = self.findChild(QLabel, "translated_content")
        if sentence_label:
            sentence_label.setText("")
        if translated_label:
            translated_label.setText("")

    def translate_text(self):
        if self.detector.sentence:
            target_language = self.lang_combo.currentText()
            if target_language in ["Hindi", "Marathi"]:
                lang_code = "hi" if target_language == "Hindi" else "mr"
                translated = self.detector.translate_sentence(lang_code)
                translated_label = self.findChild(QLabel, "translated_content")
                if translated_label:
                    translated_label.setText(translated)

    def closeEvent(self, event):
        self.detector.release_resources()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = STT()
    window.show()
    sys.exit(app.exec())

