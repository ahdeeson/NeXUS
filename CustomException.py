# @Author : Ankita
from enum import unique, Enum


@unique
class ErrorCodes(Enum):
    A = "Unknown message code or floating point controller address"
    B = "Controller address not correct"
    C = "Parameter missing or out of range"
    D = "Execution not allowed"
    H = "Execution not allowed in NOT REFERENCED state"
    I = "Execution not allowed in CONFIGURATION state"
    J = "Execution not allowed in DISABLE state"
    K = "Execution not allowed in READY state"
    L = "Execution not allowed in HOMING state"
    M = "Execution not allowed in MOVING state"


class CustomException(Exception):
    def __init__(self, code):
        self.code = code
        self.message = ErrorCodes(code)

    def __str__(self):
        return repr(self.code)
