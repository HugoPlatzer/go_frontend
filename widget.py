from PyQt5.QtWidgets import QLabel, QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QStackedLayout
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt
from game import Game, Phase

def renderSvg(renderer, element, width, height):
  #print("render {} {}".format(element, (width, height)))
  pixmap = QPixmap(width, height)
  pixmap.fill(Qt.transparent)
  painter = QPainter(pixmap)
  renderer.render(painter, element)
  painter.end()
  return pixmap

def overlayPixmaps(base, overlay, x, y):
    painter = QPainter(base)
    painter.drawPixmap(x, y, overlay)
    painter.end()

class BoardStoneWidget(QLabel):
  def __init__(self, point, parent):
    super(BoardStoneWidget, self).__init__(parent)
    self.setAttribute(Qt.WA_TransparentForMouseEvents)
    self.point = point

  def getSVGElement(self):
    mapping = {0 : None, 1 : "black_stone", 2 : "white_stone",
               3 : "black_territory", 4 : "white_territory"}
    mappingLast = {1 : "black_stone_last", 2 : "white_stone_last"}
    mappingSuicide = {1 : "black_stone_last_suicide",
                      2 : "white_stone_last_suicide"}
    color = self.parent().game.colorAtPoint(self.point)
    lastMove = self.parent().game.lastMove()
    lastPlayer = 2 if self.parent().game.currentPlayer() == 1 else 1
    if lastMove == self.point:
      if color == 0:
        return mappingSuicide[lastPlayer]
      return mappingLast[color]
    return mapping[color]

  def update(self):
    element = self.getSVGElement()
    if not element:
      self.clear()
      return
    
    width, height = self.parent().svgElementSize(element)
    x, y = self.parent().pointToXy(self.point)
    x -= width / 2
    y -= height / 2
    pixmap = renderSvg(self.parent().renderer, element, width, height)
    self.setPixmap(pixmap)
    self.setGeometry(x, y, width, height)
    print("updated point {}".format(self.point))

class BoardPlacementIndicatorWidget(QLabel):
  def __init__(self, parent):
    super(BoardPlacementIndicatorWidget, self).__init__(parent)
    self.setAttribute(Qt.WA_TransparentForMouseEvents)

  def updatePosition(self, mousePosition):
    point = self.parent().xyToPoint(*mousePosition)
    if point is None or not self.parent().game.isMoveLegal(point):
      self.setVisible(False)
    else:
      size = (self.size().width(), self.size().height())
      position = self.parent().pointToXy(point)
      position = (position[0] - size[0] / 2, position[1] - size[1] / 2)
      self.setGeometry(*position, *size)
      self.setVisible(True)
  
  def update(self):
    player = self.parent().game.currentPlayer()
    print("updateIndicator {}".format(player))
    if player == 1:
      size = self.parent().svgElementSize("black_stone_hover")
      pixmap = renderSvg(self.parent().renderer, "black_stone_hover", *size)
    else:
      size = self.parent().svgElementSize("white_stone_hover")
      pixmap = renderSvg(self.parent().renderer, "white_stone_hover", *size)
    self.setGeometry(self.pos().x(), self.pos().y(), *size)
    self.setPixmap(pixmap)
    self.setVisible(False)

