from PyQt5.QtCore import QProcess
from PyQt5.QtWidgets import QApplication

import pexpect

p = QProcess()

def printQPOutput():
  print(p.readAll())

def readPexpect():
  p = pexpect.spawn("gnugo --mode gtp")
  p.sendline("version")
  p.expect("(.*)\n")
  print(p.match.group(1))
  p.sendline("vers")
  p.expect("=(.*)\n")
  print(p.match.group(1))

def readQProcess():
  p.start("gnugo --mode gtp")
  p.waitForStarted()
  p.write(b"vers\n")
  p.readyRead.connect(printQPOutput)

#readPexpect()
app = QApplication([])
readQProcess()
app.exec_()
