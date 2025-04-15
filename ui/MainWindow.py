import sys
from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QLabel, QProgressBar, QFrame, QHBoxLayout, QApplication, QPushButton
from PySide6.QtCore import Qt, QSize
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
        
        # Navigation buttons
        nav_buttons = [
            ("Home", "assets/"),
            ("Sign to Text", "assets/"),
            ("Text to Sign", "assets/"),
            ("ASL Test", "assets/"),
            ("Lessons", "assets/")
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
            button = QPushButton()
            button.setText(text)
            button.setIcon(QIcon(icon_path))
            button.setIconSize(QPixmap(icon_path).scaled(20, 20, Qt.KeepAspectRatio).size())
            button.setStyleSheet(self.inactive_style)
            sidebar_layout.addWidget(button)
            self.nav_button_dict[text] = button
            
            # Connect button click to change tab and active status
            button.clicked.connect(lambda _, idx=index: self.switch_tab(idx))
        
        sidebar_layout.addStretch()
        return sidebar
    
    def switch_tab(self, index):
        current_widget = self.content_area.currentWidget()
        
        # If we're in a test (navbar disabled), don't allow switching
        if not self.navbar.isEnabled():
            return
        
        # Switch the current tab
        self.content_area.setCurrentIndex(index)
        
        # Update styles for all buttons
        self.update_button_styles()
    
    def update_button_styles(self):
        # Update styles for all buttons based on current index
        for text, button in self.nav_button_dict.items():
            if self.content_area.currentIndex() == list(self.nav_button_dict.keys()).index(text):
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
            button.clicked.disconnect()
        
        # Reconnect all buttons
        for index, text in enumerate(self.nav_button_dict.keys()):
            self.nav_button_dict[text].clicked.connect(
                lambda _, idx=index: self.switch_tab(idx)
            )
        
        # Update button styles to reflect current state
        self.update_button_styles()
        
        # Make sure navbar is enabled
        self.navbar.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