class BoardWidget(QLabel):
  def __init__(self, game, renderer, parent = None):
    super(BoardWidget, self).__init__(parent)
    self.setMouseTracking(True)
    self.game = game
    game.boardChanged.connect(self.updateWidgets)
    self.renderer = renderer
    self.stoneWidgets = [BoardStoneWidget(i, self) for i in range(game.size() * game.size())]
    self.indicatorWidget = BoardPlacementIndicatorWidget(self)
    self.setMinimumSize(200, 200)

  def pointToXy(self, point):
    boardSize = self.game.size()
    row, col = point // boardSize, point % boardSize
    xSpacing = self.gridWidth / (boardSize - 1)
    ySpacing = self.gridHeight / (boardSize - 1)
    x = self.gridX + col * xSpacing
    y = self.gridY + row * ySpacing
    return (x, y)

  def xyToPoint(self, x, y):
    boardSize = self.game.size()
    xSpacing = self.gridWidth / (boardSize - 1)
    ySpacing = self.gridHeight / (boardSize - 1)
    row = round((y - self.gridY) / ySpacing)
    col = round((x - self.gridX) / xSpacing)
    if row < 0 or row >= boardSize or col < 0 or col >= boardSize:
      return None
    return row * boardSize + col

  def svgElementSize(self, element):
    svgGridRect = self.renderer.boundsOnElement("grid")
    svgElementRect = self.renderer.boundsOnElement(element)
    widthFactor = svgElementRect.width() / svgGridRect.width()
    heightFactor = svgElementRect.height() / svgGridRect.height()
    width = self.gridWidth * widthFactor
    height = self.gridHeight * heightFactor
    return (width, height)

  def update(self):
    svgBackgroundRect = self.renderer.boundsOnElement("background")
    svgBoardRect = self.renderer.boundsOnElement("board")
    svgGridRect = self.renderer.boundsOnElement("grid")
    backgroundWidth = self.size().width()
    backgroundHeight = self.size().height()
    boardHeight = backgroundHeight * svgBoardRect.height() / svgBackgroundRect.height()
    boardWidth = boardHeight * svgBoardRect.width() / svgBoardRect.height()
    boardX = backgroundWidth / 2 - boardWidth / 2
    boardY = backgroundHeight / 2 - boardHeight / 2
    self.gridWidth = boardWidth * svgGridRect.width() / svgBoardRect.width()
    self.gridHeight = boardHeight * svgGridRect.height() / svgBoardRect.height()
    gridXRatio = (svgGridRect.x() - svgBoardRect.x()) / svgBoardRect.width()
    gridYRatio = (svgGridRect.y() - svgBoardRect.y()) / svgBoardRect.height()
    self.gridX = boardX + gridXRatio * boardWidth
    self.gridY = boardY + gridYRatio * boardHeight
    pixmap = renderSvg(self.renderer, "background", backgroundWidth, backgroundHeight)
    boardPixmap = renderSvg(self.renderer, "board", boardWidth, boardHeight)
    overlayPixmaps(pixmap, boardPixmap, boardX, boardY)
    self.setPixmap(pixmap)

  def updateWidgets(self):
    for sw in self.stoneWidgets:
        sw.update()
    self.indicatorWidget.update()
  
  def resizeEvent(self, event):
    self.update()
    self.updateWidgets()
  
  def mouseMoveEvent(self, event):
    pos = (event.pos().x(), event.pos().y())
    self.indicatorWidget.updatePosition(pos)
  
  def mousePressEvent(self, event):
    pos = (event.pos().x(), event.pos().y())
    point = self.xyToPoint(*pos)
    if point is None or not self.game.isMoveLegal(point):
      return
    self.game.playMove(point)
    self.indicatorWidget.updatePosition(pos)

  def leaveEvent(self, event):
    pass
    self.indicatorWidget.updatePosition((-1, -1))

class GameInitWidget(QWidget):
  def __init__(self, game, parent):
    super(GameInitWidget, self).__init__(parent)
    self.game = game
    self.startButton = QPushButton("Start", self)
    self.startButton.clicked.connect(self.startGame)
    self.layout = QVBoxLayout()
    self.layout.addWidget(self.startButton)
    self.layout.addStretch(1)
    self.setLayout(self.layout)
  
  def startGame(self):
    self.game.startGame()

