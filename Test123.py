import sys

from PyQt5.QtCore import QSize

import pokemon_top_trumps
import random

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView, \
    QInputDialog, QMessageBox, QVBoxLayout, QGridLayout, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QCursor

# create welcome message
app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("Welcome to Pokemon Top Trumps")
window.setFixedWidth(1000)
window.move(2700, 200)
window.setStyleSheet("background: #161219;")

grid = QGridLayout()

image = QPixmap("Pokemon-Transparent-Images.png")
logo = QLabel()
logo.setPixmap(image)
logo.setAlignment(QtCore.Qt.AlignCenter)
grid.addwidget(logo, 0, 0)

window.setLayout(grid)
window.show()
sys.exit(app.exec())