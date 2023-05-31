import serial

class NV100:
    def __init__(self, port='COM6', timeout=1.0, cl=0):
        # connection configuration
        try:
            self.port = port
            self.ser = serial.Serial(
                port=port,
                baudrate=115200,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=timeout
            )
        except Exception as e:
            print("error opening the serial port: {}".format(e))

    def setModeToClose(self, isEnabled):
        """
            Switching between OL and CL mode
            Args:
                isEnabled (bool): closed loop (True) or open loop (False)
       """
        command = 'cl,1' if isEnabled else 'cl,0'
        self.execute_command(command)

    def get_loop_status(self):
        op = self.execute_command('cl')
        return op

    def get_device_status(self):
        return self.execute_command('stat')

    def measure(self):
        out=self.execute_command('meas')
        return float(out.split(',')[1].split('\r')[0])

    def execute_command(self, command):
        self.ser.write((command + '\r\n').encode())
        out = self.ser.read(100).decode()
        # print("Output: {} ".format(out))
        return out
    
    def close(self):
        self.ser.close()

    def set(self, input):
        command = 'set,' + str(input)
        print(command)

        # Check the loop status
        op = self.get_loop_status()
        loop_index = op.index('cl') + 3
        print("current loop status = {}".format(op[loop_index]))

        # if current loop is closed, check range validity
        if op[loop_index] == '1':
            if 0 <= input <= 80:
                self.execute_command(command)
            else:
                raise Exception(" Actuator Displacement Value is out of range. Should be between 0-80 micrometers ")
        else:
            if -20 <= input <= 130:
                self.execute_command(command)
            else:
                raise Exception(" Actuator voltage Value is out of range. Should be between -20 to 130 V")


# if __name__ == '__main__':
#     controller = NV100()

#     # get device status
#     controller.get_device_status()

#     # get loop status
#     controller.get_loop_status()

#     # set voltage for closed loop
#     setValue = 60
#     controller.setModeToClose(True)
#     controller.set(setValue)
#     # measure the current position
#     controller.measure()

#     # set position for open loop
#     posValue = 20
#     controller.setModeToClose(False)
#     controller.set(posValue)
#     # measure the current position
#     controller.measure()
