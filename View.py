#******************************************************************************************
#
# View.py: controlling code for displaying mazes using matplotlib library
# 
# Version 0.6
# Last updated 13.12.2025 16:29
#  
# *****************************************************************************************
from matplotlib import pyplot as plt, patches as pat, lines, artist
#import matplotlib.animation
from typing import cast, List
from Square import Square
from Maisie import Maisie

class View:
    #class variables

    def __init__(self, mazeDims: int, sqSz: int):
        self.mazeDims = mazeDims
        self.sqSz = sqSz
        self.fig, self.axs = plt.subplots(ncols=2, nrows=1, figsize=(11, 7), facecolor="powderblue", layout="constrained")
        self.fig.suptitle("MazeMaker Mazes")
        self.axMM = self.axs[0] # MazeMaker axis
        self.axMM.set_title("Maker")
        self.axMais = self.axs[1] #Maisie axis
        self.axMais.set_title("Maisie")
        self.maisie = None
        #self.patches: List[artist.Artist] = []
        #self.lines: List[artist.Artist] = []

    def show(self):
        plt.sca(self.axMM)
        plt.axis("off")
        plt.axis("scaled")
        plt.sca(self.axMais)
        plt.axis("off")
        plt.axis("scaled")
        plt.show()

    def show2(self):
        plt.sca(self.axMais)
        plt.axis("off")
        plt.axis("scaled")
        plt.show()

    def drawMM(self, mz: List[List[Square]]):
        plt.sca(self.axMM)
        for y in range(self.mazeDims):
            for x in range(self.mazeDims):
                mz[y][x].drawMeMaker(self.axMM)
    
    def drawEmptyMais(self, m: Maisie) -> None:
        self.maisie = m
        plt.sca(self.axMais)
        lth = self.mazeDims * self.sqSz
        rect = pat.Rectangle((0, 0), lth, lth, color="white", ec="black")
        self.axMais.add_patch(rect)
        for y in range(1, self.mazeDims):
            line = lines.Line2D((0, self.mazeDims * self.sqSz), (y * self.sqSz, y * self.sqSz), color="powderblue")
            self.axMais.add_line(line)
        for x in range(1, self.mazeDims):   
            line = lines.Line2D((x * self.sqSz, x * self.sqSz), (0, self.mazeDims * self.sqSz), color="powderblue")
            self.axMais.add_line(line)

    def addLine(self, c:int, r: int, vert: bool) -> None:
        xx = c * self.sqSz
        yy = r * self.sqSz
        clr = "black"
        if vert:
            line = lines.Line2D((xx, xx), (yy, yy + Square.sq_sz), color=clr)
        else:
            line = lines.Line2D((xx, xx + Square.sq_sz), (yy, yy), color=clr)
        self.axMais.add_line(line)

    def vwReset(self) -> None:
        #print ("View patches: " + str(len(self.axMais.patches)))
        #print ("View lines: " + str(len(self.axMais.lines)))
        #patch = self.patches.pop()
        #assert patch is pat.RegularPolygon, "Not Maisie!"
        #patch = self.patches.pop()
        #assert patch is pat.Rectangle, "Not a square!"
        pass

    def vwStart(self) -> list:
        return []

    def vwUpdate1(self, frm) -> list:
        assert self.maisie is not None
        self.maisie.go(self.axMais, True)
        return []
    
    def vwUpdate2(self, frm) -> list:
        assert self.maisie is not None
        self.maisie.leftFirst = True
        self.maisie.go(self.axMais, False)
        return []
