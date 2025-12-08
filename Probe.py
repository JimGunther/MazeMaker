#******************************************************************************************
#
# Probe.py: mzsq class to handle maze path creation
# 
# Version 0.7
# Last updated 08.12.2025 11:51
# 
# *****************************************************************************************

from Square import Square
import random
from typing import cast, List

class Probe:

    def __init__(self, startSq: Square, trNo: int):
        self.reset(startSq, trNo)
    
    def reset(self, startSq: Square, trNo : int): # this adds one square to path (startsquare) when trNo == 1
        self.xPos = startSq.col
        self.yPos = startSq.row
        self.cmpDirn = 0 # 0=N, 1=W, 2=S, 3=E: irrelevant at start
        self.sq = startSq
        self.culdesac = False
        self.path: List[Square] = []
        if trNo == 1:   # don't destroy damp list for trail 2
            self.damp: List[Square] = []
        if trNo < 3:
            startSq.setTrailNo(trNo)
            self.path.append(startSq)   # trail starts at (its) start square        
        self.trailNo = trNo
    
    def removeTrail(self, trNo: int) -> None: #removes whole trail; resets steps and trail nos;
        while len(self.path) > 0:   
            lastSq = self.path.pop()    # reduces length by 1
            lastSq.setTrailNo(0) # resets the underlying squares' trail numbers
                                
    def getTrailSq(self, n: int) -> Square:
        return self.path[n]

    def move(self, trailNo: int, dims:int) -> Square | None: #returns new square or None if no valid moves
        oldY = self.yPos
        oldX = self.xPos
        validMoves: List[int] = []
        for i in range(0, 4):
            if self.isValidMove(i, trailNo):
                validMoves.append(i)
        # moves list length will be between 0 and 3
        lngth = len(validMoves)
#        if trailNo == 2:
#            print("Valid moves: " + str(lngth))
        if lngth == 0:
            self.culdesac = True
            return None
        if lngth == 1:
            chosenMv = validMoves[0] # no choice!
        else:
            chosenMv = self.randomChoice(validMoves)
        assert self.isValidMove(chosenMv, trailNo)

        nextSq = self.destMove(chosenMv) # nextSq is guaranteed to be not none
        nextSq = cast(Square, nextSq)
        yd = abs(oldY - nextSq.row)
        xd = abs(oldX - nextSq.col)
        assert (yd + xd) == 1, "Must be neighbour"   # move is one square vert or horiz
        self.dirn = chosenMv
        self.path.append(nextSq)
        #if trailNo == 2:
         #   print((nextSq.row, nextSq.col), end="")
        nextSq.setTrailNo(trailNo)
        self.sq = nextSq
        self.xPos = nextSq.col
        self.yPos = nextSq.row
        #print("p" + str((self.yPos, self.xPos)), end="")
        return nextSq
    
    def randomChoice(self, moves: list[int]) -> int:
    # squares reached by each move earn "votes" according to closeness to centre
        votes = []
        total = 0
        for m in moves: # possible moves (2 or 3), already filtered down to real mzsq objects (not None)
            trySq = cast(Square, self.destMove(m))
            v = trySq.getVotes()
            total += v
            for i in range(0, v):
                votes.append(m)
            if m == self.cmpDirn: # tip the balance in favour of straight ahead
                votes.append(m)
                votes.append(m)
        if total == 0:
            print ("No. of move options:" + str(len(moves)))

        r = random.randint(0, total - 1)
        chosenMv = votes[r]
        return chosenMv
        
    
    # generally move is valid if within maze anf trailNo of chosen move == 0
    def isValidMove(self, mv: int, tNo: int) -> bool: # mv: 0=N, 1=W, 2=S, 3=E
        nSq = self.sq.getNeighbour(mv)
        if nSq is None:
            return False # out of maze
        sq = cast(Square, nSq)   # now it's a real Square!
        if (sq.col == self.sq.col) and (sq.row == self.sq.row):
            return False
        #if tNo == 2:    #Next square must be wet!
         #   if not sq.isWet():
          #      return False
        return sq.getTrailNo() == 0

    def destMove(self, dirn:int) -> Square | None:    # dirn is 0=N, 1=W, 2=S, 3=E
        # OK to cast as "None" squares already ruled out
        sq = self.sq.getNeighbour(dirn)
        return sq
    
    def removeTrailFences(self):
        for i in range(1, len(self.path)):
            Square.setFenceBetween(self.path[i - 1], self.path[i], False)
    
    def updateTrailSquares(self, trNo: int) -> None:
        for i in range (0, len(self.path)):
            self.path[i].setTrailNo(trNo)
            self.path[i].wet = False
    
    def makeDamp(self) -> int:
        count = 0
        self.damp.clear()
        for sq in self.path:
            sq.wet = False
            for i in range(0, 4):
                ngh = sq.getNeighbour(i)
                if ngh is not None:
                    if ngh.isWet():
                        self.damp.append(ngh)
                        count += 1
        return count
                    
    def setSquare(self, sq: Square, tNo: int) -> None:
        self.sq = sq
        sq.setTrailNo(tNo)
 
    def atTarget(self) -> bool:
        return self.sq.isTarget()
    
    def getTrail(self):
        return self.path
    
    def getDampTrail(self) -> List[Square]: # all damp trail squares have at least one "wet" (lightgrey) neighbour
        self.damp.clear()
        for sq in self.path:
            if sq.wetCount() > 0:
                self.damp.append(sq)
        return self.damp
    
