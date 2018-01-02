#!/usr/bin/python3

from PyQt5.QtWidgets import QApplication, QDesktopWidget
from PyQt5.QtCore import QRect
from sys import argv, exit
import signal
from widget import GameWidget

signal.signal(signal.SIGINT, signal.SIG_DFL)
app = QApplication(argv)
window = GameWidget()

window.setGeometry(0, 0, 700, 500)
desktopCenter = QDesktopWidget().availableGeometry().center()
fg = window.frameGeometry()
fg.moveCenter(desktopCenter)

window.move(fg.topLeft())
window.show()
app.exec_()
