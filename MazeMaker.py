#******************************************************************************************
#
# MazeMaker.py: controlling code for maze maker
# 
# Version 0.94
# Last updated 15.12.2025 10:36
#  
# *****************************************************************************************

from matplotlib import pyplot as plt
import matplotlib.animation as anim
from typing import cast, List
import random
from datetime import datetime
#import time
import sys
from Square import Square, MMException
from Probe import Probe
from Maisie import Maisie
from View import View

print()
mazeDims = 0
ctnu = True
while ctnu:
    try:
        mazeDims = int(input("\nSize of maze (NxN)"))
        ctnu = False
    except ValueError:
        print("Number unrecognised: try again!")

sqSize = 10
startCol = 0
startRow = 0
endCol = 0
endRow = 0
retries = 0
mz = [[Square(r, c) for c in range(0, mazeDims)] for r in range(mazeDims)]
sqStart = mz[0][0] # to make sqStart a Square object
sqTarget = mz[0][0] # to make sqTarget a Square object
p = Probe(sqStart, 0)
vu = View(mazeDims, sqSize)

# -----------------------------------------------------------------------------------------------------
def startup() -> None:
    # Code which only needs to run once
    global minDamp
    global mazeDims
    global mz

    minDamp = mazeDims / 2 + 1
    Square.setup(mazeDims)
    dt = datetime.timestamp(datetime.now())
    random.seed(dt) # seed randomizer

    #set up neighbours: row and column 0 already set to None
    for y in range(0, mazeDims):
        for x in range(0, mazeDims):
            if x > 0:
                mz[y][x].setNeighbour(1, mz[y][x-1])
                mz[y][x-1].setNeighbour(3, mz[y][x])
            if y > 0:
                mz[y][x].setNeighbour(2, mz[y-1][x])
                mz[y-1][x].setNeighbour(0, mz[y][x])

def prepare(prevTgt: Square, trNo: int) -> tuple[Square, Square]:    # use only for trNo == 1 or 2 
    # (1) Initial creation of maze----------------------------------------------------------------------------
    global mazeDims
    global retries
    global sqTarget
    global startCol
    
    # Clean up first
    for y in range(0, mazeDims):
        for x in range(0, mazeDims):
            sq = mz[y][x]
            sq.code = 15
            sq.setTrailNo(0)
            sq.wet = False
            sq.damp = False
            sq.target = False
    setupTargetQuad(prevTgt, False)
    
    # further initialization for trail 1 only------------------------------------------------------------------
    if (trNo == 1):
        startCol = random.randint(0, mazeDims - 1)
        Square.startCol = startCol
        startRow = 0
        i = int(mazeDims / 2)
        targetCol = random.randint(i, mazeDims - 2)
        targetRow = random.randint(i, mazeDims - 2)
        print ("Start square: " + str((startRow, startCol)) + "; ", end="")
        
        # NB: the following are set up in the Square __init__() method: trailNo => 0, code to 15
        
        sqStart = mz[startRow][startCol]
        sqStart.setTrailNo(1)
        sqTarget = mz[targetRow][targetCol]
        print("Target square: " + str((targetRow, targetCol)))
        setupTargetQuad(sqTarget, True)
    
    retries = 0

    # Assign "attraction" votes--------------------------------------------------
    for y in range(0, mazeDims):
        for x in range(0, mazeDims):
            mz[y][x].calcVotes(targetRow, targetCol)
        
    return (sqStart, sqTarget)
# END METHOD prepare()------------------------------------------------------------------------------------

def setupTargetQuad(sqTgt: Square, tf: bool) -> None:
    # set all 4 target flags and delete fences between them (tf == True) else reverse the changes

    #print("Target quad setup:" + str((sqTgt.row, sqTgt.col)) + " " + str(tf))
    targetRow = sqTgt.row
    targetCol = sqTgt.col
    for i in range(0,2):
        for j in range(0,2):
            mz[targetRow + i][targetCol + j].setTarget(tf)
            mz[targetRow][targetRow].setTrailNo(0)
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
    count = 0
    for y in range(0, mazeDims):
        for x in range(0, mazeDims):
            if mz[y][x].getTrailNo() == trNo: #????
                mz[y][x].setTrailNo(0)
                count += 1
    print (str(count) + " squares cleaned up.")

