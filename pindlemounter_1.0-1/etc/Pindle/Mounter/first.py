#!/bin/python3
from PyQt5 import QtWidgets,uic,QtCore
from PyQt5.QtGui import QPixmap, QMovie, QIcon
import re
from PyQt5.QtWidgets import QPushButton, QErrorMessage, QLabel, QLineEdit
import os
import sys
import time
import json
sys.path.insert(0,"/etc/Pindle/OneDrive/")
sys.path.insert(1,"/etc/Pindle/Mounter/")
import onedrive_auth
from secondwindow import secondwinshow
sys.path.insert(2,"/etc/Pindle/GDrive/")
import googledrive_auth


class firstwinshow(QtWidgets.QMainWindow):
	def __init__(self):
		super(firstwinshow,self).__init__()
		uic.loadUi('/etc/Pindle/Mounter/first.ui', self)
		self.errorbox = QErrorMessage()
		self.setGeometry(0,0, self.frameSize().width(), self.frameSize().height())
		self.centerOnScreen()
		self.setWindowTitle("New Mouting Configuration")
		self.setWindowIcon(QIcon("/usr/share/pixmaps/Pindle/Mounter/pindleicon.png"))
		self.getdetails()
		self.mailcheck = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
		self.mailok = self.findChild(QLabel,"label_3")
		self.mountok = self.findChild(QLabel,"label_4")
		self.mailok.setScaledContents(True)
		self.mountok.setScaledContents(True)
		self.mailid = self.findChild(QLineEdit, "lineEdit")
		self.mount = self.findChild(QLineEdit, "lineEdit_2")
		self.mok = 0
		self.m2ok = 0
		self.mailid.textChanged.connect(self.check)
		self.mount.textChanged.connect(self.check2)
		self.setup = self.findChild(QPushButton, "pushButton")
		self.setup.clicked.connect(self.next)
		self.pushButton_2.clicked.connect(self.create_folder)

	def centerOnScreen(self):
		resolution = QtWidgets.QDesktopWidget().screenGeometry()
		self.move((resolution.width() // 2) - (self.frameSize().width() // 2),
				  (resolution.height() // 2) - (self.frameSize().height() // 2))

	def getdetails(self):
		try:
			with open('/etc/Pindle/GDrive/gdrive_conf.json','r') as f:
				self.details2 = json.load(f)
			with open('/etc/Pindle/OneDrive/onedrive_conf.json','r') as f:
				self.details = json.load(f)
		except:
			self.errorbox.showMessage("/etc/Pindle/(Gdrive/Onedrive)_conf.json file not found")
			time.sleep(10)
			exit(0)

	def check(self):
		if (re.search(self.mailcheck, self.mailid.text())) and (self.mailid.text() not in list(self.details.keys())+list(self.details2.keys())):
			self.mailok.setPixmap(QPixmap("/usr/share/pixmaps/Pindle/Mounter/valid.png"))
			self.mok = 1
		else:
			self.mailok.setPixmap(QPixmap("/usr/share/pixmaps/Pindle/Mounter/invalid.png"))
			self.mok = 0

	def check2(self):
		if os.path.exists(self.mount.text()) and (self.mount.text() not in list(self.details.values())+list(self.details2.values())) and not (len(os.listdir(self.mount.text()))):
			self.mountok.setPixmap(QPixmap("/usr/share/pixmaps/Pindle/Mounter/valid.png"))
			self.m2ok = 1
		else:
			self.mountok.setPixmap(QPixmap("/usr/share/pixmaps/Pindle/Mounter/invalid.png"))
			self.m2ok = 0

	def next(self):
		try:
			if self.mok == 1 and self.m2ok == 1:
				mail = self.mailid.text()
				domain = mail[mail.index('@') + 1:]
				self.trying()
				#self.errorbox.showMessage("After authentication please close the browser")
				if domain == "gmail.com":
					a,b = googledrive_auth.authenticate(mail)
					self.details2[mail] = self.mount.text()
					with open('/etc/Pindle/GDrive/gdrive_conf.json', 'w') as f:
						json.dump(self.details2, f)
					os.system("sudo systemctl restart gdrive")
				else:
					onedrive_auth.Authenticate(mail)
					self.details[mail] = self.mount.text()
					with open('/etc/Pindle/OneDrive/onedrive_conf.json','w') as f:
						json.dump(self.details, f)
					os.system("sudo systemctl restart onedrive")
			else:
				self.errorbox.showMessage("Invalid Mail Id!!")
		except:
			self.errorbox.showMessage("Something went wrong, Make sure you're connected to internet")
			exit(0)

	def trying(self):
		self.label_6.setGeometry(QtCore.QRect(250, 180, 400, 180))
		self.label_6.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		self.movie = QMovie('/usr/share/pixmaps/Pindle/Mounter/waited.gif')
		self.label_6.setMovie(self.movie)
		timer = QtCore.QTimer(self)
		self.movie.start()
		timer.singleShot(2000, self.stopanimate)

	def stopanimate(self):
		self.movie.stop()
		self.window =secondwinshow()
		self.window.show()
		self.close()

	def create_folder(self):
		try:
			os.system("sudo mkdir {}".format(self.mount.text()))
			self.mountok.setPixmap(QPixmap("/usr/share/pixmaps/Pindle/Mounter/valid.png"))
			self.m2ok = 1
		except:
			self.errorbox.showMessage("Invalid parent folder")

if __name__ == "__main__":
	arr = QtWidgets.QApplication(sys.argv)
	pi = firstwinshow()
	pi.show()
	arr.exec_()
