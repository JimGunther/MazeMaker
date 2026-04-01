#******************************************************************************************
#
# View.py: controlling code for displaying mazes using matplotlib library
# 
# Version 0.1
# Last updated 31.03.2026 15:07
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
        self.axMM = self.axs#[0] # MazeMaker axis
        self.displayDims =  str(ht) + "x" + str(wid)

    def show(self):
        tit = self.axMM.get_title()
        self.axMM.set_title(self.displayDims + " " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        plt.sca(self.axMM)
        plt.axis("off")
        plt.axis("scaled")
        fName = "MZ" + datetime.now().strftime("%y%m%d%H%M%S") + ".png"
        os.chdir("Pix")
        plt.savefig(fName)
        os.chdir("..") # change it back
        plt.show()

    def drawMM(self, mz: List[List[Square]]):
        plt.sca(self.axMM)
        for y in range(self.ht):
            for x in range(self.wid):
                mz[y][x].drawMeMaker(self.axMM)
    
    

