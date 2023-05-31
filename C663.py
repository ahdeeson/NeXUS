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

from pipython import GCSDevice, pitools

REFMODES = ['FNL', 'FRF']


def readparametervalue(device, func_unit, parameter_id):
    return device.SPA(func_unit, parameter_id)[func_unit][parameter_id]

class C663():
    def __init__(self):
        self.Type = 'C663'
        self.home_position = 0
        self.homed = False
        self.encoded = True
        self.motorlist = ['L-611.991300V7']
        self.units = 'deg'
        self.controller = GCSDevice('C-663')
        self.controller.ConnectUSB(serialnum='022550121')

        self.search()

    def search(self):
        pitools.startup(self.controller, stages=self.motorlist, refmodes=REFMODES)

    def connect(self, axisName='L-611.991300V7'):
        axis = str(self.motorlist.index(axisName) + 1)
        self.axis = axis

    def setSpeed(self, velocity=100):
        velocity = velocity / 5
        self.controller.SPA({self.axis: {73: velocity}})

    def wait_for_finished_movement(self):
        pitools.waitontarget(self.controller, axes=self.axis)

    def moveR(self, dx, WaitToMove=True):
        x = dx + self.position
        self.controller.MOV(self.axis, x)
        if WaitToMove: self.wait_for_finished_movement()

    def moveA(self, x, WaitToMove=True):
        #x in degrees
        self.controller.MOV(self.axis, x)
        if WaitToMove: self.wait_for_finished_movement()

    def set_home(self, home):
        """set home position"""
        self.home_position = home

    def home(self, WaitToMove=True):
        print("homer")
        rangemin = self.controller.qTMN()
        self.controller.MOV(self.axis, rangemin[self.axis])
        if WaitToMove:
            self.wait_for_finished_movement()
        self.homed = True
        self.home_position = 0

    def move_home(self):
        """move to the home position"""
        print(self.position, self.home_position)
        self.moveA(self.home_position)

    def stop(self):
        self.controller.HLT(self.axis)

    def disconnect(self):
        self.axis = None
        self.units = None
        self.encoded = None

    @property
    def position(self):
        """in deg"""
        return self.controller.qPOS(self.axis)[self.axis]

    @property
    def is_moving(self):
        pos = self.controller.qPOS(self.axis)[self.axis]
        moving = False
        if not pos == self.controller.qPOS(self.axis)[self.axis]:
            moving = True
        return moving

    @property
    def is_homed(self):
        return self.homed

    @property
    def hasSensor(self):
        return self.encoded