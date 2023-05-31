"""
class for thorlabs_elliptec  stages and filter holders

@author: Slawa
"""

import serial
from serial.tools import list_ports


from thorlabs_elliptec import ELLx, ELLError, ELLStatus

# stage = ELLx(serial_port='COM9')
# print(f"{stage.model_number} #{stage.device_id} on {stage.port_name}, serial number {stage.serial_number}, status {stage.status.description}")
# Prints something like:

#device=COM9, manufacturer=FTDI, product=None, vid=0x0403, pid=0x6015, serial_number=DK0BKCQSA, location=None    

# stage.home()
# # Movements are in real units appropriate for the device (degrees, mm).
# stage.move_absolute(25.0)

def com_ports():
    """returns [com,manufacture,serialN,product ID]"""
    out=[]
    for p in list_ports.comports():
        try:
            pid = f"{p.pid:#06x}"
        except:
            pid = p.pid

        out.append([p.device,p.manufacturer,p.serial_number,pid])
    return out

class Thor_ell_motor():
    
    def __init__(self,init=True,Autoconnect=True):
        self.Type='Thorlabs_elliptec'
        self.motorlist=[]
        self.home_position=0
        if init:
            self.search()
            if Autoconnect:
                self.connect()
                
    def search(self):
        """create a list of available motors"""
        allcoms=com_ports()
        for p in allcoms:
            if p[1] == 'FTDI' and not p[3] == None:
                self.motorlist.append([p[0],p[2],p[3]])
                
    def connect(self,MotorNumber=0,SN=None):
        if MotorNumber >= len(self.motorlist) and SN==None:
            print("specified motor is absent")
            #raise error
        else:
            if SN == None:
                p=self.motorlist[MotorNumber]
                self.motor=ELLx(serial_port=p[0])
                self.SN=p[1]
                self.units=self.motor.units
            else:
                com='0'
                for m in self.motorlist:
                    if m[1] == SN:
                        com=m[0]
                if com!='0':
                    self.SN=SN
                    self.motor=ELLx(serial_port=com)
                else:
                    print("motor with specified SN not found")

    def moveA(self,X):
        """move to position X"""
        self.motor.move_absolute(X)
        
    def moveR(self,dx):
        """move relative"""
        self.motor.move_relative(dx)
    
    def move_home(self):
        """move to the home position"""
        #self.motor.move_home()
        self.moveA(self.home_position)
        
    def home(self):
        """home the motor (move to the end switch and set it as the home position)"""
        self.motor.home()
        self.ishomed=True
        
    def set_home(self,home=None):
        """set home position"""
        if home==None:
            self.home_position=self.position
        else:
            self.home_position=home
        
    def ismoving(self):
        """check if the motor is moving"""
        return self.motor.is_moving()
    
    def stop(self):
        """doesnt seem to have this command"""
        pass
        
    def disconnect(self):
        """disconnect the motor and the port"""
        self.motor.close()
    
    @property
    def position(self):
        return self.motor.get_position()
     
    @property
    def is_moving(self):
        return self.ismoving()



# M=Thor_ell_motor()





















