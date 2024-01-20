from PyQt5 import QtWidgets,QtCore
from PyQt5.QtGui import QMovie
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
import sys

class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        uic.loadUi("displayfirsrt.ui", self)
        user_x,user_y = 1920/2,1080/2
        x = user_x - 415
        y = user_y - 290
        self.setGeometry(x, y, 830, 580)
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(flags)
        self.trying()

    def trying(self):
        self.movie = QMovie('finalpindle.gif')
        self.label.setMovie(self.movie)
        timer= QtCore.QTimer(self)
        self.movie.start()
        timer.singleShot(2000, self.stopanimation)

    def stopanimation(self):
        self.movie.stop()
        self.movie1 = QMovie('load.gif')
        self.label_2.setMovie(self.movie1)
        timer1 = QtCore.QTimer(self)
        self.movie1.start()
        timer1.singleShot(4000, self.stopanimate)

    def stopanimate(self):
        self.movie.stop()

if __name__ == "__main__":
    arr=  QtWidgets.QApplication(sys.argv)
    pi=UI()
    pi.show()
    arr.exec_()