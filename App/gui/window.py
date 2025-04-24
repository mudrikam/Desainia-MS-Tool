from PyQt6.QtWidgets import QMainWindow, QLabel, QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QScreen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Desainia MS Tool")
        
        # Set fixed size 800x600
        self.setFixedSize(800, 600)
        
        # Center window on screen
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        
        # Create and set up Hello World label
        label = QLabel("Hello World", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(label)
