from matplotlib import pyplot as plt, patches, lines
from typing import cast, Self, List

#******************************************************************************************
#
# MSquare.py: MSquare class represents maze square as known by Maisie
# Version 0.3
# Last updated 05.12.2025 09:21
# 
# *****************************************************************************************

class MSquare:

#class variables
    sq_sz = 10  # size of square for drawing

    @classmethod
    def setup(cls, dims: int): ##initiates class attributes
        cls.mazeDims = dims

    def __init__(self, r:int, c:int):
        self.sq_sz = 10
        self.row = r
        self.col = c
        self.ngh = []# temporarily assign None
        self.ngh.append(None)      
        self.ngh.append(None)      
        self.ngh.append(None)      
        self.ngh.append(None) # 4 None objects initially     
        self.code = 0 # unknow all fences initially
        self.visited = False

    def drawMe(self, bMaisie: bool) -> tuple[int, int]:       
        ax = plt.gca()
        nPatches = len(ax.patches)
        nLines = len(ax.lines)
        t = (0, 0) 
        c = "white"
        if self.code == 15:
            c = "grey"
        if bMaisie:
            c = "orchid"
        rect = patches.Rectangle((self.col * self.sq_sz, self.row * self.sq_sz), self.sq_sz, self.sq_sz, color=c)
        ax.add_patch(rect)
        self.drawMaiFences()
        newP = len(ax.patches)
        newL = len(ax.lines)
        t = (newP - nPatches, newL - nLines) # patches and lines added
        return t

    def drawMaiFences(self) -> None:
        msk = 1
        for i in range(0,4):
            if (msk & self.code) != 0:
                self.drawLine(i)
            msk = msk << 1  # double it

    def drawLine(self, n: int) -> None:
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
        line = lines.Line2D((xs + xCorner, xe + xCorner), (ys + yCorner, ye + yCorner), color="black")
        plt.gca().add_line(line)

    def getPos(self) -> tuple:
        return (self.row, self.col)
        
    def getNeighbour(self, i: int) -> Self | None:
        return self.ngh[i]
    
    def setNeighbour(self, i: int, sq: Self) -> None:
        if sq is not None:
            self.ngh[i] = sq
    
    def getFence(self, nwse: int) -> bool:
        t = 2**nwse
        return t & self.code != 0
    
    def countFences(self) -> int:
        count = 0
        x = 1
        for i in range(0,4):
            if (self.code & x) != 0:
                count += 1
            x = x << 1  #double it
        assert count < 4, "Square is fully enclosed!"
        return count

    @classmethod
    def setFenceBetween(cls, sqA: Self, sqB: Self) -> None:
        yd = abs(sqA.row - sqB.row)
        xd = abs(sqA.col - sqB.col)
        assert (yd + xd) == 1, "Not adjacent: " + str((sqA.row, sqA.col)) + ("<->") + str((sqB.row, sqB.col))
        if yd != 0: #above and below
            if sqA.col > sqB.col:
                sqA.code |= 4
                sqB.code |= 1
            else:
                sqA.code |= 1
                sqB.code |= 4
        else: #side by side
            if sqA.row > sqB.row:
                sqA.code |= 2
                sqB.code |= 8
            else:
                sqA.code |= 8
                sqB.code |= 2
