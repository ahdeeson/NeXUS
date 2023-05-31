"""
Thorlabs Motor class

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
import matplotlib.pyplot as plt
from pylablib.devices import Thorlabs

class ThorMotor():
    
    def __init__(self,init=True,Autoconnect=True):
        self.Type='Thorlabs'
        self.scale=1
        # self.ishomed=False
        self.motorlist=[]
        self.home_position=0
        if init:
            self.search(useFirst=Autoconnect)
            if Autoconnect:
                self.get_velocity()
        
    def search(self,useFirst=True):
        """create a list of available motors"""
        self.motorlist=Thorlabs.list_kinesis_devices()
        if useFirst:
            self.connect()
    
    def connect(self,MotorNumber=0,SN=None,Linear=True,SetFast=True):
        """connect to a motor from the motor list"""
        if MotorNumber >= len(self.motorlist) and SN==None:
            print("specified motor is absent")
            #raise error
        else:
            if int(SN) == 27261762:
                scale="Z812"
                self.units='mm'
                self.scale=10**3
            else:
                scale='PRM1-Z8'
                self.units='deg'
                self.scale = 1
                
            if SN==None:
                self.motor=Thorlabs.KinesisMotor(self.motorlist[MotorNumber][0],scale=scale)
                self.SN=int(self.motorlist[MotorNumber][0])
            else:
                self.motor=Thorlabs.KinesisMotor(SN,scale=scale)
                self.SN=int(SN)
            if SetFast:
                self.set_velocity(Vmin=0, Vmax=3, Accel=3)
            self.get_velocity()
            
    def moveA(self,X, WaitToMove=True):
        """move to position X"""
        self.motor.move_to(X/self.scale)
        
    def moveR(self,dx, WaitToMove=True):
        """move relative"""
        self.motor.move_by(dx/self.scale)
    
    def move_home(self, WaitToMove=True):
        """move to the home position"""
        #self.motor.move_home()
        self.moveA(self.home_position)
        
    def home(self):
        """home the motor (move to the end switch and set it as the home position)"""
        print("homer")
        self.motor.home()
        # self.ishomed=True
        
    def set_home(self,home):
        """set home position"""
        self.home_position=home#*self.scale

    def setSpeed(self, velocity=100):
        self.set_velocity(0, velocity, velocity)
        
    def set_velocity(self,Vmin,Vmax,Accel):
        """set velocity parameters
        minimum velocity, maximum velocity, acceleration"""
        self.motor.setup_velocity(Vmin/self.scale , Accel/self.scale , Vmax/self.scale)
        self.min_velocity=Vmin
        self.max_velocity=Vmax
        self.acceleration=Accel
        
    def get_velocity(self):
        """returns velocity parameters
        (minimum velocity, acceleration, maximum velocity)"""
        self.velocity=tuple(self.motor.get_velocity_parameters())
        self.min_velocity=self.velocity[0]*self.scale
        self.max_velocity=self.velocity[2]*self.scale
        self.acceleration=self.velocity[1]*self.scale
        
    def ismoving(self):
        """check if the motor is moving"""
        return self.motor.is_moving
    
    def stop(self):
        self.motor.stop()
        
    def disconnect(self):
        """disconnect the motor and the port"""
        self.motor.close()
    
    @property
    def position(self):
        return self.motor.get_position()*self.scale
     
    @property
    def is_moving(self):
        return self.motor.is_moving()
    
    @property
    def is_homed(self):
        return self.motor.is_homed()

# M=ThorMotor()




# import thorlabs_apt as apt

# class ThorMotor():
    
#     def __init__(self,init=True,Autoconnect=True):
#         self.Type='Thorlabs'
#         self.ishomed=False
#         self.motorlist=[]
#         if init:
#             self.search(useFirst=Autoconnect)
#             if Autoconnect:
#                 self.get_velocity()
        
#     def search(self,useFirst=True):
#         """create a list of available motors"""
#         self.motorlist=apt.list_available_devices()
#         if useFirst:
#             self.connect()
    
#     def connect(self,MotorNumber=0,SN=None):
#         """connect to a motor from the motor list"""
#         if MotorNumber > len(self.motorlist) and SN==None:
#             pass
#             #raise error
#         else:
#             if SN==None:
#                 self.motor=apt.Motor(self.motorlist[MotorNumber][1])
#             else:
#                 self.motor=apt.Motor(SN)
            
#     def moveA(self,X):
#         """move to position X"""
#         self.motor.move_to(X)
        
#     def moveR(self,dx):
#         """move relative"""
#         self.motor.move_by(dx)
    
#     def move_home(self):
#         """move to the home position"""
#         self.motor.move_home()
        
#     def home(self):
#         """home the motor (move to the end switch and set it as the home position)"""
#         self.motor.move_home(blocking = True)
#         self.ishomed=True
        
#     def set_velocity(self,Vmin,Vmax,Accel):
#         """set velocity parameters
#         minimum velocity, maximum velocity, acceleration"""
#         self.motor.set_velocity_parameters(Vmin,Accel,Vmax)
        
#     def get_velocity(self):
#         """returns velocity parameters
#         (minimum velocity, acceleration, maximum velocity)"""
#         self.velocity=self.motor.get_velocity_parameters()
        
#     def ismoving(self):
#         """check if the motor is moving"""
#         return self.motor.is_in_motion
    
#     @property
#     def position(self):
#         return self.motor.position
        

# M=ThorMotor()
        