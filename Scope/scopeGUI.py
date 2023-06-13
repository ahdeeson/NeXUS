"""
Scope gui

@author Addison
"""
import os
import sys
from threading import Thread
from ctypes import byref, c_int16  # , c_int32, sizeof, c_byte
import math
import numpy as np

from PyQt5.QtWidgets import *
from PyQt5 import uic, QtCore
from PyQt5 import QtGui
import pyqtgraph as pg

from pico import read_block, read_block5000, channel_set, channel_set5000, get_timebase
from picosdk.ps2000 import ps2000
from picosdk.ps5000a import ps5000a
import smaract.ctl as ctl
# from picosdk.functions import assert_pico2000_ok, adc2mV
# from picosdk.PicoDeviceEnums import picoEnum
# from PyQt5.QtCore import Qt


Path = os.path.dirname((os.path.abspath(__file__)))
sys.path.append(Path)


class ScopeGUI(QMainWindow):
    def __init__(self, show=True):
        self.app = QApplication(sys.argv)
        super(ScopeGUI, self).__init__()
        uic.loadUi(Path[0:-5] + "Qt\\scope.ui", self)
        # # uic.loadUi(Path+"\\Qt\\motor_dialog.ui", self)
        if show:
            self.show()
        self.configuration = ConfigWindow()
        self.settingsBtn.clicked.connect(self.open_settings)
        self.plot.plot()
        self.step1.setValue(0.1)
        self.step2.setValue(0.1)
        self.running = False
        self.data = None
        self.correlogram = None
        self.device = None
        self.c_handle = c_int16()
        self.driver = None
        self.channel = 'A'
        self.vRange = '500MV'
        self.samples = 0
        self.vMax = 500
        self.timebase = 3
        self.interval = 0
        self.stpstrt.clicked.connect(self.start_stop)
        self.connectBtn.toggled.connect(self.connection)
        self.configuration.okBtn.clicked.connect(self.set)
        self.configuration.cancel.clicked.connect(self.configuration.hide)

        try:
            buffer = ctl.FindDevices()
            if len(buffer) == 0:
                print("MCS2 no devices found.", buffer)
            locators = buffer.split("\n")
            for locator in locators:
                print("MCS2 available device: {}".format(locator))
            print("MCS2 number of devices:", len(locators))
        except:
            print("MCS2 failed to find devices. Exit.")

        self.d_handle = ctl.Open(locators[0])
        self.motors = []
        for i in range(ctl.GetProperty_i32(self.d_handle, 0, ctl.Property.NUMBER_OF_CHANNELS)):
            ctl.SetProperty_i32(self.d_handle, i, ctl.Property.MOVE_MODE, ctl.MoveMode.CL_ABSOLUTE)
            self.motors.append(ctl.GetProperty_s(self.d_handle, i, ctl.Property.POSITIONER_TYPE_NAME))

        ctl.SetProperty_i64(self.d_handle, 1, ctl.Property.MOVE_VELOCITY, 100 * (10 ** 9))
        ctl.SetProperty_i64(self.d_handle, 2, ctl.Property.MOVE_VELOCITY, 100 * (10 ** 9))
        ctl.SetProperty_i64(self.d_handle, 1, ctl.Property.MOVE_ACCELERATION, 1 * (10 ** 12))
        ctl.SetProperty_i64(self.d_handle, 2, ctl.Property.MOVE_ACCELERATION, 1 * (10 ** 12))

        self.posTimer = QtCore.QTimer(self)
        self.posTimer.setInterval(200)  # .2 seconds
        self.posTimer.timeout.connect(self.display_position)
        self.posTimer.start()

        self.select1.addItems(self.motors)
        self.select1.setPlaceholderText(None)
        self.select2.addItems(self.motors)
        self.select2.setPlaceholderText(None)

    def start_stop(self):
        if self.running:
            """todo cancel"""
            self.running = False
            self.stpstrt.setText('Start')
        else:
            self.running = True
            self.stpstrt.setText('Stop')
            start = (self.start1.value(), self.start2.value())
            stop = (self.stop1.value(), self.stop2.value())
            step = [self.step1.value(), self.step2.value()]
            self.step = step
            m1 = self.motors.index(self.select1.currentText())
            m2 = self.motors.index(self.select2.currentText())

            if stop[0] < start[0]:
                step[0] = -step[0]
            if stop[1] < start[1]:
                step[1] = -step[1]

            self.plot.getPlotItem().setLabel('left', text=self.select1.currentText(), units='degrees')
            self.plot.getPlotItem().setLabel('bottom', text=self.select2.currentText(), units='degrees')

            ctl.Move(self.d_handle, m1, int(start[0] * 10 ** 9))
            self.wait_for_finished_movement()
            ctl.Move(self.d_handle, m2, int(start[1] * 10 ** 9))
            self.wait_for_finished_movement()
            steps = [
                math.floor((stop[0] - start[0]) / step[0]),
                math.floor((stop[1] - start[1]) / step[1])]

            self.data = np.zeros([steps[1] + 1, steps[0] + 1])
            self.show_data(start, stop, step)

            Thread(target=self.main_move, args=(m1, m2, start, stop, step, steps,)).start()

    def main_move(self, m1, m2, start, stop, step, steps):
        """begin main movement"""
        for i in range(steps[0] + 1):
            y = int((start[0] + step[0] * i) * 10 ** 9)
            ctl.Move(self.d_handle, m1, y)
            self.wait_for_finished_movement()

            for j in range(steps[1] + 1):
                if not self.running:
                    return
                # move in reverse every other sweep
                if i % 2 == 0:
                    x = int((start[1] + step[1] * j) * 10 ** 9)
                else:
                    x = int((stop[1] - step[1] * j) * 10 ** 9)
                ctl.Move(self.d_handle, m2, x)
                self.wait_for_finished_movement()
                # get reading
                if self.scopeSelect.currentText() == '2000':
                    voltage, time = read_block(self.device, self.channel, self.vRange, self.samples, self.timebase)
                else:
                    voltage, time = read_block5000(self.c_handle, self.vRange, self.channel, int(self.samples / 2),
                                                   self.timebase)
                # insert average into data
                if i % 2 == 0:
                    self.data[j][i] = voltage.mean()
                else:
                    self.data[(steps[1]) - j][i] = voltage.mean()
                self.correlogram.setImage(self.data)

        self.running = False
        self.stpstrt.toggle()
        self.stpstrt.setText('Start')

    def show_data(self, start, stop, step):
        self.correlogram = pg.ImageItem()
        self.correlogram.setTransform(QtGui.QTransform().translate(-0.5, -0.5))
        self.correlogram.setImage(self.data)
        self.correlogram.setRect(start[1] - step[1] / 2, start[0] - step[0] / 2, (stop[1] - start[1]) + step[1],
                                 (stop[0] - start[0]) + step[0])

        plot = self.plot.getPlotItem()
        plot.clear()
        plot.addItem(self.correlogram)

        color_map = pg.colormap.get("CET-R4")  # choose perceptually uniform, diverging color map
        bar = pg.ColorBarItem(values=(-self.vMax, self.vMax), colorMap=color_map)
        bar.setImageItem(self.correlogram, insert_in=plot)
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        plot.addItem(self.vLine, ignoreBounds=True)
        plot.addItem(self.hLine, ignoreBounds=True)
        self.vb = plot.vb
        self.correlogram.hoverEvent = self.mouseMoved

    def wait_for_finished_movement(self):
        """ Wait for events generated by the connected device """
        # The wait for event function blocks until an event was received or the timeout elapsed.
        # In case of timeout, a "ctl.Error" exception is raised containing the "TIMEOUT" error.
        # If the "timeout" parameter is set to "ctl.INFINITE" the call blocks until an event is received.
        # This can be useful in case the WaitForEvent function runs in a separate thread.
        # For simplicity, this is not shown here thus we set a timeout of 3 seconds.
        timeout = ctl.INFINITE  # in ms
        try:
            event = ctl.WaitForEvent(self.d_handle, timeout)
            # The "type" field specifies the event.
            # The "i32" data field gives additional information about the event.
            if event.type == ctl.EventType.MOVEMENT_FINISHED:
                if not (event.i32 == ctl.ErrorCode.NONE):
                    print("MCS2 movement finished, channel: {}, error: 0x{:04X} ({}) ".format(event.idx, event.i32,
                                                                                              ctl.GetResultInfo(
                                                                                                  event.i32)))
            else:
                print("MCS2 received event: {}".format(ctl.GetEventInfo(event)))
        except ctl.Error as e:
            if e.code == ctl.ErrorCode.TIMEOUT:
                print("MCS2 wait for event timed out after {} ms".format(timeout))
            else:
                print("MCS2 {}".format(ctl.GetResultInfo(e.code)))
            return

    def connection(self):
        radio_button = self.sender()
        if radio_button.isChecked():
            if self.scopeSelect.currentText() == '2000':
                self.driver = ps2000
                self.device = self.driver.open_unit()
            else:
                self.driver = ps5000a
                resolution = self.driver.PS5000A_DEVICE_RESOLUTION["PS5000A_DR_12BIT"]
                self.driver.ps5000aOpenUnit(byref(self.c_handle), None, resolution)
        else:
            if self.scopeSelect.currentText() == '2000':
                self.driver.close_unit(self.device)
            else:
                self.driver.ps5000aCloseUnit(self.c_handle)

    def set(self):
        v = self.configuration.range.currentText()

        self.channel = self.configuration.channel.currentText()
        self.vRange = v

        if v[-2] == 'M':
            self.vMax = int(v[:-2])
        else:
            self.vMax = int(v[:-1]) * 1000

        if self.scopeSelect.currentText() == '2000':
            channel_set(self.device, self.channel, self.vRange)
            self.timebase, self.interval = get_timebase(self.device, self.configuration.timebase.value() * 10 + 1)
        else:
            self.timebase = math.floor(self.configuration.timebase.value() / 16) + 3
            channel_set5000(self.c_handle, self.channel, self.vRange)

        self.configuration.hide()
        self.samples = self.configuration.samps.value()

        ctl.SetProperty_i64(self.d_handle, 1, ctl.Property.MOVE_VELOCITY,
                            int(self.configuration.vel1.value() * (10 ** 9)))
        ctl.SetProperty_i64(self.d_handle, 2, ctl.Property.MOVE_VELOCITY,
                            int(self.configuration.vel2.value() * (10 ** 9)))
        ctl.SetProperty_i64(self.d_handle, 1, ctl.Property.MOVE_ACCELERATION,
                            int(self.configuration.vel1.value() * (10 ** 10)))
        ctl.SetProperty_i64(self.d_handle, 2, ctl.Property.MOVE_ACCELERATION,
                            int(self.configuration.vel2.value() * (10 ** 10)))

    def open_settings(self):
        self.configuration.channel.clear()
        if self.scopeSelect.currentText() == '5000':
            self.configuration.channel.addItems(['A', 'B', 'C', 'D'])
            self.configuration.range.addItems(['50V'])
        else:
            self.configuration.channel.addItems(['A', 'B'])
        self.configuration.show()

    def display_position(self):
        ch = self.motors.index(self.select1.currentText())
        state = ctl.GetProperty_i32(self.d_handle, ch, ctl.Property.CHANNEL_STATE)
        encoded = state & ctl.ChannelState.SENSOR_PRESENT
        if encoded:
            self.pos1.display((ctl.GetProperty_i64(self.d_handle, ch, ctl.Property.POSITION) / 10 ** 9))
        else:
            self.pos1.display(None)

        ch = self.motors.index(self.select2.currentText())
        state = ctl.GetProperty_i32(self.d_handle, ch, ctl.Property.CHANNEL_STATE)
        encoded = state & ctl.ChannelState.SENSOR_PRESENT
        if encoded:
            self.pos2.display((ctl.GetProperty_i64(self.d_handle, ch, ctl.Property.POSITION) / 10 ** 9))
        else:
            self.pos2.display(None)

    def mouseMoved(self, evt):
        pos = evt.pos()
        i, j = pos.y(), pos.x()
        i = int(np.clip(i, 0, self.data.shape[1] - 1))
        j = int(np.clip(j, 0, self.data.shape[0] - 1))
        val = self.data[j, i]
        ppos = self.correlogram.mapToParent(pos)
        x, y = ppos.x(), ppos.y()
        self.label_8.setText(("<span style='font-size: 12pt'>mV=%0.1f,   <span style='color: red'>x=%0.1f</span>," +
                              "   <span style='color: green'>y=%0.1f</span>") % (val, x, y))
        self.vLine.setPos(x)
        self.hLine.setPos(y)
        # if self.plot.sceneBoundingRect().contains(pos):
        #     mousePoint = self.vb.mapSceneToView(pos)
        #     x_index = math.floor(mousePoint.x()/self.step[1] + .5)
        #     y_index = math.floor(mousePoint.y() / self.step[0] + .5)
        #     #if x_index >= 0 and x_index < len(self.data):


class ConfigWindow(QDialog):
    def __init__(self):
        super(ConfigWindow, self).__init__()
        uic.loadUi(Path[0:-5] + "\\Qt\\scope_config.ui", self)


if __name__ == '__main__':
    app = QApplication([])
    window = ScopeGUI()

    app.exec_()
