from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QLabel, QFrame, QProgressBar, QStackedWidget)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QUrl, QPropertyAnimation, QEasingCurve
from PySide6.QtCore import QPoint
import random

class BeginnerMode(QWidget):
    def __init__(self):

        super().__init__()
        self.score = 0
        self.current_letter = None
        self.letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        self.time_remaining = 30
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        self.questions_answered = 0
        self.correct_answers = 0
        
        # New tracking variables
        self.current_streak = 0
        self.best_streak = 0
        self.practice_mode = False
        self.stats = {
            'total_attempts': 0,
            'correct_answers': 0,
            'average_time': 0,
            'best_time': float('inf')
        }
        
        self.init_ui()
        self.load_new_question()
        self.setup_sounds()

    def update_timer(self):
        if not self.practice_mode:
            self.time_remaining -= 1
            self.timer_label.setText(f"Time: {self.time_remaining}s")
            if self.time_remaining <= 0:
                self.timer.stop()
                self.skip_question()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        
        # Left Frame with Image
        left_frame = QFrame()
        left_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 20px;
                margin: 15px;
                border: 2px solid #e0e0e0;
            }
        """)
        left_layout = QVBoxLayout(left_frame)
        
        # Stats Panel
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 15px;
                padding: 10px;
                margin: 10px;
            }
        """)
        stats_layout = QHBoxLayout(stats_frame)
        
        self.streak_label = QLabel("Streak: 0 🔥")
        self.best_streak_label = QLabel("Best: 0 ⭐")
        self.level_label = QLabel("Level: 1")
        
        for label in [self.streak_label, self.best_streak_label, self.level_label]:
            label.setStyleSheet("""
                font-size: 18px;
                color: #2c3e50;
                font-weight: bold;
                padding: 5px;
            """)
            stats_layout.addWidget(label)
        
        left_layout.addWidget(stats_frame)
        # Image Display Section
        image_title = QLabel("ASL Sign")
        image_title.setFixedHeight(65)
        image_title.setAlignment(Qt.AlignCenter)
        image_title.setStyleSheet("""
            font-size: 20px;
            color: #2c3e50;
            background-color: #f8f9fa;
            font-weight: bold;
            margin: 5px;
            padding: 5px;
        """)
        left_layout.addWidget(image_title)

        # Practice Mode Toggle
        practice_mode_btn = QPushButton("Practice Mode 📚")
        practice_mode_btn.setCheckable(True)
        practice_mode_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                margin: 5px;
            }
            QPushButton:checked {
                background-color: #27ae60;
            }
        """)
        practice_mode_btn.toggled.connect(self.toggle_practice_mode)
        left_layout.addWidget(practice_mode_btn)

        # Hint Button
        self.hint_button = QPushButton("Show Hint 💡")
        self.hint_button.setStyleSheet("""
            QPushButton {
                background-color: #f1c40f;
                color: white;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #f39c12;
            }
        """)
        self.hint_button.clicked.connect(self.show_hint)
        self.hint_button.hide()  # Initially hidden, shown in practice mode
        left_layout.addWidget(self.hint_button)
        # Image Frame
        image_frame = QFrame()
        image_frame.setStyleSheet("""
            QFrame {
                border: 3px solid #3498db;
                border-radius: 15px;
                padding: 0px;
                margin: 0px;
                background-color: white;
            }
        """)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(500, 500)
        self.image_label.setScaledContents(True)
        image_layout = QVBoxLayout(image_frame)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.addWidget(self.image_label)
        left_layout.addWidget(image_frame)

        # Right Frame
        right_frame = QFrame()
        right_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 20px;
                margin: 15px;
                border: 2px solid #e0e0e0;
            }
        """)
        right_layout = QVBoxLayout(right_frame)

        # Score and Progress Panel
        score_frame = QFrame()
        score_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 15px;
                padding: 10px;
                margin: 10px;
            }
        """)
        score_layout = QHBoxLayout(score_frame)
        # Score Label with Bonus Display
        self.score_label = QLabel(f"Score: {self.score}")
        self.score_label.setStyleSheet("""
            font-size: 22px;
            color: #2c3e50;
            font-weight: bold;
            padding: 5px;
        """)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 26)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3498db;
                border-radius: 8px;
                text-align: center;
                height: 25px;
                background-color: white;
                color: black;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 6px;
            }
        """)

        # Time Display with Bonus Indicator
        self.timer_label = QLabel("Time: 30s")
        self.timer_label.setStyleSheet("""
            font-size: 22px;
            color: #e74c3c;
            font-weight: bold;
            padding: 5px 15px;
            background-color: white;
            border-radius: 10px;
            border: 2px solid #e74c3c;
        """)

        # Bonus Label for Time Bonus Display
        self.bonus_label = QLabel("")
        self.bonus_label.setStyleSheet("""
            font-size: 18px;
            color: #27ae60;
            font-weight: bold;
            padding: 5px;
        """)
        # Add components to score layout
        score_layout.addWidget(self.score_label)
        score_layout.addWidget(self.progress_bar)
        score_layout.addWidget(self.timer_label)
        score_layout.addWidget(self.bonus_label)

        # Question Label
        question_label = QLabel("Which is the correct hand sign?")
        question_label.setAlignment(Qt.AlignCenter)
        question_label.setStyleSheet("""
            font-size: 24px;
            color: #2c3e50;
            font-weight: bold;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 12px;
            margin: 15px 10px;
        """)

        # Choice Buttons Setup
        choice_layout = QVBoxLayout()
        self.choice_buttons = []    
        choice_layout.setAlignment(Qt.AlignCenter)

        for _ in range(4):
            btn = QPushButton()
            btn.setFixedHeight(55)
            btn.setFixedWidth(550)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 12px;
                    font-size: 20px;
                    font-weight: bold;
                    margin: 6px;
                    padding: 5px;
                    border: 2px solid #2980b9;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            btn.clicked.connect(lambda checked, b=btn: self.check_answer(b.text()))
            self.choice_buttons.append(btn)
            choice_layout.addWidget(btn, 0, Qt.AlignCenter)
        # Skip Button
        self.skip_button = QPushButton("Skip →")
        self.skip_button.setFixedWidth(550)  # Matched with choice buttons
        self.skip_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
                padding: 10px 20px;
                margin: 10px;
                border: 2px solid #e67e22;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        self.skip_button.clicked.connect(self.skip_question)

        # Statistics Button
        stats_btn = QPushButton("View Statistics 📊")
        stats_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        stats_btn.clicked.connect(self.show_statistics)

        # Back Button
        back_btn = QPushButton("← Back to Modes")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
                border-radius: 12px;
                margin: 15px;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #7f8c8d;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        back_btn.clicked.connect(self.go_back_to_modes)

        # Assemble right layout
        right_layout.addWidget(score_frame)
        right_layout.addWidget(question_label)
        right_layout.addLayout(choice_layout)
        right_layout.addWidget(self.skip_button)
        right_layout.addWidget(stats_btn)
        right_layout.addStretch()
        right_layout.addWidget(back_btn)

        # Add frames to main layout
        main_layout.addWidget(left_frame, 1)
        main_layout.addWidget(right_frame, 1)

    def load_new_question(self):
        self.start_timer()
        self.current_letter = random.choice(self.letters)
        image_path = f"assets/asl_images/{self.current_letter.lower()}.png"
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap.scaled(450, 450, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        choices = [self.current_letter]
        while len(choices) < 4:
            choice = random.choice(self.letters)
            if choice not in choices:
                choices.append(choice)
        
        random.shuffle(choices)
        for btn, choice in zip(self.choice_buttons, choices):
            btn.setText(choice)

    def setup_sounds(self):
        self.correct_sound = QSoundEffect()
        self.correct_sound.setSource(QUrl.fromLocalFile("assets/sounds/correct.wav"))
        self.wrong_sound = QSoundEffect()
        self.wrong_sound.setSource(QUrl.fromLocalFile("assets/sounds/wrong.wav"))

    def check_answer(self, selected_letter):
        self.timer.stop()
        self.stats['total_attempts'] += 1
        
        if selected_letter == self.current_letter:
            self.handle_correct_answer(selected_letter)
        else:
            self.handle_wrong_answer(selected_letter)
        
        QTimer.singleShot(1000, self.reset_buttons_and_load_new)

    # Update the handle_correct_answer method to properly handle level updates
    def handle_correct_answer(self, selected_letter):
        self.correct_sound.play()
        self.current_streak += 1
        self.best_streak = max(self.current_streak, self.best_streak)
        
        # Calculate time bonus
        time_bonus = max(0, self.time_remaining)
        bonus_points = time_bonus * 2
        self.score += 10 + bonus_points
        
        # Update UI elements
        self.score_label.setText(f"Score: {self.score} ✨")
        self.streak_label.setText(f"Streak: {self.current_streak} 🔥")
        self.best_streak_label.setText(f"Best: {self.best_streak} ⭐")
        self.bonus_label.setText(f"+{bonus_points} Time Bonus!")
        
        current_progress = self.progress_bar.value()
        new_progress = current_progress + 1
        self.progress_bar.setValue(new_progress)
        self.progress_bar.setFormat(f"Progress: {new_progress}/26 Letters")
        
        # Show success emoji
        self.show_success_emoji()
        
        # Update statistics
        self.stats['correct_answers'] += 1
        response_time = 30 - self.time_remaining
        self.stats['average_time'] = (self.stats['average_time'] * 
                                    (self.stats['correct_answers']-1) + 
                                    response_time) / self.stats['correct_answers']
        self.stats['best_time'] = min(self.stats['best_time'], response_time)
        
        # Calculate and update level
        new_level = (new_progress // 5) + 1
        current_level = int(self.level_label.text().split(": ")[1])
        
        # Check if level has increased
        if new_level > current_level:
            self.show_level_transition(new_level)
            self.level_label.setText(f"Level: {new_level}")

    def handle_wrong_answer(self, selected_letter):
        self.wrong_sound.play()
        self.current_streak = 0
        self.streak_label.setText("Streak: 0 🔥")
        self.show_wrong_emoji()
        
        for btn in self.choice_buttons:
            if btn.text() == selected_letter:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border-radius: 12px;
                        font-size: 20px;
                        font-weight: bold;
                        margin: 6px;
                        border: 2px solid #c0392b;
                    }
                """)
            elif btn.text() == self.current_letter:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #27ae60;
                        color: white;
                        border-radius: 12px;
                        font-size: 20px;
                        font-weight: bold;
                        margin: 6px;
                        border: 2px solid #219a52;
                    }
                """)

    def show_success_emoji(self):
        success_label = QLabel("🎉", self)
        success_label.setFixedSize(100, 100)
        success_label.setStyleSheet("""
            QLabel {
                font-size: 60px;
                background: transparent;
                padding: 10px;
            }
        """)
        self.show_emoji_animation(success_label)

    def show_wrong_emoji(self):
        wrong_label = QLabel("😕", self)
        wrong_label.setFixedSize(100, 100)
        wrong_label.setStyleSheet("""
            QLabel {
                font-size: 60px;
                background: transparent;
                padding: 10px;
            }
        """)
        self.show_emoji_animation(wrong_label)
    def toggle_practice_mode(self, checked):
        self.practice_mode = checked
        if checked:
            self.timer.stop()
            self.timer_label.setText("Practice Mode")
            self.hint_button.show()
        else:
            self.start_timer()
            self.hint_button.hide()

    def show_hint(self):
        if self.practice_mode:
            hint_text = f"This is the sign for letter '{self.current_letter}'"
            hint_label = QLabel(hint_text, self)
            hint_label.setStyleSheet("""
                QLabel {
                    background-color: #f1c40f;
                    color: #2c3e50;
                    padding: 15px;
                    border-radius: 10px;
                    font-weight: bold;
                    font-size: 18px;
                }
            """)
            hint_label.adjustSize()
            hint_label.move(
                self.width()//2 - hint_label.width()//2,
                self.height() - hint_label.height() - 20
            )
            hint_label.show()
            QTimer.singleShot(3000, hint_label.deleteLater)

    def show_level_transition(self, level):
        level_label = QLabel(f"Level {level}! 🌟", self)
        level_label.setStyleSheet("""
            QLabel {
                font-size: 36px;
                color: #2980b9;
                background-color: rgba(255, 255, 255, 0.9);
                padding: 30px;
                border-radius: 15px;
                border: 3px solid #3498db;
            }
        """)
        level_label.adjustSize()
        level_label.setAlignment(Qt.AlignCenter)
        level_label.move(
            self.width()//2 - level_label.width()//2,
            self.height()//2 - level_label.height()//2
        )
        level_label.show()
        self.level_label.setText(f"Level: {level}")
        QTimer.singleShot(2000, level_label.deleteLater)
    def show_statistics(self):
        stats_window = QLabel(self)
        accuracy = (self.stats['correct_answers'] / max(1, self.stats['total_attempts'])) * 100
        
        stats_text = f"""
            📊 Performance Statistics:
            
            Total Attempts: {self.stats['total_attempts']}
            Correct Answers: {self.stats['correct_answers']}
            Accuracy: {accuracy:.1f}%
            Average Response Time: {self.stats['average_time']:.1f}s
            Best Response Time: {self.stats['best_time']:.1f}s
            Best Streak: {self.best_streak}
            Current Score: {self.score}
        """
        
        stats_window.setText(stats_text)
        stats_window.setStyleSheet("""
            QLabel {
                background-color: white;
                padding: 20px;
                border: 2px solid #3498db;
                border-radius: 15px;
                font-size: 18px;
                color: #2c3e50;
                font-weight: bold;
            }
        """)
        stats_window.adjustSize()
        stats_window.move(
            self.width()//2 - stats_window.width()//2,
            self.height()//2 - stats_window.height()//2
        )
        stats_window.show()
        QTimer.singleShot(5000, stats_window.deleteLater)

    def show_emoji_animation(self, emoji_label):
        emoji_label.setAlignment(Qt.AlignCenter)
        emoji_label.show()
        emoji_label.move(
            self.width() // 2 - emoji_label.width() // 2,
            self.height() // 2 - emoji_label.height() // 2
        )
        
        # Create bounce animation
        anim = QPropertyAnimation(emoji_label, b"pos")
        anim.setDuration(1000)
        anim.setStartValue(emoji_label.pos())
        
        # Calculate the new position using QPoint arithmetic
        new_pos = emoji_label.pos() + QPoint(0, -30)  # Move up by 30 pixels
        anim.setKeyValueAt(0.5, new_pos)
        
        anim.setEndValue(emoji_label.pos())
        anim.setEasingCurve(QEasingCurve.OutBounce)
        anim.start()
        
        QTimer.singleShot(1000, emoji_label.deleteLater)
    def start_timer(self):
        if not self.practice_mode:
            self.time_remaining = 30
            self.timer.start(1000)
            self.timer_label.setText(f"Time: {self.time_remaining}s")


    def skip_question(self):
        self.timer.stop()
        self.current_streak = 0
        self.streak_label.setText("Streak: 0 🔥")
        self.load_new_question()
        self.start_timer()

    def reset_buttons_and_load_new(self):
        for btn in self.choice_buttons:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 12px;
                    font-size: 20px;
                    font-weight: bold;
                    margin: 6px;
                    padding: 5px;
                    border: 2px solid #2980b9;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
        self.bonus_label.clear()
        self.load_new_question()

    def go_back_to_modes(self):
        self.timer.stop()
        self.parent().setCurrentIndex(0)
