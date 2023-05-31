"""
multi-motor controll class

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
import numpy as np
Pi=np.pi
import matplotlib.pyplot as plt
import copy
import time 

from Hardware.Motors.Motor_class import Motor

class MultiMotor():
    def __init__(self,Type=None):
        self.M0=Motor()
        self.motors=[]
        self.pattern=[]
        self.Stop=False
        self.Nmotors=len(self.M0.motorlist)
        self.Nm=0
    
    def connect_motor(self,MotorNumber=0):
        """add one motor"""
        self.motors+=[copy.deepcopy(self.M0)]
        self.motors[-1].connect(MotorNumber)
        
    def connect_next_motor(self):
        """add next motor"""
        if self.Nm < self.Nmotors:
            self.connect_motor(self.Nm)
            self.Nm+=1
        else:
            print("no more motors")
            #add raise
        
    def moveR(self,dX):
        """move all motors by dX; it is a vector that must hav esame length as the number of motors
        0 is no movement"""
        if len(dX)==len(self.motors):
            for i in range(len(dX)):
                x=dX[i]
                if x!=0:
                    self.motors[i].moveR(x)
        else:
            print('wrong length of the move vector')
            #add raise
            
    def moveA(self,X):
        """move all motors by dX; it is a vector that must hav esame length as the number of motors
        0 is no movement"""
        if len(X)==len(self.motors):
            for i in range(len(X)):
                x=X[i]
                if x!=0:
                    self.motors[i].moveA(x)
        else:
            print('wrong length of the move vector')
            #add raise
            
    def home_all(self):
        """home all motors"""
        for m in self.motors:
            m.home()
            
    def position(self):
        """return current posisions"""
        if len(self.motors)>0:
            return [m.position for m in self.motors]
        else:
            print("no motors")
            
    def set_pattern(self,Type='circle',R=0.5,Nsteps=100):
        """define the pattern to move the motors
        R - radius of a circule in mm
        Nsteps is the number of steps in the pattern"""
        if Type == 'circle':
            """move in a spiral shape to fill curcile"""
            positions=[[0,0]]
            
            #find step size for homogenious filling
            Scircule=Pi*R**2
            Sstep=Scircule/Nsteps
            Rstep=2*(Sstep/Pi)**0.5
            
            #make the list of positions
            Nr=int(np.round(R/Rstep))
            for n in range(Nr):
                n+=1
                Rn=n*Rstep
                if Rn > R:
                    Rn=R
                # print(Rn)
                Nphi=int(np.round(2*Pi*Rn/Rstep))
                positions+=[[Rn*np.cos(2*Pi/Nphi*nphi),Rn*np.sin(2*Pi/Nphi*nphi)] for nphi in range(Nphi)]
            self.pattern=np.array(positions)
            # print(len(self.pattern))
        else:
            print('unknown Type')
            #add raise
            
    def move_pattern(self, ZeroPos=[], dt=0.1, Nrepeats=1):
        """move according to the pattern
        ZeroPos : position corresponding to the zero in the pattern. if [], takes the current position as zero
        dt : time interval between steps
        Nrepeats: number of repeated movements according to the same pattern"""
        if len(self.motors)>=len(self.pattern[0]):
            if ZeroPos==[]:
                ZeroPos=self.position()
            Nr=0
            Nstep=0
            while Nr < Nrepeats and not self.Stop:
                while Nstep < len(self.pattern) and not self.Stop:
                    time.sleep(dt)
                    self.moveA_motors(ZeroPos+self.pattern[Nstep])
                    Nstep+=1
                Nr+=1
                Nstep=1
            self.moveA_motors(ZeroPos)
        else:
            print("not enough motors for the given pattern")
            #add raise
    
    def Stop(self):
        self.Stop=True
    
    
    
# MM=MultiMotor()
# MM.connect_next_motor()
# MM.connect_next_motor()
    
    
    
    
    
    
    
    
    
    
    
    