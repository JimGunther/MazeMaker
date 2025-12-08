from matplotlib import pyplot as plt, patches, lines
from typing import cast, Self, List
import math
import random

#******************************************************************************************
#
# Square.py: Square class represents maze square functionality
# 
# Version 0.7
# Last updated 07.12.2025 15:51
# 
# *****************************************************************************************
class MMException(Exception):
    pass

class Square:

#class variables
    sq_sz = 10  # size of square for drawing

    @classmethod
    def setup(cls, dims: int): ##initiates class attributes
        cls.mazeDims = dims

    def __init__(self, r:int, c:int):
        self.row = r
        self.col = c
        self.code = 15
        self.ngh = [] # temporarily assign None
        self.ngh.append(None)      
        self.ngh.append(None)      
        self.ngh.append(None)      
        self.ngh.append(None) # 4 None objects initially     
        self.wet = False
        self.damp = False
        self.votes = 0
        self.trailNo = 0
        self.target = False
        self.attract = 0.0

    def drawMe(self) -> None:
        ax = plt.gca()
        yy = self.row * Square.sq_sz
        xx = self.col * Square.sq_sz
        c = "white"
        if self.trailNo == 1:
            c = "yellow"
        if self.damp:
            c = "lightgrey"
        if self.wet:
            c = "grey"
        if self.trailNo == 2:
            c = "pink"
        if self.trailNo > 2:
            c = "cyan"
        if self.target:
            c = "green"
        patch = patches.Rectangle((xx, yy), Square.sq_sz, Square.sq_sz, color=c)
        ax.add_patch(patch)
        self.drawFences()    
    
    def drawFences(self) -> None: # draws fence for ONE MM square
        if (self.code & 1) == 1: 
            self.drawLine(1, 0, False)
        if (self.code & 2) == 2: 
            self.drawLine(0, 0, True)
        if (self.code & 4) == 4: 
            self.drawLine(0, 0, False)
        if (self.code & 8) == 8: 
            self.drawLine(0, 1, True)

    def drawLine(self, y: int, x: int, vert: bool) -> None:
        ax = plt.gca()
        yy = (self.row + y) * Square.sq_sz
        xx = (self.col + x) * Square.sq_sz
        if vert:
            line = lines.Line2D((xx, xx), (yy, yy + Square.sq_sz), color="black")
        else:
            line = lines.Line2D((xx, xx + Square.sq_sz), (yy, yy), color="black")
        ax.add_line(line)

    def calcVotes(self, yTarget: int, xTarget: int) -> None:
        # give an attractiveness score to each square
        xd = (self.col - xTarget) * (self.col - xTarget)
        yd = (self.row - yTarget) * (self.row - yTarget)
        att = int(math.sqrt(xd + yd))
        att = int(math.sqrt(2.0) * Square.mazeDims) - att
        self.votes = att

    def getPos(self) -> tuple:
        return (self.row, self.col)
        
    def getNeighbour(self, i: int) -> Self | None:
        return self.ngh[i]
    
    def setNeighbour(self, i: int, sq: Self | None) -> None:
        if sq is not None:
            self.ngh[i] = sq

    def getTrailNo(self) -> int:
        return self.trailNo
    
    def setTrailNo(self, n) -> None:
        self.trailNo = n
    
    def setTarget(self, b: bool) -> None:
        self.target = b
    
    def getVotes(self) -> int:
        return self.votes

    def setVotes(self, v: int) -> None:
        self.votes = v

    def isEnclosed(self) -> bool:
        return self.code == 15

    def isFloodable(self) -> bool:
        return (self.trailNo == 0) and not self.wet
    
    def isTarget(self) -> bool:
        return self.target
    
    def isYellow(self) -> bool:
        return self.trailNo == 1
    
    def isWet(self) -> bool:
        return self.wet
    
    def flood(self) -> None:
        self.wet = True
        for i in range (0, 4):
            if self.getNeighbour(i) is not None:
                neigh = cast(Square, self.ngh[i])
                if neigh.isFloodable():
                    neigh.flood()   # RECURSIVE!

    def t1Neighbour(self) -> Self | None:
        for i in range(0, 4):
            if self.ngh[i] is not None:
                ngh = cast(Self, self.ngh[i])
                if ngh.trailNo == 1:
                    return ngh
        return None

    def wetCount(self) -> int:  # counts neighbours
        count = 0
        for i in range(0,4):
            if self.ngh[i] is not None:
                neigh = cast(Square, self.ngh[i])
                if (neigh.getTrailNo() == 0) and (neigh.isWet()):
                    count += 1
        return count

    def whiteCount(self) -> int: # includes white and light grey ????
        count = 0
        for i in range(0, 4):
            if self.ngh[i] is not None:
                neigh = self.ngh[i]
                if neigh.trailNo == 0:
                    count += 1
        return count
    
    def yellowCount(self) -> int:
        count = 0
        for i in range(0, 4):
            if self.ngh[i] is not None:
                neigh = self.ngh[i]
                if neigh.trailNo == 1:
                    count += 1
        return count
    
    def tryYellow(self) -> None: 
        assert (self.getTrailNo() == 0)  # is white
        # Find yellow neighbours and choose one
        yellNgh: List[Square] = []
        for i in range(0, 4):
            if self.ngh[i] is not None:
                if self.ngh[i].getTrailNo() > 0:
                    yellNgh.append(self.ngh[i])
        nYellow = len(yellNgh)
        if nYellow > 0: # we only choose white squares with at least one yellow neighbour
            if nYellow == 1:
                yNeigh = yellNgh[0] # no choice!
            else:
                r = random.randint(0, nYellow - 1)
                yNeigh = yellNgh[r]
            self.setTrailNo(4)
            # remove fence between
            Square.setFenceBetween(self, yNeigh, False)

    @classmethod
    def setFenceBetween(cls, sqA: Self, sqB: Self, tf: bool) -> None:
        origCode = sqA.code
        yd = abs(sqA.row - sqB.row)
        xd = abs(sqA.col - sqB.col)
        if (yd + xd) == 1:  # only do it for adjacent squares!
            if yd == 0: #side by side
                if sqA.col > sqB.col:
                    sq1 = sqA
                    sq2 = sqB
                else:
                    sq1 = sqB
                    sq2 = sqA# now sq1 is always the higher column number
                if tf:
                    sq1.code = sq1.code | 2
                    sq2.code = sq2.code | 8
                else:
                    sq1.code = sq1.code & 13
                    sq2.code = sq2.code & 7
            else: #above and below
                if sqA.row > sqB.row:
                    sq1 = sqA
                    sq2 = sqB
                else:
                    sq1 = sqB
                    sq2 = sqA
                if tf:
                    sq1.code = sq1.code | 4
                    sq2.code = sq2.code | 1
                else:
                    sq1.code = sq1.code & 11
                    sq2.code = sq2.code & 14
        revCode = sqA.code
        assert tf == (revCode > origCode), "check logic for fence between"
