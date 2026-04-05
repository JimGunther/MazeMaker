#******************************************************************************************
#
# MazeMaker.py: controlling code for maze maker: designer only (revision in progress)
# 
# Version 0.4
# Last updated 04.04.2026 15:42
#  
# *****************************************************************************************

#from matplotlib import pyplot as plt
#import matplotlib.animation as anim
from typing import List
import random
from datetime import datetime
#import time
#import sys
from Square import Square, MMException
from Probe import Probe
from View import View
import math

print()
ht = 0
wid = 0
# First, get maze size (height, width) from user
ctnu = True
while ctnu:
    try:
        ht = int(input("\nHeight of maze:"))
        ctnu = False
    except ValueError:
        print("Number unrecognised: try again!")
ctnu = True
while ctnu:
    try:
        wid = int(input("\nWidth of maze:"))
        ctnu = False
    except ValueError:
        print("Number unrecognised: try again!")

sqSize = 10 # actaully square: unimportant as just for display!
startCol = 0
startRow = 0
endCol = 0
endRow = 0
retries = 0
mz = [[Square(r, c) for c in range(0, wid)] for r in range(ht)]
sqStart = mz[0][0] # to make sqStart a Square object
sqTarget = mz[0][0] # to make sqTarget a Square object
p = Probe(sqStart, 0)
vu = View(ht, wid, sqSize)

# -----------------------------------------------------------------------------------------------------
def startup() -> None:
    # Code which only needs to run once
    global minDamp
    global h
    global mz
    global ht
    global wid

    z = int(math.sqrt(ht * wid))
    minDamp = z / 2 + 1
    Square.setup(ht, wid)
    dt = datetime.timestamp(datetime.now())
    random.seed(dt) # seed randomizer

    #set up neighbours: row and column 0 already set to None
    for y in range(0, ht):
        for x in range(0, wid):
            if x > 0:
                mz[y][x].setNeighbour(1, mz[y][x-1])
                mz[y][x-1].setNeighbour(3, mz[y][x])
            if y > 0:
                mz[y][x].setNeighbour(2, mz[y-1][x])
                mz[y-1][x].setNeighbour(0, mz[y][x])

def prepare(prevTgt: Square, trNo: int) -> tuple[Square, Square]:    # use only for trNo == 1 or 2
    '''prepare() resets values needed at the start of trails 1 and 2 (yellow, pink)
        parameters:
            prevTgt: Square object: the Square at the bottom left of the target quad (if already known)
            trNo: int: trail number (1 or 2)
        returns: tuple[Square, Square]: tuple of 2 Square object representing start square and target square (as defined 2 lines above)
    ''' 
    # (1) Initial creation of maze----------------------------------------------------------------------------
    global ht, wid
    global retries
    global sqTarget
    global startCol
    
    # Clean up first
    for y in range(0, ht):
        for x in range(0, wid):
            sq = mz[y][x]
            sq.code = 15
            sq.setTrailNo(0)
            sq.wet = False
            sq.damp = False
            sq.target = False
    setupTargetQuad(prevTgt, False)
    
    # further initialization for trail 1 only------------------------------------------------------------------
    if (trNo == 1):
        # Set startSquare and target square (bottom left corner of quad)
        startCol = random.randint(0, wid - 1)
        Square.startCol = startCol
        startRow = 0
        print ("Start square: " + str((startRow, startCol)) + "; ", end="")

        minRow = int(ht / 2)
        if minRow == ht - 2:
            targetRow = minRow
        else:
            targetRow = random.randint(minRow, ht - 2)
    
        assert int(ht - 2) >= minRow, "Valid range for target row"
        targetCol = random.randint(0, wid - 2)
        assert int(wid - 2) > 0, "Valid range for target column"
        
        # NB: the following are set up in the Square __init__() method: trailNo => 0, code to 15
        
        sqStart = mz[startRow][startCol]
        sqStart.start = True
        sqStart.setTrailNo(1)
        sqTarget = mz[targetRow][targetCol]
        print("Target square: " + str((targetRow, targetCol)))
        setupTargetQuad(sqTarget, True)
    
    retries = 0

    # Assign "attraction" votes--------------------------------------------------
    for y in range(0, ht):
        for x in range(0, wid):
            mz[y][x].calcVotes(targetRow, targetCol)

    return (sqStart, sqTarget)

