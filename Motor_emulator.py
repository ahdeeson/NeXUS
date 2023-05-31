"""
Motor emulator class

for testing purposes

@author: Slawa
"""

class Motor_emulator():
    
    def __init__(self,init=True,Autoconnect=True):
        self.Type='Emulator'
        self.scale=1
        self.Pos=0
        self.ishomed=False
        self.units='mm'
        self.home_position=0
        self.SN=1
        
    def connect(self):
        pass
        
    def moveA(self,X):
        """move to position X"""
        self.Pos=X
        
    def moveR(self,dx):
        """move relative"""
        self.Pos+=dx
        
    def move_home(self):
        """move to the home position"""
        self.Pos=0
        
    def home(self):
        """home the motor (move to the end switch and set it as the home position)"""
        self.Pos=0
        self.ishomed=True
        
    def ismoving(self):
        """check if the motor is moving"""
        return False
    
    def stop(self):
        pass
        
    def disconnect(self):
        """disconnect the motor and the port"""
        pass
    
    def set_home(self,home):
        """set home position"""
        self.home_position=home
    
    @property
    def position(self):
        return self.Pos
     
    @property
    def is_moving(self):
        return self.motor.is_moving()
    
    @property
    def is_homed(self):
        return self.ishomed
        
        