#******************************************************************************************
#
# View.py: controlling code for displaying mazes using matplotlib library
# 
# Version 0.3
# Last updated 07.12.2025 15:39
#  
# *****************************************************************************************
from matplotlib import pyplot as plt, patches, lines
import matplotlib.animation
from typing import cast, List
from Square import Square
from Maisie import Maisie
from MSquare import MSquare

class View:
    #class variables

    def __init__(self, mazeDims: int, sqSz: int):
        self.mazeDims = mazeDims
        self.sqSz = sqSz
        self.fig, self.axs = plt.subplots(ncols=2, nrows=1, figsize=(10, 6), facecolor="powderblue", layout="constrained")
        self.fig.suptitle("MazeMaker Mazes")
        self.axMM = self.axs[0] # MazeMaker axis
        self.axMM.set_title("Maker")
        self.axMais = self.axs[1] #Maisie axis
        self.axMais.set_title("Maisie")
        #self.maisie = None

    def show(self):
        plt.sca(self.axMM)
        plt.axis("scaled")
        plt.axis("off")
        plt.sca(self.axMais)
        plt.axis("scaled")
        plt.axis("off")
        plt.show()

    def drawMM(self, mz: List[List[Square]]):
        plt.sca(self.axMM)
        for y in range(self.mazeDims):
            for x in range(self.mazeDims):
                mz[y][x].drawMe()
        #self.show()
    
    #def getMaisie(self, m: Maisie) -> bool:
      #  self.maisie = m
     #   if m is not None:
       #     self.maisie = cast(Maisie, m)
        #return (m is not None)
    
    def drawEmptyMais(self) -> None:
        plt.sca(self.axMais)
        lth = self.mazeDims * self.sqSz
        rect = patches.Rectangle((0, 0), lth, lth, color="white", ec="black")
        self.axMais.add_patch(rect)
        for y in range(1, self.mazeDims):
            line = lines.Line2D((0, self.mazeDims * self.sqSz), (y * self.sqSz, y * self.sqSz), color="powderblue")
            self.axMais.add_line(line)
        for x in range(1, self.mazeDims):   
            line = lines.Line2D((x * self.sqSz, x * self.sqSz), (0, self.mazeDims * self.sqSz), color="powderblue")
            self.axMais.add_line(line)
    
    def drawMaiSq(self, sq: MSquare, ownsMaisie: bool) -> None: #NB: this is ANY square in Maisie maze, NOT just where Maisie is!
        #ax = plt.gca()
        c = "white"
        if ownsMaisie:
            c = "orchid"
        if sq.visited:
            c = "powderblue"
        rect = patches.Rectangle((sq.col * MSquare.sq_sz, sq.row * MSquare.sq_sz), MSquare.sq_sz, MSquare.sq_sz, color=c)
        self.axMais.add_patch(rect)
        self.drawMaiFences(sq)

    def drawMaiFences(self, sq: MSquare) -> None:
        if sq.code & 2 != 0: #W
            self.drawLine(sq.col, sq.row, True)
        if sq.code & 4  != 0: #S
            self.drawLine(sq.col, sq.row, False)
        if sq.row == self.mazeDims - 1:
            if sq.code & 1 != 0: #N
                self.drawLine(sq.col, sq.row + 1, False)
        if sq.col == self.mazeDims - 1:
            if sq.code & 8 != 0: #E
                self.drawLine(sq.col + 1, sq.row, True)

    def drawLine(self, c:int, r: int, vert: bool) -> None:
        xx = c * self.sqSz
        yy = r * self.sqSz
        clr = "black"
        #ax = plt.gca()
        if vert:
            line = lines.Line2D((xx, xx), (yy, yy + MSquare.sq_sz), color=clr)
        else:
            line = lines.Line2D((xx, xx + MSquare.sq_sz), (yy, yy), color=clr)
        self.axMais.add_line(line)

