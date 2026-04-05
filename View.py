#******************************************************************************************
#
# View.py: controlling code for displaying mazes using matplotlib library
# 
# Version 0.1
# Last updated 02.04.2026 22:55
# 07
#  
# *****************************************************************************************
from matplotlib import pyplot as plt, patches as pat, lines, artist
import os
from typing import List
from Square import Square
from datetime import datetime

class View:
    #class variables

    def __init__(self, ht: int, wid: int, sqSz: int):
        self.ht = ht
        self.wid = wid
        self.sqSz = sqSz
        self.fig, self.axs = plt.subplots(ncols=1, nrows=1, figsize=(7, 7), facecolor="powderblue", layout="constrained")
        self.fig.suptitle("MazeMaker Mazes")
        self.axMM = self.axs # MazeMaker axis
        self.displayDims =  str(ht) + "x" + str(wid)

    def show(self, iFences: int, oFences: int) -> None:
        '''show(): displays maze and saves picture file (.png) in Pix subfolder)
        parameters:
            self: this View object
            iFences: int: number of inner fences
            oFences: number of outer fences
        returns: None
        '''
        self.axMM.set_title("Maze size: " + self.displayDims + "; " + datetime.now().strftime("%Y-%m-%d %H:%M") + "; F Panels: " + str(iFences) + "(I) + " + str(oFences) + "(O)")
        plt.sca(self.axMM)
        plt.axis("off")
        plt.axis("scaled")
        fName = "MZ" + datetime.now().strftime("%y%m%d%H%M%S") + ".png"
        os.chdir("Pix")
        plt.savefig(fName)
        os.chdir("..") # change it back
        plt.show()

    def drawMM(self, mz: List[List[Square]]) -> int:
        '''drawMM(): draws the maze using matplotlib
        parameters:
            self: this View object
            mz: List[List[Square]]: matrix of Square objects
        returns: int: count of fences (before correction: double-counts all internal fences!)
        '''
        plt.sca(self.axMM)
        count = 0
        for y in range(self.ht):
            for x in range(self.wid):
                count += mz[y][x].drawMeMaker(self.axMM)
        return count
    
    

