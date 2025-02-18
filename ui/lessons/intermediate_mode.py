import os
import random
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
)
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QSoundEffect
from PySide6.QtCore import Qt, QTimer, QUrl, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtCore import QSize

class IntermediateMode(QWidget):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.current_gesture = None
        self.current_streak = 0
        self.best_streak = 0
        self.time_remaining = 45
        self.practice_mode = False
        
        # Initialize timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        self.bonus_multiplier = 1
        self.bonus_duration = 30  # Duration in seconds
        self.bonus_timer = QTimer()
        self.bonus_timer.timeout.connect(self.update_bonus_timer)
        self.remaining_bonus_time = 0

        # Initialize choice buttons
        self.choice_buttons = []
        for _ in range(4):
            btn = QPushButton()
            btn.setFixedHeight(70)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 15px;
                    font-size: 20px;
                    font-weight: bold;
                    margin: 8px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            self.choice_buttons.append(btn)

        # Gestures dictionary
        # Gestures dictionary
        self.gestures = {
            'hello': 'Hello',
            'thank_you': 'Thank You',
            'please': 'Please',
            'sorry': 'Sorry',
            'good': 'Good',
            'bad': 'Bad',
            'alligator':'Alligator',
            'apple':'Apple',
            'april':'April',
            'august':'August',
            'banana':'Banana',
            'bear':'Bear',
            'cabbage':'Cabbage',
            'camel':'Camel',
            'carrot':'Carrot',
            'cat':'Cat',
            'cherry':'Cherry',
            'coconut':'Coconut',
            'corn':'Corn',
            'cow':'Cow',
            'december':'December',
            'deer':'Deer',
            'dog':'Dog',
            'dolphin':'Dolphin',
            'duck':'Duck',
            'eagle':'Eagle',
            'elephant':'Elephant',
            'february':'February',
            'fish':'Fish',
            'fox':'Fox',
            'friday':'Friday',
            'frog':'Frog',
            'giraffe':'Giraffe',
            'goat':'Goat',
            'gorilla':'Gorilla',
            'grapes':'Grapes',
            'horse':'Horse',
            'january':'January',
            'july':'July',
            'june':'June',
            'kangaroo':'Kangaroo',
            'lettuce':'Lettuce',
            'lion':'Lion',
            'march':'March',
            'monday':'Monday',
            'mouse':'Mouse',
            'mushroom':'Mushroom',
            'november':'November',
            'october':'October',
            'onion':'Onion',
            'orange':'Orange',
            'owl':'Owl',
            'peach':'Peach',
            'pear':'Pear',
            'pepper':'Pepper',
            'pig':'Pig',
            'potato':'Potato',
            'pumpkin':'Pumpkin',
            'rabbit':'Rabbit',
            'raccoon':'Raccoon',
            'rat':'Rat',
            'saturday':'Saturday',
            'september':'September',
            'sheep':'Sheep',
            'snake':'Snake',
            'squirrel':'Squirrel',
            'sunday':'Sunday',
            'thursday':'Thursday',
            'tiger':'Tiger',
            'tomato':'Tomato',
            'tuesday':'Tuesday',
            'turtle':'Turtle',
            'watermelon':'Watermelon',
            'wednesday':'Wednesday',
            'whale':'Whale',
            'wolf':'Wolf',
            'goodbye':'Goodbye',
            'yes':'Yes',
            'no':'No',
            'help':'Help',
            'stop':'Stop',
            'eat':'Eat',
            'drink':'Drink',
            'sleep':'Sleep',
            'go':'Go',
            'come':'Come',
            'want':'Want',
            'need':'Need',
            'like':'Like',
            'work':'Work',
            'play':'Play'

        }

        # Statistics dictionary
        self.stats = {
            'total_attempts': 0,
            'correct_answers': 0,
            'average_time': 0,
            'best_time': float('inf')
        }

        # Initialize components
        self.init_ui()
        self.setup_video_player()
        self.setup_sounds()
    def animate_button_scale(self, button, scale_factor=1.1):
        """Animate the button to scale up on hover."""
        animation = QPropertyAnimation(button, b"size")
        animation.setDuration(200)  # Animation duration in milliseconds
        original_size = button.size()
        new_size = QSize(original_size.width() * scale_factor, original_size.height() * scale_factor)
        animation.setStartValue(original_size)
        animation.setEndValue(new_size)
        animation.setEasingCurve(QEasingCurve.OutBack)  # Smooth easing curve
        return animation

    def enterEvent(self, event):
        """Handle mouse enter event for bonus button."""
        self.animate_button_scale(self.bonus_button).start()

    def leaveEvent(self, event):
        """Handle mouse leave event for bonus button."""
        self.animate_button_scale(self.bonus_button, 1.0).start()

    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QHBoxLayout(self)

        # Left Frame - Video Display
        left_frame = QFrame()
        left_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
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
        stats_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
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
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            label.setStyleSheet("""
                font-size: 18px;
                color: #2c3e50;
                font-weight: bold;
                padding: 5px;
            """)
            stats_layout.addWidget(label)

        left_layout.addWidget(stats_frame)

        # Video Title
        video_title = QLabel("ASL Gesture")
        video_title.setAlignment(Qt.AlignCenter)
        video_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        video_title.setStyleSheet("""
            font-size: 24px;
            color: #2c3e50;
            font-weight: bold;
            margin: 10px;
        """)

        # Practice Mode Toggle
        self.practice_mode_btn = QPushButton("Practice Mode 📚")
        self.practice_mode_btn.setCheckable(True)
        self.practice_mode_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.practice_mode_btn.setStyleSheet("""
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
        self.practice_mode_btn.toggled.connect(self.toggle_practice_mode)

        # Video Player
        self.video_widget = QVideoWidget()
        self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Video Controls
        controls_layout = QHBoxLayout()
        self.play_button = QPushButton("Play")
        self.replay_button = QPushButton("Replay")
        self.hint_button = QPushButton("Hint (Cost: 5 points)")

        for button in [self.play_button, self.replay_button, self.hint_button]:
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    padding: 10px;
                    border-radius: 10px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)

        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.replay_button)
        controls_layout.addWidget(self.hint_button)

        left_layout.addWidget(video_title)
        left_layout.addWidget(self.practice_mode_btn)
        left_layout.addWidget(self.video_widget)
        left_layout.addLayout(controls_layout)

        # Start Button
        self.start_button = QPushButton("Start Learning!")
        self.start_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 15px;
                font-size: 24px;
                font-weight: bold;
                padding: 20px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        self.start_button.clicked.connect(self.start_session)
        left_layout.addWidget(self.start_button)

        # Initially hide video elements
        self.video_widget.hide()
        self.play_button.hide()
        self.replay_button.hide()
        self.hint_button.hide()

        # Right Frame
        right_frame = QFrame()
        right_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 20px;
                margin: 15px;
                border: 2px solid #e0e0e0;
            }
        """)
        right_layout = QVBoxLayout(right_frame)

        # Score and Timer Panel
        score_frame = QFrame()
        score_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        score_layout = QHBoxLayout(score_frame)

        self.score_label = QLabel(f"Score: {self.score}")
        self.timer_label = QLabel(f"Time: {self.time_remaining}s")
        self.bonus_button = QPushButton("🎁 2X Bonus")
        self.bonus_button.setCheckable(True)
        self.bonus_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.bonus_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                        stop:0 #f1c40f, stop:1 #f39c12);
                color: white;
                border-radius: 12px;
                padding: 8px 15px;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #fff;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                        stop:0 #f39c12, stop:1 #e67e22);
            }
            QPushButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                        stop:0 #e74c3c, stop:1 #c0392b);
            }
        """)
        self.bonus_button.clicked.connect(self.toggle_bonus_multiplier)

        # Connect hover events for bonus button
        self.bonus_button.enterEvent = self.enterEvent
        self.bonus_button.leaveEvent = self.leaveEvent

        for label in [self.score_label, self.timer_label]:
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            label.setStyleSheet("""
                font-size: 22px;
                color: #2c3e50;
                font-weight: bold;
                padding: 5px;
            """)

        score_layout.addWidget(self.score_label)
        score_layout.addWidget(self.timer_label)
        score_layout.addWidget(self.bonus_button)

        right_layout.addWidget(score_frame)

        # Add choice buttons
        for btn in self.choice_buttons:
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            right_layout.addWidget(btn)

        # Statistics Button
        stats_btn = QPushButton("View Statistics 📊")
        stats_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
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
        back_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        back_btn.clicked.connect(self.go_back_to_modes)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
                border-radius: 12px;
                margin: 15px;
                font-size: 16px;
                font-weight: bold;
            }
        """)

        right_layout.addWidget(stats_btn)
        right_layout.addStretch()
        right_layout.addWidget(back_btn)

        main_layout.addWidget(left_frame)
        main_layout.addWidget(right_frame)

    def animate_button_scale(self, button, scale_factor=1.1):
        """Animate the button to scale up on hover."""
        animation = QPropertyAnimation(button, b"size")
        animation.setDuration(200)  # Animation duration in milliseconds
        original_size = button.size()
        new_size = QSize(original_size.width() * scale_factor, original_size.height() * scale_factor)
        animation.setStartValue(original_size)
        animation.setEndValue(new_size)
        animation.setEasingCurve(QEasingCurve.OutBack)  # Smooth easing curve
        return animation

    # Rest of the code remains unchanged...


    def setup_video_player(self):
        """Initialize the video player and audio output."""
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.7)
        
        self.play_button.clicked.connect(self.play_video)
        self.replay_button.clicked.connect(self.replay_video)
        self.hint_button.clicked.connect(self.show_hint)
        self.media_player.errorOccurred.connect(self.handle_media_error)

    def setup_sounds(self):
        """Initialize sound effects."""
        self.correct_sound = QSoundEffect()
        self.correct_sound.setSource(QUrl.fromLocalFile(os.path.join("assets", "sounds", "correct.wav")))
        self.wrong_sound = QSoundEffect()
        self.wrong_sound.setSource(QUrl.fromLocalFile(os.path.join("assets", "sounds", "wrong.wav")))

    def play_video(self):
        """Play or pause the video."""
        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.play_button.setText("Play")
        else:
            self.media_player.play()
            self.play_button.setText("Pause")

    def replay_video(self):
        """Replay the current video."""
        self.media_player.setPosition(0)
        self.media_player.play()
        self.play_button.setText("Pause")

    def show_hint(self):
        """Show a hint for the current gesture."""
        if self.score >= 5:
            self.score -= 5
            self.score_label.setText(f"Score: {self.score}")
            hint_text = f"This gesture means: {self.gestures[self.current_gesture]}"
            hint_label = QLabel(hint_text, self)
            hint_label.setStyleSheet("""
                background-color: #f1c40f;
                color: #2c3e50;
                padding: 15px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 18px;
            """)
            hint_label.adjustSize()
            hint_label.move(
                self.width() // 2 - hint_label.width() // 2,
                self.height() - hint_label.height() - 20
            )
            hint_label.show()
            QTimer.singleShot(3000, hint_label.deleteLater)

    def update_timer(self):
        """Update the timer and handle time expiration."""
        if not self.practice_mode:
            self.time_remaining -= 1
            self.timer_label.setText(f"Time: {self.time_remaining}s")
            if self.time_remaining <= 0:
                self.timer.stop()
                self.load_new_gesture()

    def toggle_practice_mode(self, checked):
        """Toggle practice mode on or off."""
        self.practice_mode = checked
        if checked:
            self.timer.stop()
            self.timer_label.setText("Practice Mode")
        else:
            self.start_timer()

    def start_timer(self):
        """Start or restart the timer."""
        if not self.practice_mode:
            self.time_remaining = 45
            self.timer.stop()
            self.timer.start(1000)
            self.timer_label.setText(f"Time: {self.time_remaining}s")
            self.start_button.setEnabled(False)  # Prevent multiple starts

    def show_bonus_points(self, bonus_points):
        """Display animated bonus points notification."""
        bonus_label = QLabel(f"+{bonus_points} BONUS! 🌟", self)
        bonus_label.setStyleSheet("""
            QLabel {
                background-color: #f1c40f;
                color: #2c3e50;
                padding: 15px 25px;
                border-radius: 15px;
                font-weight: bold;
                font-size: 22px;
                border: 2px solid #f39c12;
            }
        """)
        bonus_label.adjustSize()
        
        # Initial position
        bonus_label.move(
            self.score_label.x() + self.score_label.width() + 20,
            self.score_label.y()
        )
        bonus_label.show()
        
        # Create bounce and fade animation
        anim = QPropertyAnimation(bonus_label, b"pos")
        anim.setDuration(1500)
        anim.setStartValue(bonus_label.pos())
        anim.setKeyValueAt(0.3, bonus_label.pos() + QPoint(0, -40))
        anim.setKeyValueAt(0.6, bonus_label.pos() + QPoint(0, -30))
        anim.setEndValue(bonus_label.pos() + QPoint(0, -20))
        anim.setEasingCurve(QEasingCurve.OutBounce)
        anim.start()
        
        # Remove the label after animation
        QTimer.singleShot(1500, bonus_label.deleteLater)

    def toggle_bonus_multiplier(self):
        """Toggle the bonus score multiplier."""
        if self.bonus_button.isChecked():
            self.bonus_multiplier = 2
            self.remaining_bonus_time = self.bonus_duration
            self.bonus_timer.start(1000)  # Update every second
            self.bonus_button.setText(f"🔥 2X ({self.remaining_bonus_time}s)")
        else:
            self.reset_bonus()
    
    def update_bonus_timer(self):
        """Update the bonus timer countdown."""
        self.remaining_bonus_time -= 1
        self.bonus_button.setText(f"🔥 2X ({self.remaining_bonus_time}s)")
        
        if self.remaining_bonus_time <= 0:
            self.reset_bonus()

    def reset_bonus(self):
        """Reset bonus multiplier and button state."""
        self.bonus_multiplier = 1
        self.bonus_timer.stop()
        self.bonus_button.setChecked(False)
        self.bonus_button.setText("🎁 2X Bonus")
    
    def close_statistics(self):
        """Close the statistics overlay."""
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.hide()
            self.overlay.deleteLater()
            del self.overlay  # Remove reference to the overlay

        # Show the video widget again
        self.video_widget.show()


    def show_statistics(self):
        """Display performance statistics with enhanced UI."""
        # Hide the video widget
        self.video_widget.hide()

        # Calculate accuracy
        accuracy = (self.stats['correct_answers'] / max(1, self.stats['total_attempts'])) * 100

        # Create a semi-transparent overlay
        self.overlay = QFrame(self)  # Store overlay as an instance variable
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
        stats_container.raise_()  # Bring the stats container to the front


    def show_level_transition(self, new_level):
        """Show level up animation and message with a semi-transparent overlay."""
        # Hide the video widget
        self.video_widget.hide()

        # Create a semi-transparent overlay
        self.level_overlay = QFrame(self)
        self.level_overlay.setStyleSheet("background-color: rgba(0, 0, 0, 0.7);")  # Semi-transparent black
        self.level_overlay.setGeometry(self.rect())  # Cover the entire widget

        # Create a container for the level-up message
        level_container = QFrame(self.level_overlay)
        level_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 3px solid #3498db;
                border-radius: 20px;
                padding: 25px;
            }
        """)
        level_container.setFixedSize(400, 200)  # Set a fixed size for the container

        # Add the level-up message
        level_label = QLabel(f"Level Up! 🎮\nYou reached Level {new_level}", level_container)
        level_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 10px;
        """)
        level_label.setAlignment(Qt.AlignCenter)

        # Layout for the container
        level_layout = QVBoxLayout(level_container)
        level_layout.addWidget(level_label, alignment=Qt.AlignCenter)

        # Center the container within the overlay
        level_container.move(
            self.level_overlay.width() // 2 - level_container.width() // 2,
            self.level_overlay.height() // 2 - level_container.height() // 2
        )

        # Show the overlay and container
        self.level_overlay.show()
        level_container.show()

        # Animate the container (optional: add a bounce effect)
        anim = QPropertyAnimation(level_container, b"pos")
        anim.setDuration(1000)
        anim.setStartValue(level_container.pos())
        anim.setKeyValueAt(0.5, level_container.pos() + QPoint(0, -30))
        anim.setEndValue(level_container.pos())
        anim.setEasingCurve(QEasingCurve.OutBounce)
        anim.start()

        # Remove the overlay and container after the animation
        QTimer.singleShot(2000, lambda: (self.level_overlay.deleteLater(), level_container.deleteLater()))

        # Show the video widget again after the animation is complete
        QTimer.singleShot(2000, self.video_widget.show)

    def show_success_emoji(self):
        """Show a success emoji animation."""
        success_label = QLabel("🎉", self)
        success_label.setFixedSize(100, 100)
        success_label.setStyleSheet("font-size: 60px;")
        self.show_emoji_animation(success_label)

    def show_wrong_emoji(self):
        """Show a wrong emoji animation."""
        wrong_label = QLabel("😕", self)
        wrong_label.setFixedSize(100, 100)
        wrong_label.setStyleSheet("font-size: 60px;")
        self.show_emoji_animation(wrong_label)

    def show_emoji_animation(self, emoji_label):
        """Animate an emoji label."""
        emoji_label.setAlignment(Qt.AlignCenter)
        emoji_label.show()
        emoji_label.move(
            self.width() // 2 - emoji_label.width() // 2,
            self.height() // 2 - emoji_label.height() // 2
        )

        anim = QPropertyAnimation(emoji_label, b"pos")
        anim.setDuration(1000)
        anim.setStartValue(emoji_label.pos())
        new_pos = emoji_label.pos() + QPoint(0, -30)
        anim.setKeyValueAt(0.5, new_pos)
        anim.setEndValue(emoji_label.pos())
        anim.setEasingCurve(QEasingCurve.OutBounce)
        anim.start()
        QTimer.singleShot(1000, emoji_label.deleteLater)

    def load_new_gesture(self):
        """Load a new gesture video and update the UI."""
        # Gracefully stop current video
        self.media_player.stop()
        self.media_player.setPosition(0)
        
        # Add a brief transition delay
        QTimer.singleShot(150, self._load_new_content)

    def _load_new_content(self):
        """Helper method to load new video content with smooth transition"""
        available_gestures = list(self.gestures.keys())
        if not available_gestures:
            print("No gestures available")
            return
            
        # Select new gesture, excluding current one if possible
        remaining_gestures = [g for g in available_gestures if g != self.current_gesture]
        self.current_gesture = random.choice(remaining_gestures if remaining_gestures else available_gestures)
        
        video_path = os.path.join("assets", "gesture_videos", f"{self.current_gesture}.mp4")
        if not os.path.exists(video_path):
            print(f"Video file not found: {video_path}")
            return
        
        # Set up new video with smooth transition
        self.media_player.setSource(QUrl.fromLocalFile(video_path))
        self.update_choice_buttons()
        
        # Add slight delay before playing new video
        QTimer.singleShot(100, self.media_player.play)


    def update_choice_buttons(self):
        """Update choice buttons with new options"""
        correct_answer = self.gestures[self.current_gesture]
        choices = [correct_answer]
        
        wrong_options = [g for g in self.gestures.values() if g != correct_answer]
        choices.extend(random.sample(wrong_options, min(3, len(wrong_options))))
        random.shuffle(choices)
        
        for btn, choice in zip(self.choice_buttons, choices):
            btn.setText(choice)
            try:
                btn.clicked.disconnect()
            except TypeError:
                pass
            btn.clicked.connect(lambda checked, text=choice: self.check_answer(text))

    def handle_media_error(self, error, error_string):
        """Handle media player errors"""
        print(f"Media Error {error}: {error_string}")
        error_label = QLabel(f"Error playing video: {error_string}", self)
        error_label.setStyleSheet("""
            background-color: #e74c3c;
            color: white;
            padding: 10px;
            border-radius: 5px;
        """)
        error_label.adjustSize()
        error_label.move(
            self.width() // 2 - error_label.width() // 2,
            self.height() // 2 - error_label.height() // 2
        )
        error_label.show()
        QTimer.singleShot(3000, error_label.deleteLater)

    def check_answer(self, selected_gesture):
        """Handle answer selection"""
        self.stats['total_attempts'] += 1
        self.media_player.pause()
        self.timer.stop()
        correct_gesture = self.gestures[self.current_gesture]

        if selected_gesture == correct_gesture:
            self.handle_correct_answer(selected_gesture)
        else:
            self.handle_wrong_answer(selected_gesture)

        QTimer.singleShot(2000, self.proceed_to_next)


    def start_session(self):
        """Start the learning session"""
        self.start_button.hide()
        self.video_widget.show()
        self.play_button.show()
        self.replay_button.show()
        self.hint_button.show()
        
        for btn in self.choice_buttons:
            btn.setEnabled(True)
            
        self.load_new_gesture()
        self.start_timer()
    def proceed_to_next(self):
        """Load next gesture after feedback"""
        for btn in self.choice_buttons:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 15px;
                    font-size: 20px;
                    font-weight: bold;
                    margin: 8px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
        
        self.load_new_gesture()
        self.media_player.play()
        if not self.practice_mode:
            self.start_timer()


    def handle_correct_answer(self, selected_gesture):
        self.correct_sound.play()
        self.current_streak += 1
        self.best_streak = max(self.current_streak, self.best_streak)
        
        # Calculate score and bonus
        time_bonus = max(0, self.time_remaining)
        bonus_points = time_bonus * 2 * self.bonus_multiplier  # Apply multiplier
        self.score += (10 * self.bonus_multiplier) + bonus_points  # Apply multiplier to base score too
        
        # Show bonus animation if there are bonus points
        if bonus_points > 0:
            self.show_bonus_points(bonus_points)
        
        
        # Update UI
        self.score_label.setText(f"Score: {self.score} ✨")
        self.streak_label.setText(f"Streak: {self.current_streak} 🔥")
        self.best_streak_label.setText(f"Best: {self.best_streak} ⭐")
        
        # Update statistics
        self.stats['correct_answers'] += 1
        response_time = 45 - self.time_remaining
        self.stats['average_time'] = (
            (self.stats['average_time'] * (self.stats['correct_answers'] - 1) + response_time)
            / self.stats['correct_answers']
        )
        self.stats['best_time'] = min(self.stats['best_time'], response_time)
        
        # Show success animation
        self.show_success_emoji()
        
        # Highlight correct button
        for btn in self.choice_buttons:
            if btn.text() == selected_gesture:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #27ae60;
                        color: white;
                        border-radius: 15px;
                        font-size: 20px;
                        font-weight: bold;
                        margin: 8px;
                    }
                """)

        # Level calculation
        new_level = (self.stats['correct_answers'] // 5) + 1
        current_level = int(self.level_label.text().split(": ")[1])
        
        if new_level > current_level:
            self.show_level_transition(new_level)
            self.level_label.setText(f"Level: {new_level}")

    def handle_wrong_answer(self, selected_gesture):
        """Handle a wrong answer."""
        self.wrong_sound.play()
        self.current_streak = 0
        self.streak_label.setText("Streak: 0 🔥")
        self.show_wrong_emoji()

        correct_gesture = self.gestures[self.current_gesture]

        for btn in self.choice_buttons:
            if btn.text() == selected_gesture:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border-radius: 15px;
                        font-size: 20px;
                        font-weight: bold;
                        margin: 8px;
                    }
                """)
            elif btn.text() == correct_gesture:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #27ae60;
                        color: white;
                        border-radius: 15px;
                        font-size: 20px;
                        font-weight: bold;
                        margin: 8px;
                    }
                """)

    def go_back_to_modes(self):
        """Go back to the modes screen."""
        self.media_player.stop()
        self.timer.stop()
        self.parent().setCurrentIndex(0)

    def __del__(self):
        """Clean up resources"""
        try:
            if hasattr(self, 'timer') and self.timer:
                self.timer.stop()
            if hasattr(self, 'media_player') and self.media_player:
                self.media_player.stop()
            if hasattr(self, 'correct_sound') and self.correct_sound:
                self.correct_sound.stop()
            if hasattr(self, 'wrong_sound') and self.wrong_sound:
                self.wrong_sound.stop()
        except:
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IntermediateMode()
    window.show()
    sys.exit(app.exec())


