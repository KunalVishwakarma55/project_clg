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

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()

# Initialize the camera, hand detector, and classifier
cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1)
classifier = Classifier("Model/keras_model.h5", "Model/labels.txt")

# Initialize Translator
translator = Translator()

# Parameters
offset = 20
imgSize = 300
labels = ["A", "B", "C", "D","E","F","G","H"]
sentence = ""  # To store the concatenated sentence
current_sign = ""  # To store the detected character
detecting = False  # Flag to indicate if detection is running

# Function to detect sign language
def detect_sign():
    global current_sign, img_frame
    if not detecting:  # Stop detection if the flag is False
        return
    success, img = cap.read()
    if not success:
        return

    imgOutput = img.copy()
    hands, img = detector.findHands(img)

    if hands:
        hand = hands[0]
        x, y, w, h = hand['bbox']
        imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255

        imgCrop = img[y - offset:y + h + offset, x - offset:x + w + offset]
        aspectRatio = h / w

        try:
            if aspectRatio > 1:
                k = imgSize / h
                wCal = math.ceil(k * w)
                imgResize = cv2.resize(imgCrop, (wCal, imgSize))
                wGap = math.ceil((imgSize - wCal) / 2)
                imgWhite[:, wGap:wCal + wGap] = imgResize
            else:
                k = imgSize / w
                hCal = math.ceil(k * h)
                imgResize = cv2.resize(imgCrop, (imgSize, hCal))
                hGap = math.ceil((imgSize - hCal) / 2)
                imgWhite[hGap:hCal + hGap, :] = imgResize

            prediction, index = classifier.getPrediction(imgWhite, draw=False)
            current_sign = labels[index]
        except:
            current_sign = ""
    else:
        current_sign = ""

    # Convert the OpenCV frame (BGR) to a format compatible with PySide6
    img_frame = cv2.cvtColor(imgOutput, cv2.COLOR_BGR2RGB)
    h, w, c = img_frame.shape
    bytes_per_line = c * w
    q_image = QImage(img_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(q_image)

    # Update the video feed
    video_label.setPixmap(pixmap)

    # Update the detected sign
    detected_sign_label.setText(f"Character: {current_sign}")

# Function to save the current sign to the sentence
def save_sign():
    global sentence, current_sign
    if current_sign:  # Save only if there's a detected sign
        sentence += current_sign
        sentence_label.setText(f"Sentence: {sentence}")

# Function to add a space to the sentence
def add_space():
    global sentence
    sentence += " "  # Add a space to the sentence
    sentence_label.setText(f"Sentence: {sentence}")

# Function to remove the last character from the sentence
def remove_last():
    global sentence
    sentence = sentence[:-1]  # Remove the last character
    sentence_label.setText(f"Sentence: {sentence}")

# Function to clear the sentence
def clear_sentence():
    global sentence
    sentence = ""
    sentence_label.setText("Sentence: ")

# Function to speak the sentence
def speak_sentence():
    if sentence:
        engine.say(sentence)
        engine.runAndWait()

# Function to translate the sentence based on selected language
def translate():
    global sentence
    selected_language = language_combobox.currentText()
    if sentence:
        if selected_language == "Hindi":
            translated = translator.translate(sentence, src='en', dest='hi')
            translated_sentence_label.setText(f"Translated Sentence (Hindi): {translated.text}")
        elif selected_language == "Marathi":
            translated = translator.translate(sentence, src='en', dest='mr')
            translated_sentence_label.setText(f"Translated Sentence (Marathi): {translated.text}")
        else:
            translated_sentence_label.setText("Please select a language")

# Function to start sign detection
def start_detection():
    global detecting
    detecting = True
    start_button.setDisabled(True)
    stop_button.setEnabled(True)

# Function to stop sign detection
def stop_detection():
    global detecting
    detecting = False
    start_button.setEnabled(True)
    stop_button.setDisabled(True)

# PySide6 GUI Setup
app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("Sign Language To Text Conversion")

# Set window size to fullscreen
window.setGeometry(0, 0, 1920, 1080)

# Layouts
main_layout = QVBoxLayout()
video_layout = QVBoxLayout()
controls_layout = QHBoxLayout()
translate_layout = QVBoxLayout()

# Background Image (Full screen)
background = QPixmap("background.jpg")
background_label = QLabel(window)
background_label.setPixmap(background)
background_label.setScaledContents(True)
background_label.setGeometry(0, 0, window.width(), window.height())  # Make the background cover the full window

# Video Feed
video_label = QLabel()
video_label.setFixedSize(640, 480)
video_label.setStyleSheet("border: 5px solid #2980b9; background-color: rgba(0, 0, 0, 0.6);")
video_layout.addWidget(video_label)

# Detected Character
detected_sign_label = QLabel("Character: ")
detected_sign_label.setFont(QFont("Arial", 18, QFont.Bold))
detected_sign_label.setStyleSheet("color: #ecf0f1; background-color: rgba(44, 62, 80, 0.7); padding: 10px;")
main_layout.addWidget(detected_sign_label)

# Detected Sentence
sentence_label = QLabel("Sentence: ")
sentence_label.setFont(QFont("Arial", 18))
sentence_label.setStyleSheet("color: #ecf0f1; background-color: rgba(44, 62, 80, 0.7); padding: 10px;")
main_layout.addWidget(sentence_label)

# Language Dropdown
language_combobox = QComboBox()
language_combobox.addItem("Select Language")
language_combobox.addItem("Hindi")
language_combobox.addItem("Marathi")
language_combobox.setStyleSheet("font: 14px Arial; background-color: rgba(44, 62, 80, 0.7); color: #ecf0f1;")
translate_layout.addWidget(language_combobox)

# Translated Sentence
translated_sentence_label = QLabel("Translated Sentence: ")
translated_sentence_label.setFont(QFont("Arial", 18))
translated_sentence_label.setStyleSheet("color: #ecf0f1; background-color: rgba(44, 62, 80, 0.7); padding: 10px;")
translate_layout.addWidget(translated_sentence_label)

# Buttons
button_style = "font: 14px Arial; background-color: #2980b9; color: white; padding: 10px; border-radius: 5px;"
save_button = QPushButton("Save Sign")
save_button.setStyleSheet(button_style)
save_button.clicked.connect(save_sign)
controls_layout.addWidget(save_button)

space_button = QPushButton("Space")
space_button.setStyleSheet(button_style)
space_button.clicked.connect(add_space)
controls_layout.addWidget(space_button)

remove_button = QPushButton("Remove Last")
remove_button.setStyleSheet(button_style)
remove_button.clicked.connect(remove_last)
controls_layout.addWidget(remove_button)

clear_button = QPushButton("Clear")
clear_button.setStyleSheet(button_style)
clear_button.clicked.connect(clear_sentence)
controls_layout.addWidget(clear_button)

speak_button = QPushButton("Speak")
speak_button.setStyleSheet(button_style)
speak_button.clicked.connect(speak_sentence)
controls_layout.addWidget(speak_button)

translate_button = QPushButton("Translate")
translate_button.setStyleSheet(button_style)
translate_button.clicked.connect(translate)
controls_layout.addWidget(translate_button)

# Start and Stop Buttons
start_button = QPushButton("Start")
start_button.setStyleSheet(button_style)
start_button.clicked.connect(start_detection)
controls_layout.addWidget(start_button)

stop_button = QPushButton("Stop")
stop_button.setStyleSheet(button_style)
stop_button.clicked.connect(stop_detection)
stop_button.setDisabled(True)  # Disable Stop button initially
controls_layout.addWidget(stop_button)

# Add all layouts to the main window
main_layout.addLayout(video_layout)
main_layout.addLayout(controls_layout)
main_layout.addLayout(translate_layout)

# Set the layout for the window
window.setLayout(main_layout)

# Set a timer to continuously update the video feed
timer = QTimer()
timer.timeout.connect(detect_sign)
timer.start(10)  # Update every 10 milliseconds

# Show the window
window.show()

# Start the application event loop
sys.exit(app.exec())