class GamePlayWidget(QWidget):
  def __init__(self, game, parent):
    super(GamePlayWidget, self).__init__(parent)
    self.game = game
    self.game.boardChanged.connect(self.updateLabels)
    self.titleLabel = QLabel(self)
    self.infoLabel = QLabel(self)
    self.resignButton = QPushButton("Resign", self)
    self.resignButton.clicked.connect(self.resignGame)
    self.passButton = QPushButton("Pass", self)
    self.passButton.clicked.connect(self.playPassMove)
    self.layout = QVBoxLayout()
    self.layout.addWidget(self.titleLabel)
    self.layout.addWidget(self.infoLabel)
    self.layout.addWidget(self.resignButton)
    self.layout.addStretch(1)
    self.layout.addWidget(self.passButton)
    self.setLayout(self.layout)
    self.updateLabels()
  
  def playPassMove(self):
    self.game.playMove(-1)
    
  def resignGame(self):
    self.game.resignGame()
  
  def updateLabels(self):
    currentPlayer = self.game.currentPlayer()
    if currentPlayer == 1:
      self.titleLabel.setText("Black to move")
    if currentPlayer == 2:
      self.titleLabel.setText("White to move")
    lastMoveText = "<strong>Last move</strong>:<br><font size=5>{}</font>"
    lastMoveText = lastMoveText.format(self.game.lastMoveStr())
    self.infoLabel.setText(lastMoveText)
  
class GameFinishedWidget(QWidget):
  def __init__(self, game, parent):
    super(GameFinishedWidget, self).__init__(parent)
    self.game = game
    self.game.resultChanged.connect(self.updateResult)
    self.titleLabel = QLabel("Game finished", self)
    self.infoLabel = QLabel(self)
    self.newGameButton = QPushButton("New game", self)
    self.newGameButton.clicked.connect(self.resetGame)
    self.layout = QVBoxLayout()
    self.layout.addWidget(self.titleLabel)
    self.layout.addWidget(self.infoLabel)
    self.layout.addWidget(self.newGameButton)
    self.layout.addStretch(1)
    self.setLayout(self.layout)
  
  def resetGame(self):
    self.game.initGame()
  
  def updateResult(self):
    resultText = "<strong>Result</strong>:<br><font size=5>{}</font>"
    resultText = resultText.format(self.game.resultStr())
    self.infoLabel.setText(resultText)
  
class GameWidget(QWidget):
  def __init__(self, parent = None):
    super(GameWidget, self).__init__(parent)
    self.game = Game()
    self.renderer = QSvgRenderer("theme.svg")
    self.boardWidget = BoardWidget(self.game, self.renderer, self)
    
    self.stackLayoutWidget = QWidget(self)
    self.stackLayoutWidget.setFixedWidth(150)
    self.initWidget = GameInitWidget(self.game, self.stackLayoutWidget)
    self.playWidget = GamePlayWidget(self.game, self.stackLayoutWidget)
    self.finishedWidget = GameFinishedWidget(self.game, self.stackLayoutWidget)
    self.stackLayout = QStackedLayout()
    self.stackLayout.addWidget(self.initWidget)
    self.stackLayout.addWidget(self.playWidget)
    self.stackLayout.addWidget(self.finishedWidget)
    self.stackLayoutWidget.setLayout(self.stackLayout)
    
    self.hboxLayout = QHBoxLayout()
    self.hboxLayout.addWidget(self.boardWidget)
    self.hboxLayout.addWidget(self.stackLayoutWidget)
    self.hboxLayout.setStretch(0, 1)
    self.hboxLayout.setContentsMargins(0, 0, 0, 0)
    self.setLayout(self.hboxLayout)
    self.game.phaseChanged.connect(self.update)
    self.update()
  
  def update(self):
    print("gwUpdate phase={}".format(self.game.phase))
    if self.game.phase == Phase.INIT:
      self.stackLayout.setCurrentWidget(self.initWidget)
    if self.game.phase == Phase.PLAY_HUMAN or self.game.phase == Phase.PLAY_ENGINE:
      self.stackLayout.setCurrentWidget(self.playWidget)
    if self.game.phase == Phase.FINISHED:
      self.stackLayout.setCurrentWidget(self.finishedWidget)
