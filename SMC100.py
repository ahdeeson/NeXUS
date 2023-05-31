import serial
import time
import sys, os

from CustomException import CustomException


class SMC100:
    def __init__(self, port='COM7', timeout=1, controller=1):
        # connection configuration
        try:
            self.port = port
            self.ser = serial.Serial(
                port=port,
                baudrate=57600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                xonxoff=True,
                timeout=timeout
            )
            if controller and 1 <= controller <= 31:
                self.controller = controller
            else:
                print("Please pass a valid controller address")
                raise CustomException("C")

            self.states = {
                "0A": "NOT REFERENCED from reset",
                "0B": "NOT REFERENCED from HOMING",
                "0C": "NOT REFERENCED from CONFIGURATION",
                "0D": "NOT REFERENCED from DISABLE",
                "0E": "NOT REFERENCED from READY",
                "0F": "NOT REFERENCED from MOVING",
                "10": "NOT REFERENCED ESP stage error",
                "11": "NOT REFERENCED from JOGGING",
                "14": "CONFIGURATION",
                "1E": "HOMING commanded from RS-232-C",
                "1F": "HOMING commanded by Keypad",
                "28": "MOVING",
                "32": "READY from HOMING",
                "33": "READY from MOVING",
                "34": "READY from DISABLE",
                "35": "READY from JOGGING",
                "3C": "DISABLE from READY",
                "3D": "DISABLE from MOVING",
                "3E": "DISABLE from JOGGING",
                "46": "JOGGING from READY",
                "47": "JOGGING from DISABLE"
            }

        except Exception as e:
            print("error opening the serial port: {}".format(e))

    def get_acceleration(self):
        """
            If the sign “?” takes place of nn, this command returns the current programmed
            value for acceleration

            Args: command (str) in the form of xxAC? where xx (int) = controller address in range 1 to 31

        :return: acceleration in units/s^2. Format: 1AC500
        """
        acc = self.execute_command(str(self.controller), "AC", "?")
        return acc

    def set_acceleration(self, acc):
        """
        In CONFIGURATION state, this command sets the maximum acceleration value which
        can then be saved in the controller’s nonvolatile memory using the PW command. This
        is the maximum acceleration that can be applied to the mechanical system.

        Args: command (str) in the form of xxACnn where xx (int) = controller address  in range 1 to 31 and
        nn (float)= acceleration in units/s^2 in range > 10^-6 and < 10^12

        """
        if acc and 10 ** -6 < acc < 10 ** 12:
            self.enter_configuration()
            self.execute_command(str(self.controller), "AC", str(acc))
            self.exit_configuration()
        else:
            raise CustomException("C")

    def get_stage_identifier(self):
        """
            The ID? command return the stage identifier. When used with Newport ESP compatible
            stages (see blue label on the product), this is the identical to the Newport product name.

            Args: command (str) is in the form of xxID? where xx (int)= controller address in range 1 to 31

            :return: stage identifier for controller xx
        """
        self.execute_command(str(self.controller), "ID", "?")

    # def set_stage_identifier(self, stage_model_number):
    #     """
    #         In CONFIGURATION mode, this command allows changing the stage identifier.
    #         However, customer should never do this when the ESP stage configuration is enabled
    #         (ZX3)
    #         # TODO(ankita): Check this scenario where the ESP stage config is enabled
    #     :param command (str): Format - xxIDnn where xx (int)= controller address in range 1 to 31,
    #         nn (float) = stage model number in range 1-31 ASCII characters
    #     """
    #     if not command:
    #         raise Exception("Please use a valid command. Command cannot be empty")
    #
    #     controller_addr, command_name, nn = command[:2], command[2:4], command[4:]
    #     # TODO(ankita): Check the ASCII character range
    #     if stage_model_number and 1 <= stage_model_number <= 31:
    #         self.execute_command(str(self.controller), "ID", stage_model_number)
    #     else:
    #         raise Exception(" The command format is incorrect.")

    def get_HOME_search_velocity(self):
        """
        :param command: str, format = xxOH?
        :return: HOME search velocity in units/s
        """
        self.execute_command(str(self.controller), "OH", "?")

    def set_HOME_search_velocity(self, velocity):
        """
        This command sets the maximum velocity used by the controller for the HOME search
        :param velocity:
        """

        if velocity and 10 ** -6 < velocity < 10 ** 12:
            self.execute_command(str(self.controller), "OH", str(velocity))
        else:
            raise CustomException("C")
    
    def set_home_type(self,Type=2,adjust_limits=True):
        """Type:
        0 use MZ switch and encoder Index.
            1 use current position as HOME.
            2 use MZ switch only.
            3 use EoR- switch and encoder Index.
            4 use EoR- switch only"""
        self.enter_configuration()
        self.execute_command(str(self.controller), "HT",str(Type))
        
        if adjust_limits:
            if Type in [0, 1, 2]:
                self.set_neg_software_limit(-75)
                self.set_pos_software_limit(75)
            elif Type in [3, 4]:
                self.set_neg_software_limit(0)
                self.set_pos_software_limit(150)
                
        self.exit_configuration()

    def home(self):
        """required to enter ready state from the initial not referenced state"""
        self.execute_command(str(self.controller), cmd="OR")

    def move_absolute(self, new_target_position):
        """
        The PA command initiates an absolute move. When received, the positioner will move,
        with the predefined acceleration and velocity, to the new target position specified by nn

        :param new_target_position: position in units
        :param controller_addr: str, format = xxPAnn where xx (int)= controller address in range 1-31
        :return:
        """

        if not new_target_position:
            raise Exception("Please use a valid command. Command cannot be empty")

        # check if target position is greater than SL and lesser than SR
        SL = self.get_neg_software_limit()
        SR = self.get_pos_software_limit()

        if SL < new_target_position < SR:
            self.execute_command(str(self.controller), "PA", str(new_target_position))
        else:
            raise CustomException("C")

    def move_relative(self, displacement):
        """
        The PR command initiates a relative move. When received, the positioner will move,
        with the predefined acceleration and velocity, to a new target position nn units away
        from the current target position.

        :param displacement: (float)
        """

        if not displacement:
            raise Exception("Please use a valid command. Command cannot be empty")
        # check if target position is greater than SL and lesser than SR
        SL = self.get_neg_software_limit()
        SR = self.get_pos_software_limit()

        # check if SL < (current position + displacement) < SR
        curr_pos = self.get_current_position()

        if SL < curr_pos+displacement < SR:
            self.execute_command(str(self.controller), "PR", str(displacement))
        else:
            raise CustomException("C")

    def stop_motion(self):
        """
        The ST command is a safety feature. It stops a move in progress by decelerating the
        positioner immediately with the acceleration defined by the AC command until it stops.

        """
        self.execute_command(str(self.controller), "ST")

    def get_set_point_position(self):
        """
        The TH command returns the value of the set-point or theoretical position. This is the
        position where the positioner should be.
        """
        self.execute_command(str(self.controller), "TH")

    def get_current_position(self):
        """
        The TP command returns the value of the current position. This is the position where
        the positioner actually is according to his encoder value.

        """
        out = self.execute_command(str(self.controller), "TP", "?")
        out.rstrip('\r\n')
        index = out.index("TP") + 2
        out = out[index:]
        print(out)
        return float(out)

    def get_positional_error_controller_state(self):
        """
        description: gets the positioner error and the current controller state
        :return: The TS command returns six characters (1TSabcdef). The first 4 characters (abcd)
                represent the positioner error in Hexadecimal. The last two characters (ef) represent the
                controller state.
        """
        return self.execute_command(str(self.controller), "TS")

    def get_velocity(self):
        """
        This is the maximum velocity that can be applied to the mechanical system. It is also the
        default velocity that will be used for all moves unless a lower value is set in DISABLE
        or READY state
        :return: current velocity
        """
        return self.execute_command(str(self.controller), "VA", "?")

    def set_velocity(self, velocity):
        if velocity and 10 ^ -6 < velocity < 10 ^ 12:
            return self.execute_command(str(self.controller), "VA", str(velocity))

    def execute_command(self, clr_addr=None, cmd=None, nn=None):
        # get value
        if nn == "?":
            try:
                cmd = clr_addr + cmd + "?"
                # print("cmd = {}".format(cmd))
                self.ser.write((cmd + '\r\n').encode())
                time.sleep(1)
                out = self.ser.read(100).decode()
                print("Output: {} ".format(out))
                return out
            except Exception as e:
                print(e)
        else:
            cmd = clr_addr + cmd if nn is None else clr_addr + cmd + nn
            print("cmd = {}".format(cmd))
            try:
                self.ser.write((cmd + '\r\n').encode())
                out = self.ser.read(1000).decode()
                # print("Output: {} ".format(out))
            except Exception as e:
                print(e)
                
    def set_neg_software_limit(self,limit):
        if limit and -10**12 <= limit <= 0:
            self.execute_command(str(self.controller), "SL", str(limit))

    def get_neg_software_limit(self):
        out = self.execute_command(str(self.controller), "SL", "?")
        out.rstrip('\r\n')
        index = out.index("SL") + 2
        out = out[index:]
        # print(out)
        return int(out)

    def set_pos_software_limit(self,limit):
        if limit and 0 <= limit <= 10**12:
            self.execute_command(str(self.controller), "SR", str(limit))

    def get_pos_software_limit(self):
        out = self.execute_command(str(self.controller), "SR", "?")
        out.rstrip('\r\n')
        index = out.index("SR") + 2
        out = out[index:]
        # print(out)
        return int(out)

    def get_controller_state(self):
        out = self.execute_command(str(self.controller), "TS", "?")
        print("out = {}".format(out))
        return out[-4:-2] if out else "No output"
    
    def enter_configuration(self):
        self.execute_command(str(self.controller), "PW", "1")
        
    def exit_configuration(self):
        self.execute_command(str(self.controller), "PW", "0")
        
    def is_moving(self):
        out=self.get_controller_state()
        return True if out == "28" else False
    
    def disconnect(self):
        self.ser.close()


C = SMC100(controller=1)

# C.home()

# C.move_relative(5)
# C.is_moving()
# C.get_controller_state()

# C.get_current_position()

# C.move_relative(5)
# time.sleep(1)
# controller.get_current_position()

# controller.move_absolute(10)
# controller.get_current_position()

