#******************************************************************************************
#
# Probe.py: mzsq class to handle maze path creation
# 
# Version 0.8
# Last updated 04.04.2025 15:31
# 
# *****************************************************************************************

from Square import Square
import random
from typing import cast, List

class Probe:

    def __init__(self, startSq: Square, trNo: int):
        self.reset(startSq, trNo)
    
    def reset(self, startSq: Square, trNo : int) -> None:
        '''reset(): restores various variables when a trail needs to be restarted (NB:this adds one square to path (startsquare) when trNo == 1)
        parameters:
            self: this Probe object
            startSq: Square: start square
            trNo: int: trail number (1, 2 or 3) trail no 3 is for all culdesac trails
        returns: None
        '''
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
    
    def removeTrail(self) -> None: 
        '''removeTrail(): removes whole trail and resets its Squares' trail number to 0
        parameters:
            self: this Probe object
        returns: None
        '''
        while len(self.path) > 0:   
            lastSq = self.path.pop()    # reduces length by 1
            lastSq.setTrailNo(0) # resets the underlying squares' trail numbers
                                
    def getTrailSq(self, n: int) -> Square:
        '''getTrailSq() returns the nth Square in the trail (aka path)
        parameters:
            self: this Probe object
            n: int: index number of 
        returns: Square: nth in trail
        '''
        return self.path[n]

    def move(self, trailNo: int) -> Square | None: #returns new square or None if no valid moves
        '''move(): moves the Probe object to a new Square, using randomised choice
        parameters:
            self: this Probe object
            trailNo: int: trailNo (1, 2 or 3)
        returns: Square | None: new Square to move to, if available, or None if no move possible (the flag self.culdesac is also set to True in this case)
        '''
        oldY = self.yPos
        oldX = self.xPos
        validMoves: List[int] = []
        for i in range(0, 4):
            if self.isValidMove(i):
                validMoves.append(i)
        # moves list length will be between 0 and 3
        lngth = len(validMoves)
        if lngth == 0:
            self.culdesac = True
            return None
        if lngth == 1:
            chosenMv = validMoves[0] # no choice!
        else:
            chosenMv = self.randomChoice(validMoves)
        assert self.isValidMove(chosenMv)

        # double-check code to assure move is really to a neighbouring square
        nextSq = self.destMove(chosenMv) # nextSq is guaranteed to be not none
        nextSq = cast(Square, nextSq)
        yd = abs(oldY - nextSq.row)
        xd = abs(oldX - nextSq.col)
        assert (yd + xd) == 1, "Must be neighbour"   # move is one square vert or horiz

        # update various Probe and Square variables
        self.dirn = chosenMv
        self.path.append(nextSq)
        nextSq.setTrailNo(trailNo)
        self.sq = nextSq
        self.xPos = nextSq.col
        self.yPos = nextSq.row

        return nextSq
    
    def randomChoice(self, moves: List[int]) -> int:
        '''randomChoice(): the method with the random choosing algorithm
        parameters:
            self: this Probe object
            moves: List[int]: list of possible directions to move (in range 0->3 NWSE)
        returns: int: chosen direction
        '''
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
            print ("No. of move options:" + str(len(moves))) # NB: this print should never happen!

        r = random.randint(0, total - 1)
        chosenMv = votes[r]
        return chosenMv
        
    
    # generally 
    def isValidMove(self, mv: int) -> bool: # mv: 0=N, 1=W, 2=S, 3=E
        '''isValidMove(): checks validity: a move is valid if probe stays within the maze and trailNo of chosen move == 0
        parameters:
            self: this Probe object
            mv: int: move (i.e direction) to validate
        returns: bool: True if valid, else False
        '''
        nSq = self.sq.getNeighbour(mv)
        if nSq is None:
            return False # out of maze
        sq = cast(Square, nSq)   # now it's a real Square!
        if (sq.col == self.sq.col) and (sq.row == self.sq.row):
            return False
        return sq.getTrailNo() == 0

    def destMove(self, dirn: int) -> Square | None: 
        '''destMove(): returns the Square in the stated direction
        parameters:
            self: this Probe object
            dirn: int (0-3): 0=N, 1=W, 2=S, 3=E
        returns: Square | None: neighbouring square in stated direction: NB: "None" will never happen: previously found invalid
        '''
        # NB it's OK to cast as "None" squares already ruled out
        sq = self.sq.getNeighbour(dirn)
        return sq
    
    def removeTrailFences(self) -> None:
        '''removeTrailFences(): removes all fences between trail Squares
        parameter: self: this Probe object
        returns: None
        '''
        for i in range(1, len(self.path)):
            Square.setFenceBetween(self.path[i - 1], self.path[i], False)
    
    def updateTrailSquares(self, trNo: int) -> None:
        '''upDateTrailSquares(): sets the trail number and resets the "wet" attribute for all trail Squares
        parameters:
            self: this Probe object
            trNo: int trail number
        returns: None
        '''
        for i in range (0, len(self.path)):
            self.path[i].setTrailNo(trNo)
            self.path[i].wet = False
    
    def makeDamp(self) -> int:
        '''makeDamp(): creates the "damp" trail: a subset of the trail where each square has at least one "wet" neighbour
        parameter: self: this Probe object
        returns: int: number of damp squares
        '''
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
        '''setSquare(): sets the Probe's current square and its trail number
        parameters:
            self: this Probe object
            sq: Square: object to Probe's current square
            tNo: int: trail number
        returns: None
        '''
        self.sq = sq
        sq.setTrailNo(tNo)
 
    def atTarget(self) -> bool:
        '''atTarget(): checks if probe has reached a target square (in Quad)
        parameter: self: this Probe object
        returns: bool: True if target reached, else False
        '''
        return self.sq.isTarget()
    
    def getTrail(self) -> List[Square]:
        '''getTrail(): returns the probe's current trail
        parameter: self: this Probe object
        returns: List[Square]: the current trail
        '''
        return self.path
    
    def getDampTrail(self) -> List[Square]: # all damp trail squares have at least one "wet" (lightgrey) neighbour
        '''getDampTrail(): returns the damp trail (see makeDamp() above for definition of "damp")
        parameter: self: this Probe object
        returns: List[Square]: the current damp trail
        '''
        self.damp.clear()
        for sq in self.path:
            if sq.wetCount() > 0:
                self.damp.append(sq)
        return self.damp
    
