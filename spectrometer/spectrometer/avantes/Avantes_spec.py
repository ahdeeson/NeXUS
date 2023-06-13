"""
Created on Tue Oct 11 20:51:44 2022

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


#from avaspec import *
import avaspec as AVS
import time
import numpy as np


class AvaSpec():
    def __init__(self):
        self.spec=[]
        self.find()
        self.Type='Avantes'
        self.sleeptime=0.001
        self.running=False
        
    def find(self, autoconnect=False):
        """finds all compartible devices"""
        AVS.AVS_Init(0)
        ret = AVS.AVS_GetNrOfDevices()
        self.Ndev=ret
        print("number of spectrometers: ", self.Ndev)
        # self.devices=AvsIdentityType()
        AVS.AvsIdentityType()
        self.devices=AVS.AVS_GetList(1)
        self.devconfig=[]
        for i in range(self.Ndev):
            d=self.devices[i]
            dev_handle = AVS.AVS_Activate(d)
            devcon = AVS.DeviceConfigType()
            devcon = AVS.AVS_GetParameter(dev_handle, 63484)
            SN=devcon.m_aUserFriendlyId
            lam = np.array(AVS.AVS_GetLambda(dev_handle))
            ind=lam>0.1
            lam=lam[ind]
            self.devconfig.append([SN,d,[lam.min(),lam.max()]])
        # print(self.devconfig)
        if autoconnect:
            self.connect()
        
    def connect(self, DeviceN=0, deviceID=None):
        """connects to the device number DeviceN in the list of found devices"""
        # mylist = AVS_GetList(1)
        if deviceID==None:
            mylist=self.devices
            # print(mylist[0])
            self.dev_handle = AVS.AVS_Activate(mylist[DeviceN])
        else:
            self.dev_handle = AVS.AVS_Activate(deviceID)
        # devcon = AVS.AVS.eviceConfigType()
        devcon = AVS.AVS_GetParameter(self.dev_handle, 63484)
        self.devcon=devcon
        self.SN=devcon.m_aUserFriendlyId.decode("utf-8")
        # print(devcon.m_aUserFriendlyId)
        self.pixels = devcon.m_Detector_m_NrPixels
        lam = np.array(AVS.AVS_GetLambda(self.dev_handle))
        ind=lam>0.1
        self.lam=lam[ind]
        
    def config_measure(self,Tintegration=0.01,Naverage=1,HighRes=True):
        """configurates spectrometer
        Tintegration is the integration time in ms
        Naverage is the number of spectra to average
        HighRes True enables 16 bit resolution (65535 max value), 
        false uses 14 bit resolution (16383 max value)"""
        ret = AVS.AVS_UseHighResAdc(self.dev_handle, HighRes)
        measconfig = AVS.MeasConfigType()
        measconfig.m_StartPixel = 0
        measconfig.m_StopPixel = self.pixels - 1
        measconfig.m_IntegrationTime = float(Tintegration)
        measconfig.m_IntegrationDelay = 0
        measconfig.m_NrAverages = int(Naverage)
        measconfig.m_CorDynDark_m_Enable = 0  # nesting of types does NOT work!!
        measconfig.m_CorDynDark_m_ForgetPercentage = 0
        measconfig.m_Smoothing_m_SmoothPix = 0
        measconfig.m_Smoothing_m_SmoothModel = 0
        measconfig.m_SaturationDetection = 0
        measconfig.m_Trigger_m_Mode = 0
        measconfig.m_Trigger_m_Source = 0
        measconfig.m_Trigger_m_SourceType = 0
        measconfig.m_Control_m_StrobeControl = 0
        measconfig.m_Control_m_LaserDelay = 0
        measconfig.m_Control_m_LaserWidth = 0
        measconfig.m_Control_m_LaserWaveLength = 785.0
        measconfig.m_Control_m_StoreToRam = 0
        self.ret = AVS.AVS_PrepareMeasure(self.dev_handle, measconfig)
        self.measurement_configed=True
        
    def measure(self,Nspec=1):
        """take data
        Nspec is the number of spectra to measure
        param nummeas: number of measurements to do. -1 is infinite, -2 is used to
        start Dynamic StoreToRam"""
        
        if self.measurement_configed:
            if (self.ret ==  0):
                self.spec=[]
                nummeas = Nspec
                scans = 0
                stopscanning = False
                while (stopscanning == False):
                    ret = AVS.AVS_Measure(self.dev_handle, 0, nummeas)
                    dataready = False
                    while (dataready == False):
                        dataready = (AVS.AVS_PollScan(self.dev_handle) == True)
                        time.sleep(self.sleeptime)
                    if dataready == True:
                        scans = scans + 1
                        if (scans >= nummeas):
                            stopscanning = True
                        self.spec.append(np.array(self.read_data()[0])[:len(self.lam)])             
                    # time.sleep(0.001)        
            else:
                print("Error in the measurement ",self.ret)
                #add raise
        
        else:
            print("first call config_measure")
            
    def read_data(self):
        """read data from the spectrometer
        returns (spectrum, timestamp)"""
        ret = AVS.AVS_GetScopeData(self.dev_handle)
        timestamp = ret[0]
        spectraldata = ret[1]
        return spectraldata, timestamp
    
    def start_measure(self,Nspec=1):
        """start measure but dont wait for ending it"""
        if self.measurement_configed:
            self.running=True
            ret = AVS.AVS_Measure(self.dev_handle, 0, Nspec)
        else:
            print("first call config_measure")
            
    def isdataready(self):
        """check if the measured data is ready"""
        return (AVS.AVS_PollScan(self.dev_handle) == True)
    
    def stop_measure(self):
        """stop measurement"""
        ret = AVS.AVS_StopMeasure(self.dev_handle)
        self.running=False
    
    def disconnect(self):
        """disconnect device
        (actually, probably, disconnects all avantes spectrometers)"""
        AVS.AVS_Done()
    
    
    
    
    
    
    
#test
# S=AvaSpec()
# S.connect()
# #deviceID=S.devices[1]
# S.config_measure(Tintegration=1)
# S.measure()
    
# S2=AvaSpec()
# S2.connect(1)
# #deviceID=S.devices[1]
# S2.config_measure()
# S2.measure()
    
    
    
    
    
    
    
    
        