"""
drilling controll class

@author: Slawa
"""

import os
import sys
Path=os.path.dirname((os.path.abspath(__file__)))
sys.path.append(Path)
SP=Path.split("\\")
i=0
while i<len(SP) and SP[i].find('python')<0:
    i+=1
import sys
Pypath='\\'.join(SP[:i+1])
sys.path.append(Pypath)

import time  
import numpy as np
import matplotlib.pyplot as plt
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtTest
import drill_Qt
from Hardware.Motors.multi_motor import MultiMotor
import gc

class drill(QtWidgets.QMainWindow, drill_Qt.Ui_MotorScan):
    def __init__(self):
        self.app=QtWidgets.QApplication(sys.argv)
        super().__init__()
        self.setupUi(self)
        
        self.MM=MultiMotor()
        
        #main functions
        self.connect.clicked.connect(self.fconnect)
        self.home.clicked.connect(self.fhome)
        self.moveL1.clicked.connect(self.fmoveL1)
        self.moveR1.clicked.connect(self.fmoveR1)
        self.moveL2.clicked.connect(self.fmoveL2)
        self.moveR2.clicked.connect(self.fmoveR2)
        self.StartScan.clicked.connect(self.fStartScan)
        self.StopScan.clicked.connect(self.fStopScan)
        
    def fconnect(self):
        """connect motors"""
        self.MM.connect_next_motor()
        self.MM.connect_next_motor()
        
        #show info
        self.MotorChoice1.addItems([self.MM.motors[0].SN])
        self.MotorChoice2.addItems([self.MM.motors[1].SN])
        self.show_position()
    
    def show_position(self):
        """show positions of the motors"""
        position=self.MM.position()
        self.pos1.setValue(position[0])
        self.pos2.setValue(position[1])
    
    def fhome(self):
        """home motors"""
        self.MM.home_all()
        
    def moveR(self,dx):
        """move relative"""
        self.MM.moveR(dx)
        self.show_position()
        
    def moveA(self,dx):
        """move relative"""
        self.MM.moveA(dx)
        self.show_position()
    
    def fmoveL1(self):
        """move motor 1"""
        step=self.step1.value()
        self.moveR([-step,0])
    
    def fmoveR1(self):
        """move motor 1"""
        step=self.step1.value()
        self.moveR([step,0])
    
    def fmoveL2(self):
        """move motor 2"""
        step=self.step2.value()
        self.moveR([0,-step])
    
    def fmoveR2(self):
        """move motor 2"""
        step=self.step2.value()
        self.moveR([0,step])
    
    def fStartScan(self):
        """start scanning"""
        #init parameters
        self.Stop=False
        self.Sr=0
        self.Nr=self.NumRIters.value()
        self.St=0
        self.Nt=self.NumIters.value()
        self.dt=self.TimeStep.value()
        dt=self.dt
        self.R=self.radius.value()
        self.ZeroPos=self.MM.position()
        ZeroPos=self.ZeroPos
        
        self.MM.set_pattern(R=self.R,Nsteps=self.Nr)
        self.pattern=self.MM.pattern
        self.NumRIters.setValue(int(len(self.pattern)))
        
        #moving
        while self.St < self.Nt and not self.Stop:
            while self.Sr < len(self.pattern) and not self.Stop:
                QtTest.QTest.qWait(int(dt*1000))
                self.moveA(ZeroPos+self.pattern[self.Sr])
                self.Sr+=1
                self.PosShow()
            self.St+=1
            self.Sr=0
        self.moveA(ZeroPos)
        
    def fStopScan(self):
        self.Stop=True
        
    def PosShow(self):
        pos=self.pattern[:self.Sr+1]
        X=pos[:,0]
        Y=pos[:,1]
        # Ntick=7 #number of ticks
        
        View=self.PosView
        scene = QtWidgets.QGraphicsScene(self)
        pw=pg.PlotWidget(labels={'left': 'Y mm', 'bottom': 'X mm'})
        pw.resize(View.size()*0.99)
        p1=pw.plotItem
        p1.plot(X,Y,symbol='o')
        
        scene.addWidget(pw)
        View.setScene(scene)
        
        
        
        # p1=pw.plotItem
        # p1.scatter(X,Y)
    
    
def main():
    pg.setConfigOption('background', 'w')
    window = drill()
    window.show()
    window.app.exec_()

if __name__ == '__main__':
    main()
    gc.collect()
    
    
    