# END METHOD prepare()------------------------------------------------------------------------------------

def setupTargetQuad(sqTgt: Square, tf: bool) -> None:
    '''setupTargetQuad(): set all 4 target flags and delete fences between them (tf == True) else reverse the changes
        parameters:
            sqTgt: Square object at bottom left corner of target quad
            tf: boolean: clears the inner quad fences if true, else replaces them
        returns: None
    '''
    targetRow = sqTgt.row
    targetCol = sqTgt.col
    for i in range(0,2):
        for j in range(0,2):
            mz[targetRow + i][targetCol + j].setTarget(tf)
            mz[targetRow][targetCol].setTrailNo(0)
    if tf:  # delete central fences
        mz[targetRow][targetCol].code = 6
        mz[targetRow + 1][targetCol].code = 3
        mz[targetRow][targetCol + 1].code = 12
        mz[targetRow + 1][targetCol + 1].code = 9
    else: # restore fences
        mz[targetRow][targetCol].code = 15
        mz[targetRow + 1][targetCol].code = 15
        mz[targetRow][targetCol + 1].code = 15
        mz[targetRow + 1][targetCol + 1].code = 15

    
# Trail makers section----------------------------------------------------------------------------

def cleanup(trNo) -> None:
    '''cleanup(): resets Squares' trailNo attribute
        parameter: trNo: int trail number for cleanup
        returns: None
    '''
    count = 0
    for y in range(0, ht):
        for x in range(0, wid):
            if mz[y][x].getTrailNo() == trNo: #????
                mz[y][x].setTrailNo(0)
                count += 1
    print (str(count) + " squares cleaned up.")

# innermost loop: makes trail to target OR culdesac
def trailMake(startSq: Square, p: Probe, trNo: int)-> bool: # True if at target
    '''trailMake(): creates trail to target or culdesac (depends on random chance)
    parameters:
        startSq: Square object where new trail begins
        p: Probe object to do the "trailblazing"
        trNo: tail number
    returns: bool: True if Target reached, else False (culdesac)
    '''
    global ht, wid
    global retries
    
    innerLoopCount = 0
    p.reset(startSq, trNo)
    cdsCount = 0
    #print("Yellow count: " + str(trailCount(1)))
    bStop = False

    while not bStop:
        innerLoopCount += 1
        sq = p.move(trNo)
        if sq is not None:
            assert len(p.path) > 0
            p.setSquare(sq, trNo)
            if p.atTarget():
                bStop = True
                if trNo < 3:
                    print("Reached target: " + str((p.yPos, p.xPos)))
                    # p trail length measures path itself; trailCount() counts [yellow] squares
                    #assert len(p.path) == trailCount(trNo), "Path length != yellowCount" + str(len(p.path)) + ";" + str(trailCount(trNo))
        else:
            assert(p.culdesac)
            print("CDS;", end="")
            bStop = True
            p.removeTrail()
            assert len(p.path) == 0, "probe trail not empty!"
            #p.reset(startSq, trNo)

            retries += 1
            if innerLoopCount > 60:
                print ("Too many iterations")
                print("__________________________________________________________________")
                print("RESTART")
                raise MMException("Restart")
        if p.atTarget() and (trNo < 3):
            bStop = True

    return p.atTarget()
    
def cdsTrailMake(startSq: Square, p: Probe, trNo: int)-> bool:
    '''cdsTailMake(): code to create all trials after the first two, certain to end in a culdesac
        parameters:
            startSq: Square object where trail starts
            p: Probe object to blaze the trail
            trNo: int: invariably == 3 (generic for all but trails 1 and 2)
        returns: bool: True if culdesac ending: should always be so!
    ''' 
    innerLoopCount = 0
    p.reset(startSq, trNo)
    while not p.culdesac: # loop until culdesac
        innerLoopCount += 1
        sq = p.move(trNo)
        if sq is not None:
            p.setSquare(sq, trNo)
        else:
            assert(p.culdesac)
    return p.culdesac

