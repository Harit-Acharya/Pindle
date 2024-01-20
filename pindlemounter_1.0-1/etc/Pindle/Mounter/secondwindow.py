#!/bin/python3
import json
import sys
import time
import os
from PyQt5 import QtWidgets
from PyQt5 import uic,QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon,QMovie
from PyQt5.QtWidgets import QErrorMessage, QMainWindow, QListWidgetItem, QMessageBox, QLabel, QVBoxLayout

sys.path.insert(0,"/etc/Pindle/Mounter/")

class secondwinshow(QMainWindow):
    def __init__(self):
        super(secondwinshow, self).__init__()
        uic.loadUi("/etc/Pindle/Mounter/second.ui", self)
        self.setWindowTitle("Welcome to Pindle Mounter")
        self.setWindowIcon(QIcon("/usr/share/pixmaps/Pindle/Mounter/pindleicon.png"))
        self.setGeometry(0,0, self.frameSize().width(), self.frameSize().height())
        self.centerOnScreen()
        self.error_dialog = QErrorMessage()
        self.load()
        self.pushButton.clicked.connect(self.remove)
        self.pushButton_2.clicked.connect(self.add)

    def load(self):
        try:
            with open('/etc/Pindle/GDrive/gdrive_conf.json', 'r') as f:
                self.details2 = json.load(f)
            with open('/etc/Pindle/OneDrive/onedrive_conf.json', 'r') as f:
                self.details = json.load(f)
        except:
            self.error_dialog.showMessage("config file not found")
            time.sleep(10)
            exit(0)

        if len(self.details) == 0 and len(self.details2) == 0:
           self.error_dialog.showMessage("Nothing is mounted ")

        for key, value in self.details.items():
            item = QListWidgetItem("{} <--- mounted on ---> {}".format(key,value))
            self.listWidget.addItem(item)
        for key, value in self.details2.items():
            item = QListWidgetItem("{} <--- mounted on ---> {}".format(key,value))
            self.listWidget.addItem(item)

    def remove(self):
        self.msgBox = QMessageBox()
        self.msgBox.setIcon(QMessageBox.Information)
        self.msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.msgBox.setText("Do you really want to remove?")
        returnValue = self.msgBox.exec()
        if returnValue != QMessageBox.Ok:
            return
        else:
            listItems = list(self.listWidget.selectedItems())
            if not listItems: return
            for item in listItems:
                index = self.listWidget.indexFromItem(item)
                self.listWidget.takeItem(index.row())
                name = item.text()
                name = name.split(' <--- mounted on ---> ')[0]
                domain = name[name.index('@') + 1:]
                if domain == "gmail.com":
                    del self.details2[name]
                    with open('/etc/Pindle/GDrive/gdrive_conf.json', 'w') as f:
                        json.dump(self.details2, f)
                    os.system("sudo systemctl restart gdrive")
                else:
                    del self.details[name]
                    with open('/etc/Pindle/OneDrive/onedrive_conf.json', 'w') as f:
                        json.dump(self.details, f)
                    os.system("sudo systemctl restart onedrive")

    def centerOnScreen(self):
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move((resolution.width() // 2) - (self.frameSize().width() // 2),
                  (resolution.height() // 2) - (self.frameSize().height() // 2))

    def add(self):
        self.trying()

    def trying(self):
        self.label.setGeometry(QtCore.QRect(160, 140, 400, 180))
        self.label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        print("showing gif")
        self.movie = QMovie('/usr/share/pixmaps/Pindle/Mounter/waited.gif')
        print("showing gif completed")
        self.label.setMovie(self.movie)
        timer = QtCore.QTimer(self)
        self.movie.start()
        timer.singleShot(2000, self.stopanimate)

    def stopanimate(self):
        self.movie.stop()
        import first
        self.window = first.firstwinshow()
        self.close()
        self.window.show()

if __name__ == "__main__":
    arr = QtWidgets.QApplication(sys.argv)
    pi = secondwinshow()
    pi.show()
    arr.exec_()
