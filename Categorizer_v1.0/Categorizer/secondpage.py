import math

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPalette, QPainter, QBrush, QColor, QPen
from PyQt5.QtWidgets import QErrorMessage, QMainWindow, QApplication, QPushButton, QFileSystemModel, QTreeView, \
    QListWidget, QListWidgetItem, QListView, QWidget
from PyQt5 import uic
import sys
import os.path
import json
import firstpage
import update_categories

class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        uic.loadUi("categorization2.ui", self)
        self.setFixedSize(1040,880)
        self.setWindowIcon(QIcon("icon.png"))
        self.error_dialog = QErrorMessage()
        """This for circular waiting"""
        widget = QWidget(self)
        self.setCentralWidget(widget)
        self.overlay = Overlay(self.centralWidget())
        self.overlay.hide()
        """ Ends Here"""
        self.loadpaths()
        self.listview = self.findChild(QListWidget,"listWidget")
        self.listview.setMovement(QListView.Free)
        self.tree = self.findChild(QTreeView,"DirectoryView")
        self.remove = self.findChild(QPushButton,"pushButton_4")
        self.back=self.findChild(QPushButton,"pushButton")
        self.model = QFileSystemModel()
        self.model.setReadOnly(True)
        self.model.setRootPath('/')
        self.tree.setModel(self.model)
        self.tree.header().hideSection(1)
        self.tree.header().hideSection(2)
        self.tree.header().hideSection(3)
        self.paths_tolist()
        self.tree.clicked.connect(self.add_dir)
        self.pushButton_2.clicked.connect(self.savepaths)
        self.remove.clicked.connect(self.remove_dir)
        self.back.clicked.connect(self.goback)

    def paths_tolist(self):
        for direc in self.paths:
            item = QListWidgetItem(direc)
            self.listview.addItem(item)

    def goback(self):
        self.window2 = firstpage.UI()
        self.window2.show()
        self.savepaths()
        self.hide()

    def add_dir(self,index):
        try:
            direc = self.model.filePath(index)
            add = 1
            if os.path.isdir(direc) and not(direc in self.paths):
                for path in self.paths:
                    if os.path.dirname(direc) in self.paths:
                        add = 0
                        self.error_dialog.showMessage('Parent Directory is already in list!!')
                        break
                    if os.path.commonprefix([direc[1:],path[1:]]) != '':
                        if len(direc)<len(path):
        #                       remove from listview
                            self.paths.remove(path)
                            add = 1
                if add == 1:
                    item = QListWidgetItem(direc)
                    self.paths.append(direc)
                    self.listview.addItem(item)
            else:
                self.error_dialog.showMessage('Directory is already in list!!')
        except:
            pass

    def remove_dir(self):
        try:
            listItems = list(self.listview.selectedItems())
            if not listItems: return
            for item in listItems:
                index = self.listview.indexFromItem(item)
                self.listview.takeItem(index.row())
                self.paths.remove(item.text())
        except:
            pass

    def savepaths(self):
        self.settings['paths'] = self.paths
        with open('path_settings.json', 'w') as json_file:
            json.dump(self.settings, json_file)
        while update_categories.apply()!= "completed":
            self.overlay.show()

    def loadpaths(self):
        with open('path_settings.json') as f:
            self.settings = json.load(f)
        self.paths = self.settings['paths']

class Overlay(QWidget):
   def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        palette = QPalette(self.palette())
        palette.setColor(palette.Background, Qt.transparent)
        self.setPalette(palette)

   def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), QBrush(QColor(255, 255, 255, 127)))
        painter.setPen(QPen(Qt.NoPen))

        for i in range(6):
           if (self.counter / 5) % 6 == i:
              painter.setBrush(QBrush(QColor(127 + (self.counter % 5)*32, 127, 127)))
           else:
              painter.setBrush(QBrush(QColor(127, 127, 127)))
           painter.drawEllipse(self.width()/2 + 30 * math.cos(2 * math.pi * i / 6.0) - 10,self.height()/2 + 30 * math.sin(2 * math.pi * i / 6.0) - 10,20, 20)
        painter.end()

   def showEvent(self, event):
       self.timer = self.startTimer(50)
       self.counter = 0

   def timerEvent(self, event):
        self.counter += 1
        self.update()
        if self.counter == 60:
            self.killTimer(self.timer)
            self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UI()
    window.show()
    a = app.exec_()
    sys.exit(a)