def t1TrailMake(prevTgt: Square, p: Probe) -> bool: 
    '''t1TrailMake(): makes trail 1 and checks that enough flooded Squares border it: tail is abandoned and restarted if not so
        parameters:
            prevTgt: target Square object (already been set) at bottom-left corner of Target Quad
            p: Probe object to make trail
        returns: bool: True if enough wet adjacent squares, else False
    '''
    global sqStart
    global sqTarget
    global retries
    
    #prepare(1) includes setting sqTarget and trailNo to 1 
    sqStart, sqTarget = prepare(prevTgt, 1)
    retries = 0
    bSoggy = False # soggy = enough choices to start second trail
    p.reset(sqStart, 1)
    print("====================================================================")
    print ("Trail 1: begin")

    while not bSoggy:
        #soggyLoopCount += 1
        bOK = False
        while not bOK:
            bOK = trailMake(sqStart, p, 1)  # trail is culdesac or at target
            retries += 1
        sqTarget.flood() # "Flood" the accessible white squares => grey
        bSoggy = isSoggy()
    nDamp = p.makeDamp()
    print ("Path length: " + str(len(p.path)))
    #print ("No. damps: " + str(nDamp))
    p.removeTrailFences()
    p.updateTrailSquares(1)
    return bSoggy

def t2TrailMake(damps: List[Square], p: Probe) -> bool:
    '''t2TrailMake(): creates trail 2 from any square on trail 1 with at least one "flooded" neighbour
    parameters:
        damps: List[Square]: subset of trail1 Squares which have at least one flooded neighbour (and so a trail 2 starting point candidate)
        p: Probe object to make the trail
    returns: bool: always True (assuming retries keep happening) 
    '''
    global sqTarget
    # (2) Second path: start at any square on 1st trail with "light grey" neighbours -----------------------------
    # not None so OK to cast to Square
    bOK = False
    while not bOK:  
        #cleanup(2)# CLEAN UP PINK SQUARES: ADD HERE 02/12
        sq2 = chooseT2Start(damps, sqTarget)
        print("sq2 : " + str((sq2.row, sq2.col)))
        p.reset(sq2, 2) # move Probe before looping
        print("---------------------------------------------------------------------")
        print ("Trail 2 begin: " + str((sq2.row, sq2.col)) + "; ", end="")
        bOK = trailMake(sq2, p, 2)
        if bOK:
            p.removeTrailFences()
            p.updateTrailSquares(2)
            #if len(p.path) > 0:
             #   print ("Second trail created.")
    if retries > 1:
        print("Retries @ trail 2:" + str(retries))

    ngh = sq2.t1Neighbour()
    if ngh is not None:
        Square.setFenceBetween(sq2, ngh, False)
    print ("Path length: " + str(len(p.path)))
    nPink = pinkCount()
    if nPink > len(p.path):
        print ("PINK COUNT!:" + str(nPink))
    return bOK

def makeTarget1and2() -> None:
    '''makeTarget1and2(): fills all 4 Target squares with trail value 1 or 2 according to "neighbour" rule
        parameters: none
        returns: None
    '''
    sq1 = sqTarget # TEMP: to make them Square objects only
    sq2 = sqTarget
    ngh: List[Square] = []
    for y in range(0, 2):
        for x in range(0,2):
            sq = mz[sqTarget.row + y][sqTarget.col + x]
            if sq.getTrailNo() == 1:
                sq1 = sq
            if sq.getTrailNo() == 2:
                sq2 =sq
            if sq.getTrailNo() == 0:
                ngh.append(sq)
    #assert len(ngh) == 2, "Two white squares in target"
    lNgh = len(ngh)
    print ("target white squares count: " + str(lNgh))
    for z in range(0, lNgh):
        if Square.areNeigh(sq1, ngh[z]):
            ngh[z].setTrailNo(1)
        else:
            ngh[z].setTrailNo(2)

# Culdesac and mopup section--------------------------------------------------------------------

