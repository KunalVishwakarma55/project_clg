import sys
from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QLabel, QProgressBar, QFrame, QHBoxLayout, QApplication, QPushButton
from PySide6.QtCore import Qt, QSize, Signal, Slot
from PySide6.QtGui import QFont, QPixmap, QIcon
from ui.Home import Home 
from ui.STT import STT
from ui.TTS import TTS
from ui.lesson_ui import QuizUI
from ui.learning import LearningSection

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Setup UI components
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Sign Interpreter")
        self.setMinimumSize(1000, 720)
        # self.setWindowIcon(QIcon("assets/window-icon.png"))
        
        main_layout = QVBoxLayout(self)
        self.setStyleSheet("background-color: #f3f4f6;")

        
        
        # Sidebar
        self.navbar = self.create_nav_bar()
        main_layout.addWidget(self.navbar, 1)
        
        # Content area with stacked widget
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("background-color: white;border-radius: 10px;")
        main_layout.addWidget(self.content_area, 10)
        
        # Create tabs
        self.home = Home()
        self.STT = STT()
        self.TTS = TTS()
        self.lesson = QuizUI()
        self.learning = LearningSection()
        
        # Add tabs to stacked widget
        self.content_area.addWidget(self.home)
        self.content_area.addWidget(self.STT)
        self.content_area.addWidget(self.TTS)
        self.content_area.addWidget(self.lesson)
        self.content_area.addWidget(self.learning)
        
        # Connect the currentChanged signal to update button styles
        self.content_area.currentChanged.connect(self.update_button_styles)
        
    def create_nav_bar(self):
        # Sidebar container
        sidebar = QFrame()
        sidebar.setStyleSheet("background-color: black;border-radius: 10px;")
        sidebar_layout = QHBoxLayout(sidebar)
        
        # Logo
        logo = QLabel()
        logo.setAlignment(Qt.AlignCenter)
        logo.setPixmap(QPixmap("assets/logo.png").scaled(100, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setStyleSheet("margin:15px 10px")
        sidebar_layout.addWidget(logo)
        
        # Navigation buttons with default icons if specific ones aren't available
        nav_buttons = [
            ("Home", "assets/home.png"),
            ("Sign to Text", "assets/stt.png"),
            ("Text to Sign", "assets/tts.png"),
            ("ASL Test", "assets/test.png"),
            ("Lessons", "assets/lessons.png")
        ]
        
        self.nav_button_dict = {}
        
        # Active and inactive styles
        self.active_style = """
            QPushButton {
                color: white;
                background-color: #005f73;
                font-size: 15px;
                text-align: left;
                border-radius: 8px;
                padding: 10px 20px;
            }
        """
        
        self.inactive_style = """
            QPushButton {
                color: white;
                border: none;
                font-size: 15px;
                text-align: left;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #005f73;
            }
        """
        
        # Create navigation buttons
        for index, (text, icon_path) in enumerate(nav_buttons):
            button = QPushButton(text)
            
            # Try to load the icon, use a fallback if not found
            icon = QIcon(icon_path)
            if icon.isNull():
                # Use a default icon or just text if icon not found
                button.setText(text)
            else:
                button.setIcon(icon)
                button.setIconSize(QSize(20, 20))
            
            # Set initial style
            if index == 0:  # Home is active by default
                button.setStyleSheet(self.active_style)
            else:
                button.setStyleSheet(self.inactive_style)
                
            # Store button reference
            self.nav_button_dict[text] = button
            
            # Connect button directly with its index
            button.clicked.connect(lambda checked=False, idx=index: self.switch_tab(idx))
            
            sidebar_layout.addWidget(button)
        
        sidebar_layout.addStretch()
        return sidebar
    
    @Slot(int)
    def switch_tab(self, index):
        # If we're in a test (navbar disabled), don't allow switching
        if not self.navbar.isEnabled():
            return
        
        # Switch the current tab
        self.content_area.setCurrentIndex(index)
    
    @Slot()
    def update_button_styles(self):
        current_index = self.content_area.currentIndex()
        
        # Update styles for all buttons based on current index
        for i, (text, button) in enumerate(self.nav_button_dict.items()):
            if i == current_index:
                button.setStyleSheet(self.active_style)
            else:
                button.setStyleSheet(self.inactive_style)
    
    def update_navigation(self):
        """
        Update navigation bar connections when switching between sections.
        This ensures the navigation bar works correctly in all learning modes.
        """
        # Disconnect all existing connections
        for text, button in self.nav_button_dict.items():
            try:
                button.clicked.disconnect()
            except RuntimeError:
                pass  # If not connected, ignore error
        
        # Reconnect all buttons properly
        for index, text in enumerate(self.nav_button_dict.keys()):
            self.nav_button_dict[text].clicked.connect(
                lambda checked=False, idx=index: self.switch_tab(idx)
            )
        
        # Update button styles to reflect current state
        self.update_button_styles()
        
        # Make sure navbar is enabled
        self.navbar.setEnabled(True)
    
    # Add fullscreen toggle functionality
    # def keyPressEvent(self, event):
    #     # Toggle full screen with F11 key
    #     if event.key() == Qt.Key_F11:
    #         if self.isFullScreen():
    #             self.showNormal()
    #         else:
    #             self.showFullScreen()
    #     # Exit full screen with Escape key
    #     elif event.key() == Qt.Key_Escape and self.isFullScreen():
    #         self.showNormal()
    #     else:
    #         super().keyPressEvent(event)

def main():
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    # Start in windowed mode
    mainWin.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
