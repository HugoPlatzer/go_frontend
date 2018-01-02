from PyQt5.QtCore import QObject, pyqtSignal
from board import Board
from enum import Enum
from collections import namedtuple

class Phase(Enum):
  INIT = 1
  PLAY_HUMAN = 2
  PLAY_ENGINE = 3
  FINISHED = 4

class ResultType(Enum):
  POINTS = 1
  RESIGN = 2

Result = namedtuple("Score", ["resultType", "scoreValue", "scoreBoard"])

class Game(QObject):
  boardChanged = pyqtSignal()
  phaseChanged = pyqtSignal()
  resultChanged = pyqtSignal()

  def __init__(self):
    super(QObject, self).__init__()
    self.initGame()

  def initGame(self):
    self.phase = Phase.INIT
    self.board = Board(9)
    self.result = None
    self.boardChanged.emit()
    self.phaseChanged.emit()

  def startGame(self):
    self.phase = Phase.PLAY_HUMAN
    self.phaseChanged.emit()

  def finishGame(self, result):
    self.phase = Phase.FINISHED
    self.result = result
    self.phaseChanged.emit()
    self.resultChanged.emit()
  
  def resignGame(self):
    self.finishGame(Result(ResultType.RESIGN, None, None))

  def size(self):
    return self.board.size
  
  def colorAtPoint(self, point):
    if self.phase is Phase.FINISHED and self.result.resultType is ResultType.POINTS:
      return self.result.scoreBoard[point]
    else:
      return self.board.positions[-1].position[point]

  def currentPlayer(self):
    return self.board.currentPlayer()

  def lastMove(self):
    return self.board.positions[-1].lastMove
  
  def lastMoveStr(self):
    move = self.lastMove()
    if move is None:
      return "-"
    if move < 0:
      moveStr = "Pass"
    else:
      moveStr = self.board.pointToNotation(move)
    return "{}. {}".format(self.moveCount(), moveStr)
  
  def moveCount(self):
    return len(self.board.positions) - 1
  
  def isMoveLegal(self, point):
    if self.phase is Phase.PLAY_HUMAN:
      return self.board.isMoveLegal(point)
    return False

  def scoreValue(self):
    return self.result.scoreValue

  def resultStr(self):
    if self.result.resultType == ResultType.POINTS:
      if self.scoreValue() < 0:
        return "W+{}".format(-self.scoreValue())
      if self.scoreValue() == 0:
        return "Jigo"
      if self.scoreValue() > 0:
        return "B+{}".format(self.scoreValue())
    if self.result.resultType == ResultType.RESIGN:
      if self.currentPlayer() == 1:
        return "W+R"
      if self.currentPlayer() == 2:
        return "B+R"

  def playMove(self, point):
    self.board.playMove(point)
    if self.moveCount() >= 2 \
        and self.board.positions[-1].lastMove < 0 \
        and self.board.positions[-2].lastMove < 0:
      score = self.board.score()
      self.finishGame(Result(ResultType.POINTS, *score))
    self.boardChanged.emit()