def addCulDeSacs() -> None:
    '''addCulDeSacs(): code to add culdesacs trails until algorithm becomes inefficient
        parameters:none
        returns: None
    '''
    listA: List[Square] = twoTrailSquares(1, 2) # list of Squares in either trail1 or trail 2
    listB: List[Square] = []

    #dryAll()

    bCntnu = True
    while bCntnu:
        #First, find a yellow square with at least one white neighbour 
        for sq in listA:
            if (sq.whiteCount() > 0) and not sq.target:
                listB.append(sq)
    
        lng = len(listB)
        if lng < 4:
            bCntnu = False
        else:
            r = random.randint(0, lng - 1)
            sqi = listB[r]

            # Now make cds trail
            p.reset(sqi, 3)
            p.removeTrail()
            count = 0
            while not p.culdesac:
                cdsTrailMake(sqi, p, 3)
                Square.setFenceBetween(sqi, p.path[0], False)
                p.removeTrailFences()
                count += 1
            listA = twoTrailSquares(1, 2)
            listB.clear()

def mopup() -> None:
    '''mopup(): more efficient algorithm to add the final few (short) culdesac trails
        parameters: none
        returns: None (it will do the job!)
    '''
    wList = twoTrailSquares(0, 0)
    lng = len(wList)
    for i in range(0, lng):
        if not wList[i].isTarget():
            wList[i].tryYellow()
    
#def cleanupTargetQuad(sqT: Square) -> None:
 #   '''cleanupTargetQuad(): '''
  #  yT = sqT.row
   # xT = sqT.col
    #sq = mz[yT][xT]    
#    cuTQ(sq, 2, 1)
 #   cuTQ(sq, 4, 2)
  #  cuTM(sq, 6)
   # sq = mz[yT + 1][xT]
    #cuTQ(sq, 2, 1)
#    cuTQ(sq, 1, 0)
 #   cuTM(sq, 3)
  #  sq = mz[yT][xT + 1]
   # cuTQ(sq, 8, 3)
    #cuTQ(sq, 4, 2)
#    cuTM(sq, 12)
 #   sq = mz[yT + 1][xT + 1]
  #  cuTQ(sq, 8, 3)
   # cuTQ(sq, 4, 2)
    #cuTM(sq, 9)

#def cuTQ(sq: Square, flg:int, dirn: int) -> None: # restore outer wall
 #   if (sq.code & flg) == 0: # no fence
  #      ngh = sq.getNeighbour(dirn)
   #     if ngh is not None:
    #        if ngh.trailNo > 2:
     #           Square.setFenceBetween(sq, ngh, True)   #put in fence

#def cuTM(sq: Square, flag: int) -> None: # clean up target middle
 #   sq.code = sq.code & flag


# Helper and support methods----------------------------------------------------

def isSoggy() -> bool:
    '''isSoggy() Checks if trail 1 contains more than minDamp number of squares with at least one "wet" neighbour
        parameters: none
        returns: bool: True if enough such squares, otherwise False
    '''
    global p
    damp = p.getDampTrail()
    nDamp = len(damp)
    bSoggy = nDamp >= minDamp
    return bSoggy

def chooseT2Start(damps: List[Square], tgt: Square) -> Square:
    '''chooseT2Start(): makes a random choie of Square on trail 1 with at least one "wet" neighbour
        parameters:
            damps: List[Square]: list of qualifying sqaures
            tgt: target Square (starting square must not be too close)
        returns: Square: chosen starting square for trail 2
    '''
    global p
    nDamp = len(damps)
    assert nDamp > 0, "no damp!"
    count = 0
    bOK = False
    while not bOK and (count < 3):
        count += 1
        if nDamp > 3:
            r = random.randint(0, nDamp - 3)
        else:
            r = random.randint(0, nDamp - 1)
        sq2 = damps[r]   # start square for trail 2
        bOK = not tooClose(sq2, tgt)
        #print("!", end="") # TEMP!!
    return sq2

def tooClose(sqA: Square, sqB: Square) -> bool:
    '''tooClose(): returns whether 2 squares are "too close" to each other, using algorithm internal to this method
        parameters:
            sqA: Square: first square to compare for "closeness"
            sqB: Square: second square to compare
        returns: bool: True if too close, else False
    '''
    yd = abs(sqA.row - sqB.row)
    xd = abs(sqA.col - sqB.col)
    return (xd + yd) < 5
    
