from matplotlib import pyplot as plt, patches as pat, lines, artist
from typing import cast, Self, List
from Square import Square
import math
#******************************************************************************************
#
# Maisie.py: Maisie (mouse) class represents maze movement functionality
# 
# Version 0.9
# Last updated 15.12.2025 10:37
# 
# *****************************************************************************************

class Maisie:

#class variables

    def __init__(self, mazeDims: int):
        self.mazeDims = mazeDims
        self.minFilled = int(self.mazeDims * mazeDims * 4 / 5) # 80% filled
        self.rlMz = [[Square(r, c) for c in range(0, mazeDims)] for r in range(0, mazeDims)]
        self.mmz = [[Square(r, c) for c in range(0, mazeDims)] for r in range(0, mazeDims)]
        self.row = 0
        self.col = 0
        self.startCol = 0
        #self.sssq = self.mmz[0][self.startCol]
        self.prevRow = -1
        self.prevCol = -1
        self.heading = 0    # 0=N, 1=W, 2=S, 3=E
        self.prevHdg = 0
        self.trailNo = 0
        self.retrace = False
        self.leftFirst = True
        self.bBegin = True
        self.stop = False
        #self.maxVisits = 4
        #self.swapCount = 0
        Square.setup(mazeDims)
        
    def startup(self, startCol: int) -> None:
        self.col = startCol 
        self.startCol = startCol

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
    
    def reset(self, tNo: int, lFirst: bool):
        self.prevRow = self.row
        self.prevCol = self.col
        self.row = 0
        self.col = self.startCol
        self.heading = 0    # 0=N, 1=W, 2=S, 3=E
        self.prevHdg = 0
        self.trailNo = tNo
        self.retrace = False
        self.leftFirst = lFirst
        #self.stop = False

    def numUnvisited(self) -> int:
        count = 0
        for y in range(0, self.mazeDims):
            for x in range(0, self.mazeDims):
                 if self.mmz[y][x].numVisits == 0:
                     count += 1
        return count
    
    def gen1(self):
        i = 0
        while not self.stop:
            i += 1
            yield i

    #def gen2(self):
     #   i = 0
      #  while not self.atTarget():
       #     i += 1
        #    yield i

    def drawMe(self, ax) -> pat.RegularPolygon:
        sqSz = Square.sq_sz
        ssq = cast(Square, self.mmz[self.row][self.col])
        mid = sqSz / 2
        yCentre = ssq.row * sqSz + mid
        xCentre = ssq.col * sqSz + mid
        hfPi = math.pi * 0.5
        triangle = pat.RegularPolygon((xCentre, yCentre), 3, radius=mid - 1, orientation=self.heading*hfPi, color="lightyellow")
        ax.add_patch(triangle)
        return triangle

