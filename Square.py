from matplotlib import pyplot as plt, patches, lines
from typing import cast, Self, List
import math
import random

#******************************************************************************************
#
# Square.py: Square class represents maze square functionality
# 
# Version 0.93
# Last updated 13.12.2025 16:32
# 
# *****************************************************************************************
class MMException(Exception):
    pass

class Square:

#class variables
    sq_sz = 10  # size of square for drawing
    startCol = 0

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
        self.numVisits = 0

    def drawMeMaker(self, ax) -> None:   #MazeMaker (left) pane
        yy = self.row * Square.sq_sz
        xx = self.col * Square.sq_sz
        c = "white"
        if self.damp:
            c = "lightgrey"
        if self.wet:
            c = "grey"
        if self.trailNo == 1:
            c = "yellow"
            if self.target:
                c = "lightgreen"
        if self.trailNo == 2:
            c = "pink"
            if self.target:
                c = "green"
        if self.trailNo > 2:
            c = "cyan"
        #if self.target:
         #   c = "green"
        patch = patches.Rectangle((xx, yy), Square.sq_sz, Square.sq_sz, color=c)
        ax.add_patch(patch)
        self.drawFences(ax)    
    
    def drawFences(self, ax) -> None: # draws fence for ONE MM square: MazeMaker (left) pane 
        if (self.code & 1) == 1: 
            self.drawLine(ax, 1, 0, False)
        if (self.code & 2) == 2: 
            self.drawLine(ax, 0, 0, True)
        if (self.code & 4) == 4: 
            self.drawLine(ax, 0, 0, False)
        if (self.code & 8) == 8: 
            self.drawLine(ax, 0, 1, True)

    def drawLine(self, ax, y: int, x: int, vert: bool) -> None: # MazeMaker (left) pane
        yy = (self.row + y) * Square.sq_sz
        xx = (self.col + x) * Square.sq_sz
        if vert:
            line = lines.Line2D((xx, xx), (yy, yy + Square.sq_sz), color="black")
        else:
            line = lines.Line2D((xx, xx + Square.sq_sz), (yy, yy), color="black")
        ax.add_line(line)

    def drawMeMaisie(self, ax, bMaisie: bool) -> tuple[int, int]: # Maisie (right) pane      
        t = (0, 0) 
        c = "white"
        if self.numVisits > 0:
            c = "peachpuff"
        if self.code == 15:
            c = "grey"
        if self.isTarget():
            c = "green"
        if bMaisie:
            c = "orchid"
        rect = patches.Rectangle((self.col * self.sq_sz, self.row * self.sq_sz), self.sq_sz, self.sq_sz, color=c)
        ax.add_patch(rect)
        self.drawFences2(ax)
        t = (2, 4) # no. of patches and lines added
        return t

    def drawFences2(self, ax) -> None:
        msk = 1
        for i in range(0,4):
            blk = msk & self.code != 0
            self.drawLine2(i, ax, blk)
            msk = msk << 1  # double it

    def drawLine2(self, n: int, ax, blk: bool) -> lines.Line2D:
        sz = self.sq_sz
        yCorner = self.row * sz
        xCorner = self.col * sz
        match n:
            case 0:
                ys = sz
                xs = 0
                ye = sz
                xe = sz
            case 1:
                ys = 0
                xs = 0
                ye = sz
                xe = 0
            case 2:
                ys = 0
                xs = 0
                ye = 0
                xe = sz
            case 3:
                ys = 0
                xs= sz
                ye = sz
                xe = sz
        c = "peachpuff"
        if blk:
            c = "black"
        line = lines.Line2D((xs + xCorner, xe + xCorner), (ys + yCorner, ye + yCorner), color=c)
        ax.add_line(line)
        return line

#==========================================================================================================

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
    
    def setTrailNo(self, n: int) -> None:
        self.trailNo = n
    
    def setTarget(self, b: bool) -> None:
        self.target = b
    
    def getVotes(self) -> int:
        return self.votes

    def setVotes(self, v: int) -> None:
        self.votes = v

    def isCDS(self)-> bool:
        bFences = (self.code == 14) or (self.code == 13) or (self.code == 11) or (self.code ==7)
        return bFences and not self.isStart()   # start square can't be a CDS!
    
    def isStart(self) -> bool:
        return (self.row == 0) and(self.col == Square.startCol)
    
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

    def hasFence(self, nwse: int) -> bool: 
        t = 2**nwse
        return t & self.code != 0
    
    def countFences(self) -> int: # From MSquare
        count = 0
        x = 1
        for i in range(0,4):
            if (self.code & x) != 0:
                count += 1
            x = x << 1  #double it
        assert count < 4, "Square is fully enclosed!"
        return count

    def hasUnVNeigh(self) -> int: # returns direction (NWSE) of inVisited neighbour
        for d in range(0,4):
            ngh = self.getNeighbour(d)
            if ngh is not None:
                vis = ngh.numVisits
                if vis == 0:
                    return d
        return -1 # None available

    @classmethod
    def setFenceBetween(cls, sqA: Self, sqB: Self, tf: bool) -> None:
        #print("SFB", end="")
        origCode = sqA.code
        if Square.areNeigh(sqA, sqB):
            yd = abs(sqA.row - sqB.row)
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
        #assert tf == (revCode >= origCode), "check logic for fence between"

    @classmethod
    def areNeigh(cls, sqA: Self, sqB: Self) -> bool:
        yd = abs(sqA.row - sqB.row)
        xd = abs(sqA.col - sqB.col)
        return (yd + xd) == 1  # only do it for adjacent squares!
