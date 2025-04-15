# loading_spinner.py

import os
import sys
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QMovie

class LoadingSpinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create loading spinner
        self.spinner_label = QLabel()
        self.spinner_label.setAlignment(Qt.AlignCenter)
        self.spinner_label.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.7);
            border-radius: 15px;
            padding: 15px;
        """)
        
        # Set up the SVG spinner animation
        self.setup_animation()
        
        # Animation text
        self.text_label = QLabel()
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setStyleSheet("""
            color: white; 
            font-size: 16px; 
            background-color: rgba(0, 0, 0, 150); 
            border-radius: 10px;
            padding: 8px 15px;
        """)
        self.text_label.hide()
        
        # Add to layout
        layout.addWidget(self.spinner_label)
        layout.addWidget(self.text_label)
        
        # Animation text options
        self.animation_text = ["Processing", "Processing ⚫", "Processing ⚫⚫", "Processing ⚫⚫⚫"]
        self.animation_index = 0
        
        # Text animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation_text)
        
        # Hide initially
        self.hide()
    
    def setup_animation(self):
        # Ensure assets directory exists
        os.makedirs("assets", exist_ok=True)
        
        # Path to SVG spinner
        spinner_path = os.path.abspath("assets/loading_spinner.svg")
        
        # Create or verify SVG exists
        if not os.path.exists(spinner_path):
            self.create_default_svg(spinner_path)
        
        # Create movie from SVG
        self.loading_movie = QMovie(spinner_path)
        self.loading_movie.setScaledSize(QSize(100, 100))
        
        # Check if movie is valid
        if not self.loading_movie.isValid():
            print(f"Error: Loading animation file not found or invalid at path: {spinner_path}")
            # Fallback to text
            self.spinner_label.setText("Loading...")
            self.spinner_label.setStyleSheet("""
                font-size: 18px;
                color: #2962ff;
                background-color: rgba(255, 255, 255, 0.8);
                border-radius: 10px;
                padding: 15px;
            """)
        else:
            self.spinner_label.setMovie(self.loading_movie)
            self.loading_movie.start()
    
    def create_default_svg(self, path):
        """Create a default SVG loading spinner"""
        svg_content = '''<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="margin: auto; background: rgba(255, 255, 255, 0); display: block; shape-rendering: auto;" width="100px" height="100px" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid">
<g transform="rotate(0 50 50)">
  <rect x="47" y="24" rx="3" ry="6" width="6" height="12" fill="#2962ff">
    <animate attributeName="opacity" values="1;0" keyTimes="0;1" dur="1s" begin="-0.9166666666666666s" repeatCount="indefinite"></animate>
  </rect>
</g><g transform="rotate(30 50 50)">
  <rect x="47" y="24" rx="3" ry="6" width="6" height="12" fill="#2962ff">
    <animate attributeName="opacity" values="1;0" keyTimes="0;1" dur="1s" begin="-0.8333333333333334s" repeatCount="indefinite"></animate>
  </rect>
</g><g transform="rotate(60 50 50)">
  <rect x="47" y="24" rx="3" ry="6" width="6" height="12" fill="#2962ff">
    <animate attributeName="opacity" values="1;0" keyTimes="0;1" dur="1s" begin="-0.75s" repeatCount="indefinite"></animate>
  </rect>
</g><g transform="rotate(90 50 50)">
  <rect x="47" y="24" rx="3" ry="6" width="6" height="12" fill="#2962ff">
    <animate attributeName="opacity" values="1;0" keyTimes="0;1" dur="1s" begin="-0.6666666666666666s" repeatCount="indefinite"></animate>
  </rect>
</g><g transform="rotate(120 50 50)">
  <rect x="47" y="24" rx="3" ry="6" width="6" height="12" fill="#2962ff">
    <animate attributeName="opacity" values="1;0" keyTimes="0;1" dur="1s" begin="-0.5833333333333334s" repeatCount="indefinite"></animate>
  </rect>
</g><g transform="rotate(150 50 50)">
  <rect x="47" y="24" rx="3" ry="6" width="6" height="12" fill="#2962ff">
    <animate attributeName="opacity" values="1;0" keyTimes="0;1" dur="1s" begin="-0.5s" repeatCount="indefinite"></animate>
  </rect>
</g><g transform="rotate(180 50 50)">
  <rect x="47" y="24" rx="3" ry="6" width="6" height="12" fill="#2962ff">
    <animate attributeName="opacity" values="1;0" keyTimes="0;1" dur="1s" begin="-0.4166666666666667s" repeatCount="indefinite"></animate>
  </rect>
</g><g transform="rotate(210 50 50)">
  <rect x="47" y="24" rx="3" ry="6" width="6" height="12" fill="#2962ff">
    <animate attributeName="opacity" values="1;0" keyTimes="0;1" dur="1s" begin="-0.3333333333333333s" repeatCount="indefinite"></animate>
  </rect>
</g><g transform="rotate(240 50 50)">
  <rect x="47" y="24" rx="3" ry="6" width="6" height="12" fill="#2962ff">
    <animate attributeName="opacity" values="1;0" keyTimes="0;1" dur="1s" begin="-0.25s" repeatCount="indefinite"></animate>
  </rect>
</g><g transform="rotate(270 50 50)">
  <rect x="47" y="24" rx="3" ry="6" width="6" height="12" fill="#2962ff">
    <animate attributeName="opacity" values="1;0" keyTimes="0;1" dur="1s" begin="-0.16666666666666666s" repeatCount="indefinite"></animate>
  </rect>
</g><g transform="rotate(300 50 50)">
  <rect x="47" y="24" rx="3" ry="6" width="6" height="12" fill="#2962ff">
    <animate attributeName="opacity" values="1;0" keyTimes="0;1" dur="1s" begin="-0.08333333333333333s" repeatCount="indefinite"></animate>
  </rect>
</g><g transform="rotate(330 50 50)">
  <rect x="47" y="24" rx="3" ry="6" width="6" height="12" fill="#2962ff">
    <animate attributeName="opacity" values="1;0" keyTimes="0;1" dur="1s" begin="0s" repeatCount="indefinite"></animate>
  </rect>
</g>
</svg>'''
        
        try:
            with open(path, 'w', encoding='utf-8') as file:
                file.write(svg_content)
            print(f"Created default SVG spinner at {path}")
        except Exception as e:
            print(f"Error creating SVG spinner: {str(e)}")
    
    def show_with_text(self, text=None):
        """Show the spinner with optional text"""
        if text:
            self.text_label.setText(text)
            self.text_label.show()
        else:
            self.text_label.hide()
        
        # Ensure movie is playing
        if hasattr(self, 'loading_movie') and self.loading_movie.isValid():
            if self.loading_movie.state() != QMovie.Running:
                self.loading_movie.start()
        
        self.show()
    
    def start_text_animation(self, custom_text=None):
        """Start the animated text"""
        if custom_text:
            self.animation_text = custom_text
        
        self.animation_index = 0
        self.text_label.setText(self.animation_text[0])
        self.text_label.show()
        self.animation_timer.start(500)  # Update every 500ms
    
    def stop_text_animation(self):
        """Stop the text animation"""
        self.animation_timer.stop()
    
    def update_animation_text(self):
        """Update the animation text in sequence"""
        self.animation_index = (self.animation_index + 1) % len(self.animation_text)
        self.text_label.setText(self.animation_text[self.animation_index])
    
    def showEvent(self, event):
        # Center in parent if we have one
        if self.parent():
            geometry = self.parent().geometry()
            self.move(
                geometry.center().x() - self.width() // 2,
                geometry.center().y() - self.height() // 2
            )
        super().showEvent(event)