#    def textDisplay(self):
 #       cmpss = "NWSE"
  #      ssq = cast(Square, self.mmz[self.row][self.col])
   #     s = str((ssq.row, ssq.col)) + " "
    #    s += "H:" + cmpss[self.heading]
     #   s += " Fences: "
      #  for i in range(0,4):
       #     f = ssq.hasFence(i)
        #    if f:
         #       s += cmpss[i]
        #s += " No. unknown: " + str(self.nUnknown)
        #print(s)

    def go(self, ax, doScan: bool)-> bool:    # all the tasks needed in one Maisie move
        self.move()
        currSq = self.mmz[self.row][self.col]
        if currSq.numVisits == 0:
            self.scan()
        #self.textDisplay()
        self.swapSides()
        self.choose(self.leftFirst) # True for now: left first
        self.remove2patches(ax)
        prevSq = self.mmz[self.prevRow][self.prevCol]
        prevSq.drawMeMaisie(ax, False)
        currSq.drawMeMaisie(ax, True)
        patch = self.drawMe(ax)
        ax.add_patch(patch)
        nu = self.numUnvisited()
        if nu == 0:
            y, x = self.findTarget(ax)
            print("Target is " + str((y, x)))
            self.stop = True
            self.reset(2, True)
        return (currSq.row != 0) or (currSq.col != self.startCol)
    
    def remove2patches(self, ax) -> None: # and 4 lines
        if len(ax.patches) > 1:
            if ax.patches[-1] is pat.RegularPolygon: # this is to stop target and white squares from being removed
                patch = ax.patches[-1]
                patch.remove()
                patch = ax.patches[-1]
                patch.remove()
            if len(ax.lines) > 3:
                line = ax.lines[-1]
                line.remove()
                line = ax.lines[-1]
                line.remove()
                line = ax.lines[-1]
                line.remove()
                line = ax.lines[-1]
                line.remove()

    def scan(self):
        ssq = cast(Square, self.mmz[self.row][self.col])
        if ssq.numVisits == 0:
            # xfer data from rlMz to corresponding mmz
            self.mmz[self.row][self.col].code = self.rlMz[self.row][self.col].code
        
    def h2c(self, dirn: int) -> int: # direction 0=ahead, 1=left, 2=back, 3=right
        hdg = self.heading
        return (dirn + hdg) % 4
    
    def c2h(self, nwes: int) -> int: #nwes 0=N, 1=W, 2=S, 3=E
        hdg = self.heading
        return (nwes - hdg + 4) % 4
    
    def backToStart(self):
        if self.bBegin:
            self.bBegin = False
            return False
        return (self.row == 0) and (self.col == self.startCol)
    
    def swapSides(self):
        if self.backToStart(): #back at the start square
            #self.swapCount += 1
            self.leftFirst = not self.leftFirst
            if self.leftFirst:
                ss = "LF"
            else:
                ss = "RF"
            print("SWAP! " + ss)

    def choose(self, leftFirst: bool) -> int:    # output NWSE
        cmps = "NWSE"
        # Keep count of options at this square
        ssq = cast(Square, self.mmz[self.row][self.col])
        scoDir = (0, -1) # initialize

        # Now do the actual choosing (ALBR)
        if leftFirst:
            startDirn = 1
        else:
            startDirn = 3
        stp = 4 - startDirn # leftFirst => anticlockwise else clockwise
        
        self.prevHdg = self.heading
        dd = self.h2c(startDirn)    # now NWSE
        for i in range (0,4): # choose options
            fen = ssq.hasFence(dd)
            if not fen:
                sco = 4 - i
                ngh = ssq.getNeighbour(dd)
                if (ngh is not None) and (ngh.numVisits == 0):
                    sco += 5 # "bonus" points for not visited
                #print(cmps[dd] + ":" + str(sco) + ";", end="")
                if sco > scoDir[0]:
                    scoDir = (sco, dd)
            dd = (dd + stp) % 4
        #print ("=>" + cmps[scoDir[1]])
        self.heading = scoDir[1] # direction with highest score, including "bonus" points
        return self.heading #NWSE
    
    def move(self) -> bool:
        ssq = cast(Square, self.mmz[self.row][self.col])
        bStart = (self.row == 0) and (self.col == self.startCol)
        ssq.numVisits += 1  # set on leaving square (Is this best??)
        self.prevRow = self.row
        self.prevCol = self.col
        ngh = cast(Square, ssq.getNeighbour(self.heading))  # we know it's not None
        if ssq.isCDS() and not bStart:
            self.retrace = True
            Square.setFenceBetween(ngh, ssq, True)
        self.row = ngh.row
        self.col = ngh.col
        return self.retrace
    
    def resetVisits(self) -> None:
        for y in range(self.mazeDims):
            for x in range(self.mazeDims):
                self.mmz[y][x].numVisits = 0

    #def killWhite(self, ax) -> int:
     #   count = 0
      #  for y in range(self.mazeDims):
       #     for x in range(self.mazeDims):
        #        if self.mmz[y][x].numVisits == 0:
         #           count += 1
          #          self.mmz[y][x].code = 15
           #         self.mmz[y][x].drawMeMaisie(ax, False)
        #return count
    
    def findTarget(self, ax) -> tuple[int, int]:    # also sets target to True for the 4 target squares and draws them
        t = (-1, -1)
        for y in range(self.mazeDims - 1):
            for x in range(self.mazeDims - 1):
                sq = self.mmz[y][x]
                bOK = (sq.code & 9) == 0
                sq = self.mmz[y + 1][x + 1] # diagonal (NE)
                bOK = bOK and (sq.code & 6) == 0
                if bOK:
                    t = (y, x)
                    break
        yy, xx = t
        if (yy >= 0) and (xx >= 0):
            sq = self.mmz[yy][xx]
            sq.target = True
            sq.drawMeMaisie(ax, False)
            sq = self.mmz[yy][xx + 1]
            sq.target = True
            sq.drawMeMaisie(ax, False)
            sq = self.mmz[yy + 1][xx]
            sq.target = True
            sq.drawMeMaisie(ax, False)
            sq = self.mmz[yy + 1][xx + 1]
            sq.target = True
            sq.drawMeMaisie(ax, False)

        return t
    
    def atTarget(self) -> bool:
        return self.mmz[self.row][self.col].target
        
