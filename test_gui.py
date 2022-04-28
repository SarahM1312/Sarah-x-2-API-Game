import sys

from PyQt5.QtWidgets import QApplication, QLabel,QPushButton, QBoxLayout,QWidget, QFileDialog
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5 import QtGui, QtCore

app = QApplication(sys,argv)
window = QWidget()
window.setWindowTitle("Welcome to Top Trumps by Sarah B and Sarah M")
window.setFixedWidth(1000)
window.setStyleSheet("background: #white;")

window.show()

def window():
   app = QApplication(sys.argv)
   win = QWidget()
   l1 = QLabel()
   l1.setPixmap(QPixmap("Pokemon-Transparent-Images.png"))

   vbox = QVBoxLayout()
   vbox.addWidget(l1)
   win.setLayout(vbox)
   win.setWindowTitle("Welcome to Pokemon Top Trumps!!")
   win.show()
   sys.exit(app.exec_())

if __name__ == '__main__':
   window()