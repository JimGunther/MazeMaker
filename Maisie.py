from matplotlib import pyplot as plt, patches as pat, lines
from typing import cast, Self, List
from MSquare import MSquare
import math
#******************************************************************************************
#
# Maisie.py: Maisie (mouse) class represents maze movement functionality
# 
# Version 0.2
# Last updated 04.12.2025 18:50
# 
# *****************************************************************************************

class Maisie:

#class variables

    def __init__(self, mazeDims: int, startCol: int):
        self.mazeDims = mazeDims 
        self.mmz = [[MSquare(r, c) for c in range(0, mazeDims)] for r in range(0, mazeDims)]
        self.sq = self.mmz[0][startCol]
        self.sq.code = 4
        self.heading = 0    # 0=N, 1=W, 2=S, 3=E
        self.prevHdg = 0
        self.rlMz = [[0 for _ in range(0, mazeDims)] for _ in range(0, mazeDims)]
        self.retrace = False
        self.nUnknown = mazeDims * (mazeDims - 1) * 2
        MSquare.setup(mazeDims)
        
    def startup(self) -> None:

        #set up neighbours: row and column 0 already set to None
        for y in range(0, self.mazeDims):
            for x in range(0, self.mazeDims):
                if x > 0:
                    self.mmz[y][x].setNeighbour(1, self.mmz[y][x-1])
                    self.mmz[y][x-1].setNeighbour(3, self.mmz[y][x])
                self.mmz[y][x].code = 0
                if y > 0:
                    self.mmz[y][x].setNeighbour(2, self.mmz[y-1][x])
                    self.mmz[y-1][x].setNeighbour(0, self.mmz[y][x])
                self.mmz[y][x].code = 0

        # Set outer fences
        for c in range(0, self.mazeDims):
            self.mmz[c][0].code += 2
            self.mmz[0][c].code += 4
            self.mmz[c][self.mazeDims - 1].code += 8
            self.mmz[self.mazeDims - 1][c].code += 1

    def getRealMaze(self, a: List[List[int]]) -> None:
        for y in range(0, self.mazeDims):
            for x in range(0, self.mazeDims):
                c = a[y][x]
                self.rlMz[y][x] = c
                #print(str(c) + " ", end="")
            #print()
    
    def drawMe(self) -> int:
        ax = plt.gca()
        nPatches = len(ax.patches)
        sqSz = MSquare.sq_sz
        ssq = cast(MSquare, self.sq)
        mid = sqSz / 2
        yCentre = ssq.row * sqSz + mid
        xCentre = ssq.col * sqSz + mid
        hfPi = math.pi * 0.5
        triangle = pat.RegularPolygon((xCentre, yCentre), 3, radius=mid - 1, orientation=self.heading*hfPi, color="lightyellow")
        ax.add_patch(triangle)
        return len(ax.patches) - nPatches # Number of patches added

    def textDisplay(self):
        cmpss = "NWSE"
        ssq = cast(MSquare, self.sq)
        s = str((ssq.row, ssq.col)) + " "
        s += "H:" + cmpss[self.heading]
        s += " Fences: "
        for i in range(0,4):
            f = ssq.getFence(i)
            if f:
                s += cmpss[i]
        s += " No. unknown: " + str(self.nUnknown)
        print(s)

    def scan(self): # 3 fences revealed:
        cmpss = "NWSE"
        # xfer data from rlMz to corresponding mmz
        # heading is NWSE not ALRE
        print("Heading:" + cmpss[self.heading] + " => ", end ="")
        a = self.heading
        l = (self.heading + 1) % 4
        r = (self.heading + 3) % 4
        print ("Scan: " + cmpss[a] + cmpss[l] + cmpss[r])
        c = self.xfer2Maisie(a) + self.xfer2Maisie(l) + self.xfer2Maisie(r) 
        assert self.sq is not None, "Maisie's square is None"
        self.sq.code = c
        print("Scan results: fences code:" + str(c))
        #print (" scanned/added")       

    # this method takes info from rlMz tuple and sets mmz[y][x] to code
    def xfer2Maisie(self, dirn: int) -> int:
        cmpss = "NWSE"
        ssq = cast(MSquare, self.sq)
        y = ssq.row
        x = ssq.col

        c = 2**dirn
        t = self.rlMz[y][x]
        v = c & t
        if (v != 0):
            return c
        else: 
            return 0

    def h2c(self, dirn: int) -> int: # direction 0=ahead, 1=left, 2=back, 3=right
        hdg = self.heading
        return (dirn + hdg) % 4
    
    def hasChoice(self) -> bool:
        ssq = cast(MSquare, self.sq)
        n = ssq.countFences()
        return (n < 3)
    
    def c2h(self, nwes: int) -> int: #nwes 0=N, 1=W, 2=S, 3=E
        hdg = self.heading
        return (nwes - hdg + 4) % 4
    
    def choose(self, leftFirst: bool) -> int:    # output NWSE
        # Keep count of options at this square
        ssq = cast(MSquare, self.sq)
        # Now do the actual choosing (ALBR)
        if leftFirst:
            startDirn = 1
        else:
            startDirn = 3
        stp = 4 - startDirn # leftFirst => anticlockwise else clockwise
        
        self.prevHdg = self.heading
        dd = self.h2c(startDirn)    # now NWSE
        x = 2**dd
        for _ in range (0,4):
            fen = ssq.getFence(dd)
            if not fen:
                break
            dd = (dd + stp) % 4
            x = 2**dd
        self.heading = dd
        return dd #NWSE
    
    def move(self) -> bool:
        ssq = cast(MSquare, self.sq)
        ssq.visited = True  # set on leaving square (Is this best??)
        prevSq = ssq
        self.sq = ssq.getNeighbour(self.heading)
        if abs(self.heading - self.prevHdg) == 2:
            self.retrace = True
        if self.retrace:
            MSquare.setFenceBetween(prevSq, ssq)
        return True
    # for now
    
