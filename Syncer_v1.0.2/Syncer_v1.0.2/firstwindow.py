from PyQt5 import QtWidgets,uic,QtCore
from PyQt5.QtGui import QPixmap, QMovie, QIcon
import re
from PyQt5.QtWidgets import QPushButton, QErrorMessage, QLabel, QLineEdit
import os
import sys
import time
import json
from loginsecond import UI
from firstwindowone import secondwin

class firstwinshow(QtWidgets.QMainWindow):
	def __init__(self):
		super(firstwinshow,self).__init__()
		uic.loadUi('/etc/Pindle/Syncer/loginfirst.ui', self)
		self.errorbox = QErrorMessage()
		self.setGeometry(0, 0, self.frameSize().width(), self.frameSize().height())
		self.centerOnScreen()
		self.setWindowTitle("Login Screen")
		self.setWindowIcon(QIcon("/usr/share/pixmaps/Pindle/Syncer/sync.png"))
		self.mailcheck = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
		self.details = {"localname": "", "mailid": "", "firsttime": 0, "insdir":""}
		self.mailok = self.findChild(QLabel,"label_3")
		self.mailok.setScaledContents(True)
		self.mailid = self.findChild(QLineEdit, "lineEdit")
		self.mailok.setScaledContents(True)
		self.mok = 0
		self.mailid.textChanged.connect(self.check)
		self.setup = self.findChild(QPushButton, "pushButton")
		self.setup.clicked.connect(self.next)

	def trying(self):
		self.label_2.setGeometry(QtCore.QRect(260, 240, 400, 180))
		self.label_2.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		self.movie = QMovie('/usr/share/pixmaps/Pindle/Syncer/waited.gif')
		self.label_2.setMovie(self.movie)
		timer4 = QtCore.QTimer(self)
		self.movie.start()
		timer4.singleShot(20000, self.stopanimation)

	def stopanimation(self):
		self.ti = UI()
		self.close()
		self.movie.stop()
		self.ti.show()

	def centerOnScreen(self):
		resolution = QtWidgets.QDesktopWidget().screenGeometry()
		self.move((resolution.width() // 2) - (self.frameSize().width() // 2),
				  (resolution.height() // 2) - (self.frameSize().height() // 2))

	def getdetails(self):
		try:
			with open('/etc/Pindle/Syncer/localname.json') as f:
				details = json.load(f)
			if details['firsttime'] == 1:
				self.window =secondwin()
				self.close()
				self.window.show()
		except:
			self.errorbox.showMessage("localname.json file not found")
			time.sleep(10)
			exit(0)

	def check(self):
		if (re.search(self.mailcheck, self.mailid.text())):
			self.mailok.setPixmap(QPixmap("/usr/share/pixmaps/Pindle/Syncer/valid.png"))
			self.mok = 1
		else:
			self.mailok.setPixmap(QPixmap("/usr/share/pixmaps/Pindle/Syncer/invalid.png"))
			self.mok = 0

	def next(self):
		if self.mok == 1:
			mail = self.mailid.text()
			domain = mail[mail.index('@') + 1:]
			#self.errorbox.showMessage("After authentication please close the browser")

			self.details['mailid'] = mail
			self.details['insdir'] = "/etc/Pindle/Syncer"

			with open('/etc/Pindle/Syncer/localname.json','w+') as f:
				json.dump(self.details, f)
			self.trying()
		else:
			self.errorbox.showMessage("Invalid Mail Id!!")

if __name__ == "__main__":
	arr = QtWidgets.QApplication(sys.argv)
	pi = firstwinshow()
	pi.show()
	pi.getdetails()
	arr.exec_()