from matplotlib import pyplot as plt, patches, lines
from typing import cast, Self, List
import math
import random

#******************************************************************************************
#
# Square.py: Square class represents maze square functionality
# 
# Version 0.4
# Last updated 05.04.2026 07:30
# 
# *****************************************************************************************
class MMException(Exception):
    pass

class Square:

#class variables
    sq_sz = 10  # size of square for drawing
    startCol = 0

    @classmethod
    def setup(cls, ht: int, wid: int): ##initiates class attributes
        cls.ht = ht
        cls.wid = wid

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
        self.start = False
        #self.attract = 0.0
    
    def drawMeMaker(self, ax) -> int:   #MazeMaker (left) pane
        '''drawMeMaker(): draws a square (fill clour and fences)
        parameter: ax: axis object for matplotlib to draw on
        returns: int: number of fences drawn in this square (0-4)
        '''
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
                c = "limegreen"
        if self.trailNo > 2:
            c = "darkgrey"
        if self.start:
            c = "chocolate"
        patch = patches.Rectangle((xx, yy), Square.sq_sz, Square.sq_sz, color=c)
        ax.add_patch(patch)
        return self.drawFences(ax)    
    
    def drawFences(self, ax) -> int: 
        '''drawFences(): draws finces for a single square
        parameter: ax: axis to draw upon by matplotlib
        returns: int: number of fences drawn (0-4)
        ''' 
        count = 0
        if (self.code & 1) == 1: 
            self.drawLine(ax, 1, 0, False)
            count += 1
        if (self.code & 2) == 2: 
            self.drawLine(ax, 0, 0, True)
            count += 1
        if (self.code & 4) == 4: 
            self.drawLine(ax, 0, 0, False)
            count += 1
        if (self.code & 8) == 8: 
            self.drawLine(ax, 0, 1, True)
            count += 1
        return count

    def drawLine(self, ax, y: int, x: int, vert: bool) -> None:
        '''drawLine(): draws a line representing a fence
        parameters:
            self: this Square object
            ax: axis to draw on by matplotlib
            y, x: int, int: coordinates of starting point for line
            vert: bool: True for vertical line; False for horizontal line
        returns: None
        '''
        yy = (self.row + y) * Square.sq_sz
        xx = (self.col + x) * Square.sq_sz
        if vert:
            line = lines.Line2D((xx, xx), (yy, yy + Square.sq_sz), color="black")
        else:
            line = lines.Line2D((xx, xx + Square.sq_sz), (yy, yy), color="black")
        ax.add_line(line)

