"""
Pololu tic stepper motor class

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
import pytic
config=Path+'\\pololuT834_config.yml'

class TicMotor():
    
    def __init__(self,init=True,Autoconnect=True):
        self.Type='Tic'
        self.scale=1
        # self.ishomed=False
        self.motorlist=[]
        if init:
            self.search(useFirst=Autoconnect)
            if Autoconnect:
                self.get_velocity()
        
    def search(self,useFirst=True):
        """create a list of available motors"""
        tic = pytic.PyTic()
        self.motor=tic
        self.motorlist=tic.list_connected_device_serial_numbers()
        if useFirst:
            self.connect()
    
    def connect(self,MotorNumber=0,SN=None,Config=config):
        """connect to a motor from the motor list"""
        if MotorNumber >= len(self.motorlist) and SN==None:
            print("specified motor is absent")
            #raise error
        else:
            if SN==None:
                self.motor.connect_to_serial_number(self.motorlist[MotorNumber])
                self.SN=self.motorlist[MotorNumber]
            else:
                self.motor.connect_to_serial_number(SN)
                self.SN=SN
            self.motor.settings.load_config(Config)
            self.motor.settings.apply() 
            #self.motor.halt_and_set_position(0)
            self.motor.energize()
            self.motor.exit_safe_start()
            
    def moveA(self,X):
        """move to position X"""
        self.motor.set_target_position(int(X/self.scale)) #must be int = number of steps
        
    def moveR(self,dx):
        """move relative"""
        pos=self.position
        self.motor.set_target_position(int((pos+dx)/self.scale)) #must be int = number of steps
    
    def move_home(self):
        """move to the home position"""
        self.motor.set_target_position(0)
        
    def home(self):
        """home the motor (move to the end switch and set it as the home position)"""
        self.motor.halt_and_set_position(0)
        self.ishomed=True
        
    def set_velocity(self,Vmin,Vmax,Accel):
        """set velocity parameters
        minimum velocity, maximum velocity, acceleration"""
        pass
        
    def get_velocity(self):
        """returns velocity parameters
        (minimum velocity, acceleration, maximum velocity)"""
        pass
        
    def ismoving(self):
        """check if the motor is moving"""
        pass
    
    def stop(self):
        pass
        
    def power_off(self):
        self.motor.enter_safe_start()
        self.motor.deenergize()
    
    @property
    def position(self):
        return self.motor.variables.current_position*self.scale
     
    @property
    def is_moving(self):
        pass
    
    @property
    def is_homed(self):
        return self.ishomed

# M=TicMotor()
