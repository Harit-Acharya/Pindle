from PyQt5 import QtWidgets,uic,QtCore
from PyQt5.QtGui import QMovie, QIcon
import sys,json
from firstwindow import firstwinshow
from firstwindowone import secondwin

class UI(QtWidgets.QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        uic.loadUi("/etc/Pindle/Syncer/displayfirsrt.ui", self)
        self.setWindowIcon(QIcon("/usr/share/pixmaps/Pindle/Syncer/sync.png"))
        self.setGeometry(0, 0, 830, 580)
        self.centerOnScreen()
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(flags)
        self.trying()

    def trying(self):
        self.movie = QMovie('/usr/share/pixmaps/Pindle/Syncer/finalpindle.gif')
        self.label.setMovie(self.movie)
        timer= QtCore.QTimer(self)
        self.movie.start()
        timer.singleShot(2000, self.stopanimation)

    def stopanimation(self):
        self.movie.stop()
        self.movie1 = QMovie('/usr/share/pixmaps/Pindle/Syncer/load.gif')
        self.label_2.setMovie(self.movie1)
        timer1 = QtCore.QTimer(self)
        self.movie1.start()
        timer1.singleShot(4000, self.stopanimate)

    def centerOnScreen(self):
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move((resolution.width() // 2) - (self.frameSize().width() // 2),
                  (resolution.height() // 2) - (self.frameSize().height() // 2))

    def stopanimate(self):
        with open('localname.json') as f:
            details = json.load(f)
            if details['firsttime'] == 1:
                self.window =secondwin()
                self.window.show()
                self.close()
            else:
                self.win=firstwinshow()
                self.close()
                self.win.show()
                self.movie.stop()

if __name__ == "__main__":
    arr=QtWidgets.QApplication(sys.argv)
    pi=UI()
    pi.show()
    arr.exec_()