# innermost loop: makes trail to target OR culdesac
def trailMake(startSq: Square, p: Probe, trNo: int)-> bool: # True if at target
    global mazeDims
    global retries
    
    innerLoopCount = 0
    p.reset(startSq, trNo)
    cdsCount = 0
    #print("Yellow count: " + str(trailCount(1)))
    bStop = False

    while not bStop:
        innerLoopCount += 1
        sq = p.move(trNo, mazeDims)
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
            p.removeTrail(trNo)
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
    
def cdsTrailMake(startSq: Square, mazeDims: int, p: Probe, trNo: int)-> bool: 
    innerLoopCount = 0
    p.reset(startSq, trNo)
    while not p.culdesac: # loop until culdesac
        innerLoopCount += 1
        sq = p.move(trNo, mazeDims)
        if sq is not None:
            p.setSquare(sq, trNo)
        else:
            assert(p.culdesac)
    return p.culdesac

def t1TrailMake(prevTgt:Square, p: Probe) -> bool:   # keeps trying trail 1 until it's soggy enough
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
        #if mz[0][1].isWet() or mz[1][0].isWet():    # fix a "bug"?
        #    mz[0][0].wet = True
        bSoggy = isSoggy()
    nDamp = p.makeDamp()
    print ("Path length: " + str(len(p.path)))
    #print ("No. damps: " + str(nDamp))
    p.removeTrailFences()
    p.updateTrailSquares(1)
    return bSoggy

def t2TrailMake(damps: List[Square], p: Probe) -> bool:
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
    assert len(ngh) == 2, "Two white squares in target"
    if Square.areNeigh(sq1, ngh[0]):
        ngh[0].setTrailNo(1)
        ngh[1].setTrailNo(2)
    else:
        ngh[0].setTrailNo(2)
        ngh[1].setTrailNo(1)

# Culdesac and mopup section--------------------------------------------------------------------

def addCulDeSacs() -> None:
    listA: List[Square] = twoTrailSquares(1, 2)
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
            p.removeTrail(3)
            count = 0
            while not p.culdesac:
                cdsTrailMake(sqi, mazeDims, p, 3)
                Square.setFenceBetween(sqi, p.path[0], False)
                p.removeTrailFences()
                count += 1
            listA = twoTrailSquares(1, 2)
            listB.clear()

def mopup() -> None:
    wList = twoTrailSquares(0, 0)
    lng = len(wList)
    for i in range(0, lng):
        if not wList[i].isTarget():
            wList[i].tryYellow()
    
def cleanupTargetQuad(sqT: Square) -> None:
    yT = sqT.row
    xT = sqT.col
    sq = mz[yT][xT]    
    cuTQ(sq, 2, 1)
    cuTQ(sq, 4, 2)
    cuTM(sq, 6)
    sq = mz[yT + 1][xT]
    cuTQ(sq, 2, 1)
    cuTQ(sq, 1, 0)
    cuTM(sq, 3)
    sq = mz[yT][xT + 1]
    cuTQ(sq, 8, 3)
    cuTQ(sq, 4, 2)
    cuTM(sq, 12)
    sq = mz[yT + 1][xT + 1]
    cuTQ(sq, 8, 3)
    cuTQ(sq, 4, 2)
    cuTM(sq, 9)

def cuTQ(sq: Square, flg:int, dirn: int) -> None: # restore outer wall
    if (sq.code & flg) == 0: # no fence
        ngh = sq.getNeighbour(dirn)
        if ngh is not None:
            if ngh.trailNo > 2:
                Square.setFenceBetween(sq, ngh, True)   #put in fence

