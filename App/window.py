from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        self.app = QApplication(sys.argv)  # Create QApplication first
        super().__init__()  # Then create window
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Desainia-MS-Tool')
        self.setGeometry(100, 100, 800, 600)
        
        label = QLabel('HELLO WORLD', self)
        label.setFont(QFont('Arial', 48, QFont.Weight.Bold))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(label)
        
    def run(self):
        self.show()
        return self.app.exec()  # Return exit code instead of calling sys.exit directly
