"""
motor GUI

@author: Slawa
"""

from PyQt5.QtWidgets import *
from PyQt5 import uic, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import pyqtgraph as pg
import pandas as pd

import os
import sys
Path=os.path.dirname((os.path.abspath(__file__)))
sys.path.append(Path)

from Motor_class import *
import error_class as ER

#class for table construction
class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])

class MotorGUI(QMainWindow):
# class MotorGUI(QDialog):
    def __init__(self,show=True):
        self.app=QApplication(sys.argv)
        super(MotorGUI, self).__init__()
        uic.loadUi(Path+"\\Qt\\motor.ui", self)
        # uic.loadUi(Path+"\\Qt\\motor_dialog.ui", self)
        if show:
            self.show()
        self.connectwindow=ConnectWindow()
        self.configwindow=ConfigWindow()
        
        self.connected=False
        self.motor=Motor()
        
        self.connectBt.clicked.connect(self.showconnect)
        self.saveBt.clicked.connect(self.save)
        self.configwindow.saveBt.clicked.connect(self.read_save_config)
        self.configwindow.acceptBt.clicked.connect(self.readconfig)
        self.configBt.clicked.connect(self.config)
        self.homeBt.clicked.connect(self.movehome)
        self.moveLeftBt.clicked.connect(self.moveL)
        self.stopBt.clicked.connect(self.stop)
        self.moveRightBt.clicked.connect(self.moveR)
        self.sethomeBt.clicked.connect(self.sethome)
        self.Home.clicked.connect(self.home)
        self.moveToBt.clicked.connect(self.moveAclicked)
        
        self.connectwindow.cancelBt.clicked.connect(self.cancel_connection)
        self.connectwindow.connectBt.clicked.connect(self.connect)
        
        self.Dtimer = QtCore.QTimer(self)
        self.Dtimer.setInterval(200) #.2 seconds
        self.Dtimer.timeout.connect(self.DisplayPosition)
        self.Dtimer.start()

    def home(self):
        self.motor.motor.home()

    def showconnect(self):
        """open connection interface"""
        connected=self.connectBt.isChecked()
        if not connected:
            self.disconnect()
        else:
            self.connectwindow.show()
            data=self.motor.motorlist
            self.model = TableModel(data)
            self.connectwindow.table.setModel(self.model)
        
    def connect(self):
        """open connection interface"""
        try:
            index = self.connectwindow.table.selectedIndexes()[0].row()
            self.motor.connect(index)
            self.setWindowTitle(self.motor.config_parameters['userID'] + ' ' + self.motor.Type + ' ' + str(self.motor.SN))
            self.configwindow.setWindowTitle(self.configwindow.windowTitle()+' ' +
                                             self.motor.Type + ' ' + str(self.motor.SN))
        except ER.SL_exception as error:
            self.showerror(error)
            self.connectBt.setChecked(False)
            self.connected=False
        else:
            self.connected=True
            self.showstatus('connected')
        self.connectwindow.hide()
        
                
    def cancel_connection(self):
        self.connectwindow.hide()
        self.connectBt.setChecked(False)
        self.connected=False
        # raise ER.SL_exception("connection canceled")
            
    def disconnect(self):
        """disconnect the motor"""
        self.connected=False
        self.showstatus('disconnected')
        try:
            self.motor.disconnect()
        except ER.SL_exception as error:
            self.showerror(error)
        
    def save(self):
        """save config settings"""
        self.motor.save_config()
        
    def config(self):
        """configurate the motor"""
        self.configwindow.show()
        CP=self.motor.config_parameters
        self.configwindow.vendor.setPlaceholderText(CP['vendor'])
        self.configwindow.SN.setPlaceholderText(str(CP['SN']))
        self.configwindow.UserID.setPlaceholderText(str(CP['userID']))
        self.configwindow.NexusID.display(CP['NexusID'])
        self.configwindow.Pmin.setValue(CP['limit min'])
        self.configwindow.Pmax.setValue(CP['limit max'])
        self.configwindow.velocity.setValue(CP['velocity'])
        self.configwindow.Phome.setValue(CP['home position'])
        self.configwindow.left_name.setPlaceholderText(str(CP['left name']))
        self.configwindow.right_name.setPlaceholderText(str(CP['right name']))
        
    def readconfig(self):
        """configurate the motor"""
        self.motor.config_parameters['userID']=self.configwindow.UserID.toPlainText()
        self.motor.config_parameters['limit min']=self.configwindow.Pmin.value()
        self.motor.config_parameters['limit max']=self.configwindow.Pmax.value()
        self.motor.islimits=True
        self.motor.config_parameters['home position']=self.configwindow.Phome.value()
        self.motor.config_parameters['left name']=self.configwindow.left_name.toPlainText()
        self.motor.config_parameters['velocity'] = self.configwindow.velocity.value()
        self.motor.motor.setSpeed(self.configwindow.velocity.value())
        self.motor.config_parameters['right name']=self.configwindow.right_name.toPlainText()
        self.configwindow.hide()
        if self.motor.motor.home_position and self.motor.motor.home_position != self.motor.config_parameters['home position']:
            self.motor.motor.set_home(self.motor.config_parameters['home position'])
            
        self.label_left.setText(self.motor.config_parameters['left name'])
        self.label_right.setText(self.motor.config_parameters['right name'])
        
    def read_save_config(self):
        self.readconfig()
        self.save()
        self.configwindow.hide()
        
    def showerror(self,error):
        self.error_message.setPlaceholderText(error.Message) 
        
        #make red text
        # self.error_message.setTextColor(QColor(255, 0, 0))
        # self.error_message.setAcceptRichText(True)
        # print('<p style="color: red">'+error.Message+'</p>')
        # self.error_message.setPlaceholderText('<p style="color: red">'+error.Message+'</p>')    
    
    def showstatus(self,text):
        self.error_message.setPlaceholderText(text)
    
    def DisplayPosition(self):
        if self.connected:
            self.positionInd.display(self.getPosition())
    
    def getPosition(self):
        return self.motor.position-self.motor.config_parameters['home position']
    
    def movehome(self):
        """move motor to home position"""
        self.motor.move_home()
        
    def moveL(self):
        """move left"""
        try:
            dx=self.StepSize.value()
            un=self.unitsControl.currentText()
            self.motor.moveR(-dx,units=un)
        except ER.SL_exception as error:
            self.showerror(error)
        
    def moveR(self):
        """move right"""
        try:
            dx=self.StepSize.value()
            un=self.unitsControl.currentText()
            self.motor.moveR(dx,units=un)
        except ER.SL_exception as error:
            self.showerror(error)
        
    def stop(self):
        """stop motion"""
        self.motor.stop()
        
    def sethome(self):
        """set home position as the current position"""
        self.motor.set_home()
        
    def moveAclicked(self):
        """move absolute"""
        try:
            X=self.moveToIn.value()
            self.moveA(X)
        except ER.SL_exception as error:
            self.showerror(error)
            
    def moveA(self,X):
        """move absolute"""
        un=self.unitsControl.currentText()
        self.motor.moveA(X+self.motor.config_parameters['home position'],units=un)
        
    def closeEvent(self, event):
        """call at closing"""
        self.disconnect()
    
class ConnectWindow(QDialog):
    def __init__(self):
        super(ConnectWindow, self).__init__()
        uic.loadUi(Path+"\\Qt\\connect.ui", self)
        
class ConfigWindow(QDialog):
    def __init__(self):
        super(ConfigWindow, self).__init__()
        uic.loadUi(Path+"\\Qt\\motor_config.ui", self)
        
        
        
if __name__ == '__main__':
    app = QApplication([])
    window = MotorGUI()

    app.exec_()