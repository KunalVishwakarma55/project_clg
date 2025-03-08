from PySide6.QtWidgets import QApplication, QLabel, QMainWindow
from PySide6.QtGui import QMovie
import os

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Loading Spinner Test")
        self.setGeometry(100, 100, 400, 300)

        # Create a loading spinner
        self.loading_spinner = QLabel(self)
        gif_path = os.path.abspath("assets/loading.gif")
        self.loading_movie = QMovie(gif_path)
        
        if not self.loading_movie.isValid():
            print(f"Error: GIF file not found or invalid at path: {gif_path}")
        else:
            print("GIF loaded successfully")

        self.loading_spinner.setMovie(self.loading_movie)
        self.loading_spinner.setFixedSize(200, 200)
        self.loading_spinner.move(70, 100)  # Position manually
        self.loading_spinner.setStyleSheet("background-color: red;")
        self.loading_spinner.show()
        self.loading_movie.start()

        # Debugging: Check if the GIF is playing
        if self.loading_movie.state() == QMovie.Running:
            print("GIF is playing")
        else:
            print("GIF is not playing")

if __name__ == "__main__":
    app = QApplication([])
    window = TestWindow()
    window.show()
    app.exec()