def cuTM(sq: Square, flag: int) -> None: # clean up target middle
    sq.code = sq.code & flag


# Helper and support methods----------------------------------------------------

def isSoggy() -> bool:
    # Get a list of squares on trail1 with at least one "wet" neighbour
    global p
    damp = p.getDampTrail()
    nDamp = len(damp)
#    print ("No. damp: " + str(nDamp))
    bSoggy = nDamp >= minDamp
    return bSoggy

def chooseT2Start(damps: List[Square], tgt: Square) -> Square:
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
    yd = abs(sqA.row - sqB.row)
    xd = abs(sqA.col - sqB.col)
    return (xd + yd) < 5
    
def twoTrailSquares(trNoA: int, trNoB) -> List[Square]:
    whites = []
    for y in range(0, mazeDims):
        for x in range(0, mazeDims):
            sq = mz[y][x]
            if ((sq.trailNo == trNoA) or (sq.trailNo == trNoB)):# and not isTargetNeighbour(sq):
                whites.append(sq)
    return whites

#def isTargetNeighbour(sq: Square) -> bool: # True if at least one neighbour is a green square
 #   bOK = True
  #  for i in range(4):
   #     ngh = sq.getNeighbour(i)
    #    if ngh is not None:
     #       if ngh.target:
      #          bOK = False
    #return bOK

def scoreChecker() -> bool: # checks codes on both sides of the fence are consistent
    for y in range(1, mazeDims):
        for x in range(1, mazeDims):
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
    count = 0
    for y in range(0, mazeDims):
        for x in range(0, mazeDims):
            if mz[y][x].getTrailNo() == trNo:
                count += 1
                #print((y, x), end="")
    return count       

def whiteCount() -> int:
    return trailCount(0)

def pinkCount() -> int:
    return trailCount(2)       

def mazeToMaisie(destMz: List[List[Square]]) -> None:
    for y in range(0, mazeDims):
        for x in range(0, mazeDims):
            destMz[y][x].code = mz[y][x].code
            #print(str(mz[y][x].code) + ";", end ="")
        #print()
    return

def dryAll() -> None:
    for y in range(0, mazeDims):
        for x in range(0, mazeDims):
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
        t2TrailMake(p.damp ,p)
        b = False
    except MMException as ex:
        pass
    except Exception as other:
        raise other

makeTarget1and2()
# Now fill in the other squares with "culdesac" trails
maxWhiteCount = int(mazeDims * mazeDims / 20)
print("-------------------------------------------------------------------------")
print ("White pre culdesacs: " + str(whiteCount()) + "; ", end="")
addCulDeSacs()
print ("White pre mop-up: " + str(whiteCount()) + "; ", end="")

# Use a different technique to mop up remaining white squares

while whiteCount() > 0:
    mopup()
print ("mopped up!")
scoreChecker()
print()
print("=========================================================================")
print()
vu.drawMM(mz) # MazeMaker (left side) maze
#fencesToFile()
#========================= Maisie Stuff!=============================================
mai = Maisie(mazeDims)
vu.drawEmptyMais(mai) # Maisie (right side) maze

mai.startup(startCol) #sets up neighbours and sets outer fences
mazeToMaisie(mai.rlMz) # xfers code values from original maze to Maisie's copy 
print ("Maisie initial pos: " + str((mai.row, mai.col)))
passNo = 1

plt.sca(vu.axMais)

mai.scan()
ssq = mai.mmz[mai.row][mai.col]
ssq.drawMeMaisie(vu.axMais, True)
ssq.numVisits += 1

mai.choose(True)
mai.drawMe(vu.axMais)
ani = anim.FuncAnimation(vu.fig, vu.vwUpdate1, frames=mai.gen1, interval=150, blit=True, repeat=False, cache_frame_data=False)
vu.show()
ani = None

#print("Start 2")