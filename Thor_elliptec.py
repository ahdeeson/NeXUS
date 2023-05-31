# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 14:06:22 2023

@author: Slawa
"""

from thorlabs_elliptec import ELLx, ELLError, ELLStatus, list_devices
print(list_devices())

stage = ELLx(serial_port='COM9')
print(f"{stage.model_number} #{stage.device_id} on {stage.port_name}, serial number {stage.serial_number}, status {stage.status.description}")
# Prints something like:

#device=COM9, manufacturer=FTDI, product=None, vid=0x0403, pid=0x6015, serial_number=DK0BKCQSA, location=None    

stage.home()
# Movements are in real units appropriate for the device (degrees, mm).
stage.move_absolute(25.0)

