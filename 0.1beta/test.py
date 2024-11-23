from PyQt5 import uic
from PyQt5.QtCore import QSize
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtWidgets import QApplication, QTextBrowser, QComboBox
from PyQt5.QtGui import QPixmap, QIcon
from threading import Thread
import time
import os

class Stats:
    def __init__(self):
        self.ui = uic.loadUi("界面设计.ui")
        self.ui.show()
app = QApplication([])
stats = Stats()
stats.ui.show()
app.exec_()
