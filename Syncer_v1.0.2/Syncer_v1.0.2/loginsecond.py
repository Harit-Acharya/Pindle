import json
import os
import shutil
import sys

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtGui import QPixmap, QMovie, QIcon
from PyQt5.QtWidgets import QPushButton, QErrorMessage, QLineEdit, QLabel

import googledrive
import onedrive
from Google import Create_Service
from firstwindowone import secondwin

class UI(QtWidgets.QMainWindow):
	def __init__(self):
		super(UI,self).__init__()
		uic.loadUi('/etc/Pindle/Syncer/loginsecond.ui', self)
		self.setWindowTitle("New Configuration")
		self.setGeometry(0, 0, self.frameSize().width(), self.frameSize().height())
		self.centerOnScreen()
		self.setWindowIcon(QIcon("/usr/share/pixmaps/Pindle/Syncer/sync.png"))
		self.errorbox = QErrorMessage()
		self.setup_btn = self.findChild(QPushButton, "pushButton")
		self.setup_btn.clicked.connect(self.setup)
		self.id1 = self.findChild(QLineEdit, "lineEdit_2")
		self.id1.textChanged.connect(self.namecheck)
		self.id2 = self.findChild(QLineEdit, "lineEdit_3")
		self.id2.textChanged.connect(self.namecheck)
		self.msg = self.findChild(QLabel, "label_4")
		self.nameok = self.findChild(QLabel, "label_5")
		self.nameok.setScaledContents(True)
		self.nameok2 = self.findChild(QLabel, "label_8")
		self.nameok2.setScaledContents(True)
		self.nok = 1
		self.onload()

	def centerOnScreen(self):
		resolution = QtWidgets.QDesktopWidget().screenGeometry()
		self.move((resolution.width() // 2) - (self.frameSize().width() // 2),
				  (resolution.height() // 2) - (self.frameSize().height() // 2))

	def trying(self):
		self.label_2.setGeometry(QtCore.QRect(260, 240, 400, 180))
		self.label_2.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		self.movie = QMovie('/usr/share/pixmaps/Pindle/Syncer/waited.gif')
		self.label_2.setMovie(self.movie)
		timer4 = QtCore.QTimer(self)
		self.movie.start()
		timer4.singleShot(20000, self.stopanimation)

	def stopanimation(self):
		self.display = secondwin()
		self.close()
		self.movie.stop()
		self.display.show()

	def namecheck(self):
		if self.id1.text() != self.id2.text():
			self.nameok.setPixmap(QPixmap("/usr/share/pixmaps/Pindle/Syncer/valid.png"))
			self.nameok2.setPixmap(QPixmap("/usr/share/pixmaps/Pindle/Syncer/valid.png"))
			self.nok = 1
		else:
			self.nameok.setPixmap(QPixmap("/usr/share/pixmaps/Pindle/Syncer/invalid.png"))
			self.nameok2.setPixmap(QPixmap("/usr/share/pixmaps/Pindle/Syncer/invalid.png"))
			self.nok = 0

	def onload(self):
		with open('/etc/Pindle/Syncer/localname.json', 'r') as f:
			self.details = json.load(f)
		self.mail = self.details["mailid"]
		self.installation_directory = self.details["insdir"]
		self.details['firsttime'] = 1
		domain = self.mail[self.mail.index('@') + 1:]
		if domain == "gmail.com":
			self.gdrivesetup()
		else:
			self.onedrivesetup()
		self.config = {}
		if self.generate != True:
			with open('/etc/Pindle/Syncer/pindleconfig.json', 'r') as f:
				self.config = json.load(f)
			self.id1.setText(self.config['device1']['name'])
			self.id2.setText(self.config['device2']['name'])
			self.details["localname"] = self.config['device2']['name']
			self.details["device2"] = self.config['device1']['name']
			self.id1.setEnabled(False)
			self.id2.setEnabled(False)
			self.nok =1
			self.setup()
		print("completed")

	def gdrivesetup(self):
		try:
			CLIENT_SECRET_FILE = '/etc/Pindle/Syncer/credentials.json'
			API_NAME = 'drive'
			API_VERSION = 'v3'
			SCOPES = ['https://www.googleapis.com/auth/drive']
			self.api = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
			self.Gdrive = True
			fid = googledrive.search(self.api,"file","pindleconfig.json")
			if fid == '':
				self.generate = True
			else:
				self.generate =False
				googledrive.download(self.api,"pindleconfig.json",self.installation_directory,'file')
		except:
			self.errorbox.showMessage("OOPS!! Something is Wrong!!\nPlease check your connection")
			exit(0)

	def onedrivesetup(self):
		try:
			self.client = onedrive.LoadSession()
			onedrive.search(self.client,'/',"pindleconfig.json",[],"file")
			fid = onedrive.get_fid()
			self.Gdrive = False
			if fid ==None:
				self.generate = True
			else:
				self.generate=False
				onedrive.download(self.client,"pindleconfig.json",os.path.join(self.installation_directory,"pindleconfig.json"),'file')
		except:
			self.errorbox.showMessage("OOPS!! Something is Wrong!!\nPlease check your connection")
			exit(0)

	def setup(self):
		#disable finish button
		if self.generate == True:
			if self.nok == 1:
				self.details["localname"] = self.id1.text()
				self.details['device2'] = self.id2.text()
				self.config['device1'] = {}
				self.config['device2'] = {}
				self.config['device1']['name'] = self.id1.text()
				self.config['device2']['name'] = self.id2.text()
				self.config['device1']['connections'] = []
				self.config['device2']['connections'] = []
			else:
				self.errorbox.showMessage("Please Set Proper Name")
				return

		#update tree to local name on the config directory
		if self.config['device1']['name'] == self.details['localname']:
			self.config['device1']['size'] = shutil.disk_usage('/')
			self.config['device2']['size'] = ""
			self.config["connections"] = {}
			self.config['issetup'] = 0
		else:
			self.config['device2']['size'] = shutil.disk_usage('/')
			self.config['issetup'] = 1

		with open(os.path.join(self.installation_directory,'localname.json'), 'w+') as f:
			json.dump(self.details, f)

		with open(os.path.join(self.installation_directory,'pindleconfig.json'), 'w+') as f:
			json.dump(self.config, f)

		self.on_close()
		self.trying()

	def on_close(self):
			if self.Gdrive == True :
				if self.generate == True:
					if "" == googledrive.search(self.api,'folder','Pindle'):
						googledrive.create_folder(self.api, "Files", "Pindle","folder")
				googledrive.upload(self.api,os.path.join(self.installation_directory,'pindleconfig.json'),"Pindle", 'file')
			if self.Gdrive == False:
				if self.generate == True:
					onedrive.create_folder(self.client, "Pindle", "/")
				onedrive.upload(self.client, "Pindle", os.path.join(self.installation_directory,'pindleconfig.json'),'folder')

if __name__ == "__main__":
	arr=QtWidgets.QApplication(sys.argv)
	pi=UI()
	pi.show()
	arr.exec_()