def twoTrailSquares(trNoA: int, trNoB: int) -> List[Square]:
    '''twoTrailSquares(): returns a list of squares with either of 2 trail numbers
        parameters:
            trNoA: int: index number of first trail
            trNoB: int: index number of second trail
        returns: List[Square]: list of squares in either of 2 trails
    '''
    global ht, wid
    whites = []
    for y in range(0, ht):
        for x in range(0, wid):
            sq = mz[y][x]
            if ((sq.trailNo == trNoA) or (sq.trailNo == trNoB)):# and not isTargetNeighbour(sq):
                whites.append(sq)
    return whites

def scoreChecker() -> bool: # checks codes on both sides of the fence are consistent
    '''scoreChecker(): scans whole maze and checks that the presence or absence of the single fence between them is consistently coded in both squares (failsafe check)
        parameters: none
        returns: bool: True if whole maze is consistently coded, otherwise False
    '''
    global ht, wid
    for y in range(1, ht):
        for x in range(1, wid):
            c1 = mz[y][x].code
            b1 = (c1 & 2) != 0
            c2 = mz[y][x - 1].code
            b2 = (c2 & 8) != 0
            assert b1 == b2, "L<>R"
            c2 = mz[y - 1][x].code
            b1 = (c1 & 4) != 0
            b2 = (c2 & 1) != 0
            assert b1 == b2, "U<>D"

    return  True# TEMP

def trailCount(trNo: int) -> int:
    '''trailCount() counts the length (number of Squares) of a trail
        parameter: trNo: int: number of trail to check
        returns: int: trail length
    '''
    global ht, wid
    count = 0
    for y in range(0, ht):
        for x in range(0, wid):
            if mz[y][x].getTrailNo() == trNo:
                count += 1
                #print((y, x), end="")
    return count       

def whiteCount() -> int:    # wrapper
    return trailCount(0)

def pinkCount() -> int: # wrapper
    return trailCount(2)       

def dryAll() -> None:
    '''dryAll(): code to reset all Squares' "wet" attribute to False
    parameters: none
    returns: None
    '''
    global ht, wid
    for y in range(0, ht):
        for x in range(0, wid):
            mz[y][x].wet = False

#def fencesToFile() -> None:
 #   chars = " |_L"
  #  fName = "Fence" + str(mazeDims) + "_" + str(random.randint(1000, 9999)) + ".txt"
   # f = open(fName, "wt")
    #for y in range(mazeDims, -1, -1):
     #   row = ""
      #  for x in range(0, mazeDims + 1):
       #     sq = mz[y][x]
        #    val = 0
         #   if sq.vFence:
          #      val += 1
           # if sq.hFence:
            #    val += 2
       #     c = chars[val]
        #    row += c
        #print (row, file=f)
    #f.close()


############# MAIN PROGRAM STARTS HERE ###################################################################
startup()
b = True
while b:
    try:
        t1TrailMake(sqTarget, p)
        t2TrailMake(p.damp , p)
        b = False
    except MMException as ex:
        pass
    except Exception as other:
        raise other

makeTarget1and2()
# Now fill in the other squares with "culdesac" trails
maxWhiteCount = int(ht * wid / 20)
print("-------------------------------------------------------------------------")
print ("White pre culdesacs: " + str(whiteCount()) + "; ", end="")
addCulDeSacs()
print ("White pre mop-up: " + str(whiteCount()) + "; ", end="")

# Use a different technique to mop up remaining white squares

while whiteCount() > 0:
    mopup()
print ("mopped up!")
scoreChecker() # to check that scores are consistent for one fence from both sides
print()
print("=========================================================================")
print()
numFencesRaw = vu.drawMM(mz) # MazeMaker (left side) maze
numFencesInner = int(numFencesRaw / 2 - wid - ht) # NB: numFencesRaw is n even number!
numFencesOuter = (wid + ht) * 2
vu.show(numFencesInner, numFencesOuter)
