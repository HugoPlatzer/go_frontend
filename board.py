from collections import namedtuple

BoardPosition = namedtuple("BoardPosition", ["position", "lastMove"])

class Board():
  def __init__(self, size):
    self.size = size
    self.initializeNeighbors()
    startPosition = [0] * (size * size)
    self.positions = [BoardPosition(startPosition, None)]
    self.legalMoves = dict()
  
  def initializeNeighbors(self):
    self.neighbors = []
    for point in range(self.size * self.size):
        row, col = point // self.size, point % self.size
        neighbors = [(row - 1, col), (row + 1, col),
                     (row, col - 1), (row, col + 1)]
        neighbors = [n for n in neighbors if n[0] >= 0 and n[0] < self.size
                                         and n[1] >= 0 and n[1] < self.size]
        self.neighbors.append([n[0] * self.size + n[1] for n in neighbors])
  
  def isMoveLegal(self, point):
    if point in self.legalMoves:
      return self.legalMoves[point]
    
    currentPosition = self.positions[-1].position
    if currentPosition[point] == 0:
      positionsBefore = set(str(p.position) for p in self.positions)
      positionAfter = self.playMovePosition(currentPosition, point, self.currentPlayer())
      isLegal = (str(positionAfter) not in positionsBefore)
    else:
      isLegal = False

    self.legalMoves[point] = isLegal
    return isLegal
  
  def playMove(self, point):
    color = self.currentPlayer()
    opponent = 2 if color == 1 else 1
    position = self.playMovePosition(self.positions[-1].position, point, color)
    self.legalMoves = dict()
    self.positions.append(BoardPosition(position, point))

  def removeIfDead(self, position, point):
    stack = [point]
    pointSet = set([point])
    
    while len(stack) > 0:
      currentPoint = stack.pop()
      for n in self.neighbors[currentPoint]:
        if position[n] == 0:
          return False
        elif position[n] == position[point] and n not in pointSet:
          stack.append(n)
          pointSet.add(n)
    
    for p in pointSet:
      position[p] = 0
    return True

  def playMovePosition(self, position, point, color):
    opponent = 2 if color == 1 else 1
    newPosition = position[:]
    
    if point < 0:
      return newPosition
    
    newPosition[point] = color
    for n in self.neighbors[point]:
      if newPosition[n] == opponent:
        self.removeIfDead(newPosition, n)
    self.removeIfDead(newPosition, point)
    return newPosition

  def reachesColor(self, position, point):
    stack = [point]
    pointSet = set([point])
    reachesBlack, reachesWhite = False, False
    
    while len(stack) > 0:
      currentPoint = stack.pop()
      for n in self.neighbors[currentPoint]:
        if position[n] == 1:
          reachesBlack = True
        if position[n] == 2:
          reachesWhite = True
        if position[n] == 0 and n not in pointSet:
          stack.append(n)
          pointSet.add(n)
    
    return (reachesBlack, reachesWhite, pointSet)

  def scorePosition(self, position):
    positionScored = position[:]
    
    for i in range(self.size * self.size):
      if positionScored[i] == 0:
        reachesBlack, reachesWhite, points = self.reachesColor(position, i)
        if reachesBlack and not reachesWhite:
          color = 3
        elif reachesWhite and not reachesBlack:
          color = 4
        else:
          color = 5
        for p in points:
          positionScored[p] = color
          
    score = 0
    for i in range(self.size * self.size):
      if positionScored[i] == 1 or positionScored[i] == 3:
        score += 1
      elif positionScored[i] == 2 or positionScored[i] == 4:
        score -= 1
      else:
        positionScored[i] = 0
    
    return (score, positionScored)

  def score(self):
    return self.scorePosition(self.positions[-1].position)

  def currentPlayer(self):
    if len(self.positions) % 2 == 0:
      return 2
    return 1

  def pointToNotation(self, point):
    row, col = point // self.size, point % self.size
    notationRow = self.size - row
    colStr = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
    return "{}{}".format(colStr[col], notationRow)
