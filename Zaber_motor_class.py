"""
Zaber motor class

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
import zaber_motion
# from zaber_motion import Library
# from zaber_motion.ascii import Connection
# from zaber_motion import Units, MotionLibException
# from zaber_motion import Tools as Ztools

import serial.tools.list_ports as ports

zaber_motion.Library.enable_device_db_store()


class ZaberMotor():
    
    def __init__(self,COM=None,Autoconnect=True,init=True):
        """COM is the connection name e.g. COM3 """
        self.Type='Zaber'
        self.home_position=0
        self.units="mm" #at least for now for linear stages
        self.homed=False
        self.motorlist=[]
        self.connections=[]
        self.home_position=0
        if init:
            self.search(COM,useFirst=Autoconnect)
        
    def search(self,COM=None,useFirst=True):
        """create a list of available motors"""
        if not COM==None:
            connection= zaber_motion.ascii.Connection.open_serial_port(COM)
            self.connection=connection
            self.motorlist = connection.detect_devices()
            print("Found {} devices".format(len(self.motorlist)))
            
            if useFirst:
                self.connect()
        else:
            comlist=ports.comports()
            # print(comlist)
            for com in comlist:
                # print(com[0])
                if com[1][:3] == 'USB':
                    try:
                        connection= zaber_motion.ascii.Connection.open_serial_port(com[0])
                    except zaber_motion.MotionLibException as err:
                        print(err)
                    else:
                        # print(com[0])
                        self.connection = connection
                        self.connections += [connection]
                        self.motorlist += connection.detect_devices()
                        print("Found {} devices".format(len(self.motorlist)))
            if useFirst:
                self.connect()
    
    def connect(self,ZaberID=None,MotorNumber=0,axis=1,unpark=False):
        """connect to a motor from the motor list
        axis is needed when >1 motors are connected in a daisy chain"""
        if ZaberID == None:
            if MotorNumber >= len(self.motorlist):
                print("specified motor is absent")
                #raise error
            else:
                self.motor=self.motorlist[MotorNumber].get_axis(axis)
                if unpark:
                    self.motor.unpark()
        else:
            self.motor=ZaberID.get_axis(axis)
            if unpark:
                self.motor.unpark()
    
    def moveA(self,X):
        """move to position X in mm"""
        self.motor.move_absolute(X+self.home_position, zaber_motion.Units.LENGTH_MILLIMETRES)
        
    def moveR(self,dx):
        """move relative"""
        self.motor.move_relative(dx, zaber_motion.Units.LENGTH_MILLIMETRES)
    
    def move_home(self):
        """move to the home position"""
        self.moveA(self.home_position)
        
    def set_home(self,home):
        """set home position"""
        self.home_position=home
        
    def home(self):
        """home the motor (move to the end switch and set it as the home position)"""
        self.motor.home()
        self.homed=True
        
    def set_velocity(self,Vmax):
        """set velocity parameters
        maximum velocity [mm/s]"""
        self.motor.settings.set("maxspeed", Vmax, zaber_motion.Units.VELOCITY_MILLIMETRES_PER_SECOND)
        
    def get_velocity(self):
        """returns velocity parameters
        (minimum velocity, acceleration, maximum velocity)"""
        self.velocity = self.motor.settings.get("maxspeed", zaber_motion.Units.VELOCITY_MILLIMETRES_PER_SECOND)
        
    def ismoving(self):
        """check if the motor is moving"""
        return self.motor.is_busy()
    
    def stop(self):
        self.motor.stop()
        
    def disconnect(self,park=False):
        """run before closing"""
        if park:
            self.motor.park()
        for c in self.connections:
            c.close()
    
    @property
    def position(self):
        return self.motor.get_position(unit = zaber_motion.Units.LENGTH_MILLIMETRES)
     
    @property
    def is_moving(self):
        return self.motor.is_busy()
    
    @property
    def is_homed(self):
        return self.homed
    
    
    
# M=ZaberMotor('COM6')
# M=ZaberMotor()
    
    
    
    
    
    
    
    
    
