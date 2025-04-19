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
        self.skip_button.setFixedHeight(55)  # Added this line
        self.skip_button.setFixedWidth(550)
        self.skip_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
                padding: 10px 20px;
                margin: 6px;
                border: 2px solid #e67e22;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        self.skip_button.clicked.connect(self.skip_question)
        choice_layout.addWidget(self.skip_button, 0, Qt.AlignCenter)




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
        # right_layout.addWidget(self.skip_button)
        right_layout.addWidget(stats_btn)
        right_layout.addStretch()
        right_layout.addWidget(back_btn)

        # Add frames to main layout
        main_layout.addWidget(left_frame, 1)
        main_layout.addWidget(right_frame, 1)


    def setup_sounds(self):
        self.correct_sound = QSoundEffect()
        self.correct_sound.setSource(QUrl.fromLocalFile("assets/sounds/correct.wav"))
        self.wrong_sound = QSoundEffect()
        self.wrong_sound.setSource(QUrl.fromLocalFile("assets/sounds/wrong.wav"))

    def load_new_question(self):
       # Try to get main window through parent hierarchy
        try:
            main_window = self.window()
            if hasattr(main_window, 'navbar'):
                main_window.navbar.setEnabled(False)
        except:
            pass
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
        self.score_label.setText(f"Score: {self.score} 💎")
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

        if new_progress >= 26:
            QTimer.singleShot(1000, self.show_completion_screen)

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

    def show_completion_screen(self):
        """Display completion screen when all 26 letters are completed."""
        self.timer.stop()
                
        # Create a semi-transparent overlay for the entire application
        self.completion_overlay = QFrame(self)
        self.completion_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 0.8);")  # Darker overlay
        self.completion_overlay.setGeometry(self.rect())
        self.completion_overlay.raise_()  # Make sure overlay is on top
                
        # Create a container for the completion message
        completion_container = QFrame(self.completion_overlay)
        completion_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 4px solid #3498db;
                border-radius: 20px;
            }
        """)
        # Set fixed width to prevent text cutoff
        completion_container.setFixedWidth(500)
                
        # Create layout for the completion container with appropriate margins
        container_layout = QVBoxLayout(completion_container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(10)
                
        # Trophy icon
        trophy_label = QLabel("🏆")
        trophy_label.setStyleSheet("font-size: 32px; margin-bottom: 5px;")
        trophy_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(trophy_label)
                
        # Add congratulations message with improved color
        congrats_label = QLabel("🎉 Congratulations! 🎉")
        congrats_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #16a085;  /* Darker teal green for stronger contrast */
            background-color: #e8f8f5;  /* Light teal background */
            border-radius: 10px;
            padding: 8px;
        """)
        congrats_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(congrats_label)
                
        # Add completion message with improved color
        completion_message = QLabel("You've mastered all 26 ASL letters!")
        completion_message.setStyleSheet("""
            font-size: 18px;
            color: #1e3799;  /* Darker blue for better readability */
            padding: 10px;
            background-color: #e8f0ff;  /* Light blue background */
            border-radius: 10px;
            font-weight: bold;
        """)
        completion_message.setAlignment(Qt.AlignCenter)
        completion_message.setWordWrap(True)
        container_layout.addWidget(completion_message)
                
        # Add score container with improved colors
        score_container = QFrame()
        score_container.setStyleSheet("""
            background-color: #d6eaf8;  /* Slightly darker background for better contrast */
            border-radius: 10px;
            border: 1px solid #3498db;
            padding: 5px;
        """)
        score_layout = QVBoxLayout(score_container)
        score_layout.setContentsMargins(10, 10, 10, 10)
        score_layout.setSpacing(5)
                
        # Score information with improved colors
        final_score = QLabel(f"Final Score: {self.score} 💎")
        final_score.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold; 
            color: #1a5276;  /* Darker blue for better contrast */
        """)
        final_score.setAlignment(Qt.AlignCenter)
        score_layout.addWidget(final_score)
                
        best_streak = QLabel(f"Best Streak: {self.best_streak} 🔥")
        best_streak.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold; 
            color: #a93226;  /* Darker orange/red for better contrast */
        """)
        best_streak.setAlignment(Qt.AlignCenter)
        score_layout.addWidget(best_streak)
                
        container_layout.addWidget(score_container)
                
        # Add statistics with improved colors and checks for valid values
        if self.stats['correct_answers'] > 0:
            stats_frame = QFrame()
            stats_frame.setStyleSheet("""
                background-color: #d5f5e3;  /* Slightly darker green background */
                border-radius: 10px;
                border: 1px solid #27ae60;
                padding: 10px;
            """)
            stats_layout = QVBoxLayout(stats_frame)
            stats_layout.setContentsMargins(10, 10, 10, 10)
            stats_layout.setSpacing(5)
                        
            # Calculate accuracy and check for valid values
            accuracy = 0
            if self.stats['total_attempts'] > 0:
                accuracy = (self.stats['correct_answers'] / self.stats['total_attempts']) * 100
                        
            # Create simple label for each stat
            correct_label = QLabel(f"✅ Correct Answers: {self.stats['correct_answers']}")
            correct_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #196f3d;")
            correct_label.setAlignment(Qt.AlignCenter)
            stats_layout.addWidget(correct_label)
                        
            accuracy_label = QLabel(f"🎯 Accuracy: {accuracy:.1f}%")
            accuracy_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #7d3c98;")
            accuracy_label.setAlignment(Qt.AlignCenter)
            stats_layout.addWidget(accuracy_label)
                        
            # Check for valid average time
            avg_time_text = "N/A"
            if isinstance(self.stats['average_time'], (int, float)) and self.stats['average_time'] != float('inf'):
                avg_time_text = f"{self.stats['average_time']:.1f}s"
                        
            avg_time_label = QLabel(f"⏱️ Avg Time: {avg_time_text}")
            avg_time_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #1a5276;")
            avg_time_label.setAlignment(Qt.AlignCenter)
            stats_layout.addWidget(avg_time_label)
                        
            # Check for valid best time
            best_time_text = "N/A"
            if isinstance(self.stats['best_time'], (int, float)) and self.stats['best_time'] != float('inf'):
                best_time_text = f"{self.stats['best_time']:.1f}s"
                        
            best_time_label = QLabel(f"🚀 Best Time: {best_time_text}")
            best_time_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #a93226;")
            best_time_label.setAlignment(Qt.AlignCenter)
            stats_layout.addWidget(best_time_label)
                        
            container_layout.addWidget(stats_frame)
        else:
            stats_label = QLabel("No correct answers recorded.")
            stats_label.setStyleSheet("font-size: 16px; color: #c0392b; font-weight: bold;")
            stats_label.setAlignment(Qt.AlignCenter)
            container_layout.addWidget(stats_label)
                
        # Add buttons with enhanced styling
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
                
        restart_button = QPushButton("🔄 Restart")
        restart_button.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;  /* Darker blue */
                color: white;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                padding: 8px 15px;
                border: 2px solid #1a5276;  /* Dark border */
            }
            QPushButton:hover {
                background-color: #1a5276;  /* Even darker on hover */
                border: 2px solid #154360;
            }
        """)
        # Fix: Use direct method connection instead of lambda
        restart_button.clicked.connect(self.restart_test)
                
        menu_button = QPushButton("🏠 Main Menu")
        menu_button.setStyleSheet("""
            QPushButton {
                background-color: #c0392b;  /* Darker red */
                color: white;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                padding: 8px 15px;
                border: 2px solid #922b21;  /* Dark border */
            }
            QPushButton:hover {
                background-color: #922b21;  /* Even darker on hover */
                border: 2px solid #7b241c;
            }
        """)
        # Fix: Use direct method connection instead of lambda
        menu_button.clicked.connect(self.return_to_menu)
                
        button_layout.addWidget(restart_button)
        button_layout.addWidget(menu_button)
                
        container_layout.addLayout(button_layout)
                
        # Center the container within the overlay
        overlay_layout = QVBoxLayout(self.completion_overlay)
        overlay_layout.addWidget(completion_container, alignment=Qt.AlignCenter)
                
        # Show the overlay in the parent widget's scope
        self.completion_overlay.setParent(self)
        self.completion_overlay.show()
        self.completion_overlay.raise_()  # Ensure it's on top
        completion_container.raise_()  # Ensure container is on top of overlay
                
        # Add animation effect
        anim = QPropertyAnimation(completion_container, b"pos")
        anim.setDuration(800)
        anim.setStartValue(completion_container.pos() + QPoint(0, 30))
        anim.setEndValue(completion_container.pos())
        anim.setEasingCurve(QEasingCurve.OutBack)
        anim.start()



    def show_statistics_from_completion(self, overlay):
        """Show statistics from completion screen."""
        overlay.hide()
        self.show_statistics()

    def exit_to_menu(self, overlay):
        """Exit to menu from completion screen."""
        try:
            main_window = self.window()
            if hasattr(main_window, 'navbar'):
                main_window.navbar.setEnabled(True)
        except:
            pass
        
        self.reset_test()
        overlay.deleteLater()
        self.parent().setCurrentIndex(0)



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
        """Display performance statistics with enhanced UI."""
        # Hide the image label temporarily
        self.image_label.hide()

        # Create a semi-transparent overlay
        self.overlay = QFrame(self)
        self.overlay.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 0.7);
            }
        """)
        self.overlay.setGeometry(self.rect())

        # Create stats container with animation
        stats_container = QFrame(self.overlay)
        stats_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 3px solid #3498db;
                border-radius: 20px;
                padding: 25px;
            }
        """)

        stats_layout = QVBoxLayout(stats_container)

        # Add stats content
        title = QLabel("🏆 Performance Dashboard")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 10px;
        """)
        stats_layout.addWidget(title, alignment=Qt.AlignCenter)

        # Calculate accuracy
        accuracy = (self.stats['correct_answers'] / max(1, self.stats['total_attempts'])) * 100

        stats_text = f"""
            🎯 Total Attempts: {self.stats['total_attempts']}
            ✅ Correct Answers: {self.stats['correct_answers']}
            📊 Accuracy: {accuracy:.1f}%
            ⏱️ Average Response: {self.stats['average_time']:.1f}s
            🚀 Best Response: {self.stats['best_time']:.1f}s
            🔥 Best Streak: {self.best_streak}
            💫 Current Score: {self.score}
        """
        stats_content = QLabel(stats_text)
        stats_content.setStyleSheet("""
            font-size: 20px;
            color: #2c3e50;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 10px;
            margin: 10px;
        """)
        stats_layout.addWidget(stats_content, alignment=Qt.AlignCenter)

        # Close button with hover effect
        close_btn = QPushButton("Close Dashboard")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px 25px;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #2980b9;
                transform: scale(1.05);
            }
        """)
        close_btn.clicked.connect(self.close_statistics)
        stats_layout.addWidget(close_btn, alignment=Qt.AlignCenter)

        # Center the container
        overlay_layout = QVBoxLayout(self.overlay)
        overlay_layout.addWidget(stats_container, alignment=Qt.AlignCenter)

        # Show with fade-in effect
        self.overlay.show()
        stats_container.raise_()

    def close_statistics(self):
        """Close the statistics overlay."""
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.hide()
            self.overlay.deleteLater()
            del self.overlay

        # Show the image label again
        self.image_label.show()

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

    def show_exit_confirmation(self):
        # Create overlay frame
        overlay = QFrame(self)
        overlay.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 0.7);
            }
        """)
        overlay.setGeometry(self.rect())
        
        # Create confirmation dialog
        dialog = QFrame(overlay)
        dialog.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #e74c3c;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        
        dialog_layout = QVBoxLayout(dialog)
        
        # Warning message
        warning = QLabel("⚠️ Exit Test")
        warning.setStyleSheet("""
            font-size: 24px;
            color: #e74c3c;
            font-weight: bold;
        """)
        
        message = QLabel("Are you sure you want to exit?\nYour test progress will be reset.")
        message.setStyleSheet("""
            font-size: 18px; 
            padding: 10px;
            color: #2c3e50;
            text-align: center;
        """)
        message.setAlignment(Qt.AlignCenter)
        
        # Buttons
        buttons = QHBoxLayout()
        continue_btn = QPushButton("Continue Test")
        exit_btn = QPushButton("Exit Test")
        
        continue_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
        """)
        
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
        """)
        
        buttons.addWidget(continue_btn)
        buttons.addWidget(exit_btn)
        
        dialog_layout.addWidget(warning, alignment=Qt.AlignCenter)
        dialog_layout.addWidget(message, alignment=Qt.AlignCenter)
        dialog_layout.addLayout(buttons)
        
        # Center the dialog
        overlay_layout = QVBoxLayout(overlay)
        overlay_layout.addWidget(dialog, alignment=Qt.AlignCenter)
        
        overlay.show()
        
        # Connect buttons
        continue_btn.clicked.connect(overlay.deleteLater)
        exit_btn.clicked.connect(lambda: self.confirm_exit(overlay))

    # Add method to reset test
    def reset_test(self):
        self.score = 0
        self.current_streak = 0
        self.best_streak = 0
        self.time_remaining = 30
        self.timer.stop()
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Progress: 0/26 Letters")
        self.level_label.setText("Level: 1")
        self.stats = {
            'total_attempts': 0,
            'correct_answers': 0,
            'average_time': 0,
            'best_time': float('inf')
        }
                
        # Reset UI elements
        self.score_label.setText("Score: 0")
        self.streak_label.setText("Streak: 0 🔥")
        self.best_streak_label.setText("Best: 0 ⭐")
        self.timer_label.setText("Time: 30s")
        self.bonus_label.clear()
        
        # Load a new question to start fresh
        self.load_new_question()

    def restart_test(self):
        """Restart the test and close the completion overlay."""
        # Simply check if the attribute exists and handle exceptions
        try:
            if hasattr(self, 'completion_overlay'):
                self.completion_overlay.hide()  # Hide first to prevent visual glitches
                self.completion_overlay.deleteLater()
                del self.completion_overlay  # Remove the reference
        except Exception as e:
            print(f"Error cleaning up completion overlay: {e}")
                
        # Enable navbar if it exists
        try:
            main_window = self.window()
            if hasattr(main_window, 'navbar'):
                main_window.navbar.setEnabled(True)
        except Exception as e:
            print(f"Error enabling navbar: {e}")
                
        # Reset the test
        self.reset_test()

    def return_to_menu(self):
        """Return to the main menu and close the completion overlay."""
        # Simply check if the attribute exists and handle exceptions
        try:
            if hasattr(self, 'completion_overlay'):
                self.completion_overlay.hide()  # Hide first to prevent visual glitches
                self.completion_overlay.deleteLater()
                del self.completion_overlay  # Remove the reference
        except Exception as e:
            print(f"Error cleaning up completion overlay: {e}")
                
        # Enable navbar if it exists
        try:
            main_window = self.window()
            if hasattr(main_window, 'navbar'):
                main_window.navbar.setEnabled(True)
        except Exception as e:
            print(f"Error enabling navbar: {e}")
                
        # Reset the test and go back to the main menu
        self.reset_test()
        self.parent().setCurrentIndex(0)






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

    def confirm_exit(self, overlay):
        try:
            main_window = self.window()
            if hasattr(main_window, 'navbar'):
                main_window.navbar.setEnabled(True)
        except:
            pass
        self.reset_test()
        overlay.deleteLater()
        self.parent().setCurrentIndex(0)

    def go_back_to_modes(self):
        self.show_exit_confirmation()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BeginnerMode()
    window.show()
    sys.exit(app.exec())