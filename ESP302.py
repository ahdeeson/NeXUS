import telnetlib
import time


class ESP302():
    def __init__(self):
        self.Type = 'ESP302'
        self.home_position = 0
        self.homed = False
        self.nMotors = 0
        self.motorlist = []
        self.axis = None

        self.connection = telnetlib.Telnet()
        self.connection.open('192.168.50.69', 5001)

        self.search()

    def search(self):
        # print(self.send_command(0, 'ZU', '?'))
        for i in range(3):
            name = self.send_command(i+1, 'ID', '?')
            if b'NO STAGE' not in name:
                name = str(name)[2:-1]
                self.motorlist.append(name.split(',')[1])
        self.nMotors = len(self.motorlist)

    def connect(self, SN):
        self.axis = self.motorlist.index(SN) + 1
        self.send_command(self.axis, 'MO')
        self.units = 'mm'
        self.encoded = True
        self.maxV = float(self.send_command(self.axis, 'VU', '?'))
        self.maxA = float(self.send_command(self.axis, 'AU', '?'))

    def disconnect(self):
        self.send_command(self.axis, 'MF')
        self.axis = None

    def setSpeed(self, v):
        v = self.maxV * (v/100)
        a = self.maxA * (v / 100)
        self.send_command(self.axis, 'VA', v)
        self.send_command(self.axis, 'AC', a)

    def moveR(self, dx, WaitToMove=True):
        self.send_command(self.axis, 'PR', dx)
        if WaitToMove:
            moving = self.send_command(self.axis, 'MD', '?')
            while moving != b'1':
                moving = self.send_command(self.axis, 'MD', '?')

    def moveA(self, x, WaitToMove=True):
        self.send_command(self.axis, 'PA', x)
        if WaitToMove:
            moving = self.send_command(self.axis, 'MD', '?')
            while moving != b'1':
                moving = self.send_command(self.axis, 'MD', '?')

    def stop(self):
        self.send_command(self.axis, 'ST')

    def set_home(self, home):
        self.home_position = home

    def move_home(self):
        print(self.home_position)
        self.moveA(self.home_position)
        self.send_command(self.axis, 'MO')

    @property
    def position(self):
        return float(self.send_command(self.axis, 'TP', '?'))

    def home(self):
        self.send_command(self.axis, 'OR', 2)
        moving = self.send_command(self.axis, 'MD', '?')
        while moving != b'1':
            moving = self.send_command(self.axis, 'MD', '?')
        self.homed = True
        # self.home_position = 0
        self.send_command(self.axis, 'MO')

    def send_command(self, axis, command, nn=None):
        if nn or nn == 0:
            query = str(axis) + command + str(nn) + '\n'
        else:
            query = str(axis) + command + '\n'
        self.connection.write(query.encode('utf-8'))
        if nn == '?':
            resp = self.connection.read_until(b"\n", timeout=5)[:-2]
            return resp

    @property
    def is_moving(self):
        mov = self.send_command(self.axis, 'MD', '?')
        if mov != b'0':
            return True
        else:
            return False

    @property
    def is_homed(self):
        return self.homed

    @property
    def hasSensor(self):
        return self.encoded



