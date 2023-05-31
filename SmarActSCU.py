"""
Smaract SCU controll class

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
Pypath='\\'.join(SP[:i+1])
sys.path.append(Pypath)

import smaract.scu as scu
from time import sleep


def lib_version_to_string(v):
    """
    Converts DLL version to version string.
    """
    major  = v >> 24 & 0xff
    minor  = v >> 16 & 0xff
    update = v >>  0 & 0xffff

    return "{}.{}.{}".format(major, minor, update)

def assert_lib_compatibility(driver=scu):
    """
    Checks that the major version numbers of the Python API and the
    loaded shared library are the same to avoid errors due to
    incompatibilities.
    Raises a RuntimeError if the major version numbers are different.
    """
    vapi = driver.api_version
    vlib = [int(i) for i in lib_version_to_string(driver.GetDLLVersion()).split('.')]
    if vapi[0] != vlib[0]:
        raise RuntimeError("Incompatible SCU3DControl python api and library version.")
        
# def has_linear_sensor(deviceIndex, channelIndex):
#     """
#     Checks whether the target channel is configured for a linear (or otherwise rotary) positioner.
#     For devices using older firmware, we determine the movement type by
#     either checking the configured SensorType using (GetSensorType)
#     or by probing with a linear/rotary specific command and evaluate the result (used below).
#     Newer devices support the MOVEMENT_TYPE channel property which should then be used instead.
#     """
#     try:
#         dummy = scu.GetPosition_S(deviceIndex, channelIndex)
#         return True
#     except scu.Error as e:
#         if e.code == scu.ErrorCode.WRONG_SENSOR_TYPE_ERROR:
#             return False
#         else:
#             raise

class SCU():
    def __init__(self,holdtime=1000,driver=scu):
        """holdtime time to hold position after movement in ms"""
        self.Type='SmarAct_SCU'
        self.home_position=0
        self.units="mm" # in the present version (inn principle, native step is is 100nm)
        self.homed=False
        self.motorlist=[]
        self.holdtime=holdtime
        self.driver=driver
        
        version = self.driver.GetDLLVersion()
        print("SCU3DControl library version: '{}'.".format(lib_version_to_string(version)))
        assert_lib_compatibility(self.driver)
        
        self.search()
        
    def search(self):
        """search for connected devices"""
        self.driver.InitDevices(self.driver.SYNCHRONOUS_COMMUNICATION)
        numOfDevices = self.driver.GetNumberOfDevices()
        self.Nmotors=numOfDevices
        print("SCU number of devices:", numOfDevices)
        # self.motorlist=self.driver.GetAvailableDevices() #doesnt work for SCU?
        # print(self.motorlist)
        
    def connect(self,deviceIndex=0,channelIndex=0):
        """connect to a device"""
        self.deviceIndex = deviceIndex
        self.channelIndex = channelIndex
        sensorPresent = self.driver.GetSensorPresent_S(deviceIndex, channelIndex)
        self.encoded=sensorPresent
    
    def wait_for_finished_movement(self):
        status = self.driver.GetStatus_S(self.deviceIndex, self.channelIndex)
        while status != self.driver.StatusCode.STOPPED and status != self.driver.StatusCode.HOLDING:
            status = self.driver.GetStatus_S(self.deviceIndex, self.channelIndex)
            sleep(0.03) # 30 ms
    
    def moveR(self, dx, WaitToMove=True):
        """move relative
        by dx in mm"""
        Dx=dx*10000 #SDK is using 1/10 um steps
        self.driver.MovePositionRelative_S(self.deviceIndex, self.channelIndex, int(Dx), self.holdtime)
        if WaitToMove:
            self.wait_for_finished_movement()
            
    def moveA(self, x, WaitToMove=True):
        """move absolute 
        to x in mm"""
        X=x*10000+self.home_position #SDK is using 1/10 um steps
        self.driver.MovePositionAbsolute_S(self.deviceIndex, self.channelIndex, int(X), self.holdtime)
        if WaitToMove:
            self.wait_for_finished_movement()
    
    def calibrate(self, WaitToMove=True):
        """This function may be used to increase the accuracy of the position calculation. It is only executable
            by a positioner that has a sensor attached to it.
            This function should be called once for each channel if the mechanical setup changes (different
            positioners connected to different channels)."""
        self.driver.CalibrateSensor_S(self.deviceIndex, self.channelIndex)
        if WaitToMove:
            self.wait_for_finished_movement()
    
    def set_home(self,home):
        """set home position"""
        self.home_position=home
    
    def home(self, WaitToMove=True):
        self.driver.MoveToReference_S(self.deviceIndex, self.channelIndex, self.holdtime, False)
        if WaitToMove:
            self.wait_for_finished_movement()
        self.homed=True
        self.home_position=0
        
    def move_home(self):
        """move to the home position"""
        self.moveA(self.home_position)
        
    def stop(self):
        self.driver.Stop_S(self.deviceIndex, self.channelIndex)
    
    def disconnect(self):
        self.driver.ReleaseDevices()
    
    @property
    def position(self):
        """in mm"""
        return self.driver.GetPosition_S(self.deviceIndex, self.channelIndex)/10000.
    
    @property
    def is_moving(self):
        status = self.driver.GetStatus_S(self.deviceIndex, self.channelIndex)
        if status != self.driver.StatusCode.STOPPED and status != self.driver.StatusCode.HOLDING:
            return True
        else:
            return False
        
    @property
    def is_homed(self):
        return self.homed
    
#test
# M=SCU()