#==========================================================================================================

    def calcVotes(self, yTarget: int, xTarget: int) -> None:
        '''calcVotes(): code to calculate the "attractiveness" of this square based upon nearness to Target
        parameters:
            self: this Square object
            yTarget: int: row of Targer Square
            xTarget: column of target square
        returns None (code puts the calculation value into self.votes)
        '''
        xd = (self.col - xTarget) * (self.col - xTarget)
        yd = (self.row - yTarget) * (self.row - yTarget)
        att = int(math.sqrt(xd + yd))
        att = int(math.sqrt(2.0 * Square.ht * Square.wid)) - att
        self.votes = att

    def getPos(self) -> tuple:
        '''getPos(): returns row, col as tuple
        parameter: self: this Square object
        returns: tuple[int, int]: Square position
        '''
        return (self.row, self.col)
        
    def getNeighbour(self, i: int) -> Self | None:
        '''getNeighbour(): returns the neighbouring Square in the specified direction (NWSE)
        parameters:
            self: this Square object
            i: int: direction
        returns: Square | None: the neighboutring Square or None if it's outside the maze outer wall
        '''
        return self.ngh[i]
    
    def setNeighbour(self, i: int, sq: Self | None) -> None:
        '''setNeighbour(): sets the neighbour to the specified Square
        parameters:
            self: this Square object
            i: int: direction of neighbour (NWSE)
            sq: Square | None: the Square object to set as neighbour
        returns: None
        '''
        if sq is not None:
            self.ngh[i] = sq

    def getTrailNo(self) -> int:
        '''getTrailNo(): returns self.trailNo as int'''
        return self.trailNo
    
    def setTrailNo(self, n: int) -> None:
        '''setTrailNo(): sets self.trailNo to input parameter n'''
        self.trailNo = n
    
    def setTarget(self, b: bool) -> None:
        '''setTarget(): sets self.target to input parameter True/False'''
        self.target = b
    
    def getVotes(self) -> int:
        '''getVotes(): returns self.vots as int'''
        return self.votes

    def setVotes(self, v: int) -> None:
        '''setVotes(): sets self.votes to input parameter v (int)'''
        self.votes = v

    def isCDS(self)-> bool:
        '''isCDS(): uses self.code and self.isStart() to determine whether Square is a culdesac (True/False)'''
        bFences = (self.code == 14) or (self.code == 13) or (self.code == 11) or (self.code ==7)
        return bFences and not self.isStart()   # start square can't be a CDS!
    
    def isStart(self) -> bool:
        '''isStart(): returns True if (self.row, self.col) match start square values (0, Sqare.startCol)'''
        return (self.row == 0) and(self.col == Square.startCol)
    
    def isEnclosed(self) -> bool:
        '''isEnclosed(): uses self.code to return whther the Square is "fully fenced"'''
        return self.code == 15

    def isFloodable(self) -> bool:
        '''isFloodable(): uses self.trailNo and self.wet to determine whether Square can be "flooded"'''
        return (self.trailNo == 0) and not self.wet
    
    def isTarget(self) -> bool:
        '''isTarget(): uses self.target to return True or False'''
        return self.target
    
    def isYellow(self) -> bool:
        '''isYellow(): returns True if self.trailNo == 1'''
        return self.trailNo == 1
    
    def isWet(self) -> bool:
        '''isWet(): returns self.wet'''
        return self.wet
    
    def flood(self) -> None:
        '''flood(): recursive method to set self.wet and neighbours to True'''
        self.wet = True
        for i in range (0, 4):
            if self.getNeighbour(i) is not None:
                neigh = cast(Square, self.ngh[i])
                if neigh.isFloodable():
                    neigh.flood()   # RECURSIVE!

    def t1Neighbour(self) -> Self | None:
        '''t1Neighbour(): looks fo a neighbouring Square on trail 1
        parameter: self: this Square object
        returns: the (first) trail1 Square or None if none found
        '''
        for i in range(0, 4):
            if self.ngh[i] is not None:
                ngh = cast(Self, self.ngh[i])
                if ngh.trailNo == 1:
                    return ngh
        return None

    def wetCount(self) -> int:
        '''wetCount(): counts the number of wet neighbours with no trailNo
        parameter: self: this Square object
        returns: int: count of wet Neighbours
        '''
        count = 0
        for i in range(0,4):
            if self.ngh[i] is not None:
                neigh = cast(Square, self.ngh[i])
                if (neigh.getTrailNo() == 0) and (neigh.isWet()):
                    count += 1
        return count

    def whiteCount(self) -> int:
        '''whiteCount(): counts the number of neighbours with no trail number
        parameter: self: this Square object
        returns: int: count of such neighbours
        '''
        count = 0
        for i in range(0, 4):
            if self.ngh[i] is not None:
                neigh = self.ngh[i]
                if neigh.trailNo == 0:
                    count += 1
        return count
    
    def yellowCount(self) -> int:
        '''yellowCount(): counts the number of neighbours on trail 1
        parameter: self: this Square object
        returns: int: count of such neighbours
        '''
        count = 0
        for i in range(0, 4):
            if self.ngh[i] is not None:
                neigh = self.ngh[i]
                if neigh.trailNo == 1:
                    count += 1
        return count
    
    def tryYellow(self) -> None:
        '''tryYellow(): searches remaining white (no trail) Squares with at least one non-white (trail > 0) neighbour, sets its trail number to 4 and removes the joining fence
        parameter: self: this Square object (must be no trail)
        returns: None
        ''' 
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
        '''hasFence() checks whether there is a fence in Square in specified direction
        parameters:
            self: this Square object
            nwse: int: direction specified
        returns: bool: True if fence, False if no fence
        ''' 
        t = 2**nwse
        return t & self.code != 0
    
    @classmethod
    def setFenceBetween(cls, sqA: Self, sqB: Self, tf: bool) -> None:
        '''setFenceBetween(): class method to set or remove a fence between 2 adjacent squares (by adjusting their self.code values)
        parameters:
            cls: the Square class object
            sqA: Square: first square
            sqB: Square: second square
            tf: bool: sets if True, removes if False
        returns: None
        '''
        #origCode = sqA.code
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
        #revCode = sqA.code
        #assert tf == (revCode >= origCode), "check logic for fence between"

    @classmethod
    def areNeigh(cls, sqA: Self, sqB: Self) -> bool:
        '''areNeigh(): class method to check if 2 Squares really are neighbours
        parameters:
            cls: the Square class object
            sqA: Square: first Square
            sqB: Square: secod Square
        returns: bool: True if neighbours else False
        '''
        yd = abs(sqA.row - sqB.row)
        xd = abs(sqA.col - sqB.col)
        return (yd + xd) == 1  # only do it for adjacent squares!
