#!/usr/bin/python3
from random import randint
from PyQt5 import QtWidgets,uic,QtCore,QtGui
from PyQt5.QtGui import QMovie, QIcon
import sys,json
import onedrive_auth
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QPushButton, QLabel, QErrorMessage, QGroupBox,QDesktopWidget
from Google import Create_Service
import time
import onedrive,googledrive
from userstat2 import UI
import os

counter=0
cloudcounter=0
cloudcounter_2=0

def getdetails(errorbox):
    try:
        with open('/etc/Pindle/Syncer/localname.json') as f:
            details = json.load(f)
            return details
    except:
        errorbox.showMessage("localname.json file not found")
        time.sleep(10)
        exit(0)

class secondwin(QtWidgets.QMainWindow):
    def __init__(self):
        super(secondwin,self).__init__()
        uic.loadUi('/etc/Pindle/Syncer/firstwindow1.ui', self)
        self.error_dialog = QErrorMessage()
        self.setWindowIcon(QIcon("/usr/share/pixmaps/Pindle/Syncer/sync.png"))
        self.setWindowTitle("Pindle Syncer")
        self.setGeometry(0, 0, 840, 700)
        self.centerOnScreen()
        self.details = getdetails(self.error_dialog)
        self.named2 = self.details["device2"]
        self.named = self.details["localname"]
        self.mailid = self.details["mailid"]
        self.instdir = self.details["insdir"]
        self.check()
        self.gdrive = self.findChild(QPushButton,"pushButton")
        self.onedrive = self.findChild(QPushButton,"pushButton_2")
        self.logout = self.findChild(QPushButton,"pushButton_6")
        self.next = self.findChild(QPushButton,"pushButton_7")
        self.name = self.findChild(QPushButton,"pushButton_5")
        self.mail = self.findChild(QPushButton,"pushButton_4")
        self.name2 = self.findChild(QPushButton,"pushButton_9")
       # self.setup = self.findChild(QPushButton,"pushButton_8")
        self.image = self.findChild(QLabel,"label")
        self.image.setPixmap(QPixmap("usr/share/pixmaps/Pindle/Syncer/image{}.png".format(randint(1,9))))
        self.name2.setText(self.named2)
        self.name.setText(self.named)
        self.mail.setText(self.mailid)
        self.next.clicked.connect(self.nest)
        self.logout.clicked.connect(self.logut)

    def trying(self):
        self.label_2.setGeometry(QtCore.QRect(260, 240, 400, 180))
        self.label_2.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.movie=QMovie('/usr/share/pixmaps/Pindle/Syncer/waited.gif')
        self.label_2.setMovie(self.movie)
        timer4=QtCore.QTimer(self)
        self.movie.start()
        timer4.singleShot(20000,self.stopanimation)

    def centerOnScreen(self):
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move((resolution.width() // 2) - (self.frameSize().width() // 2),
                  (resolution.height() // 2) - (self.frameSize().height()// 2))

    def stopanimation(self):
        self.display = UI()
        self.hide()
        self.display.show()
        self.movie.stop()
    def loadsession(self):
        domain = self.mailid[self.mailid.index('@') + 1:]
        if domain != "gmail.com":
            try:
                api = onedrive_auth.LoadSession()
                self.ctotal = api.drive.get().quota.total/(2**30)
                self.cused = api.drive.get().quota.used/(2**30)
                onedrive.download(api, "pindleconfig.json", os.path.join(self.instdir,"pindleconfig.json"), 'file')
            except:
                self.error_dialog.showMessage("OOPS!! Something is Wrong!!\nPlease check your connection")
        else:
            try:
                CLIENT_SECRET_FILE = '/etc/Pindle/Syncer/credentials.json'
                API_NAME = 'drive'
                API_VERSION = 'v3'
                SCOPES = ['https://www.googleapis.com/auth/drive']
                self.api = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
                googledrive.download(self.api, "pindleconfig.json", self.instdir, 'file')
                response = self.api.about().get(fields='*').execute()
                for k, v in response.get('storageQuota').items():
                    if 'limit' == k:
                        self.ctotal = int(v)/(1024**3)
                    if 'usage' == k:
                        self.cused = int(v)/(1024**3)
                        break
            except:
                self.error_dialog.showMessage("OOPS!! Something is Wrong!!\nPlease check your connection")
        self.cused=round(self.cused,2)
        self.ctotal=round(self.ctotal,2)

    def check(self):
        self.loadsession()
        with open(os.path.join(self.instdir,'pindleconfig.json'), 'r') as f:
            self.config = json.load(f)
        self.device1_tsize = (self.config['device1']['size'][0])/(1024**3)
        self.device1_tused = (self.config['device1']['size'][1])/(1024**3)
        self.device1_tused = round(self.device1_tused,2)
        self.device1_tsize = round(self.device1_tsize,2)
        self.cpuprogress_a()
        self.cloudprogress_a()

        if self.config['issetup'] != 0:
            self.device2_tsize = self.config['device2']['size'][0]/(1024**3)
            self.device2_tused = self.config['device2']['size'][1]/(1024**3)
            self.device2_tused=round(self.device2_tused, 2)
            self.device2_tsize=round(self.device2_tsize,2)
            self.cloudprogress2_a()
            #3rd progress bar
        else:
            self.cloudprogress2_c(0)
            self.cloud2_total.setText("Unavailable")
            self.cloud2_used.setText("0%")

    def cpuprogress_a(self):
        self.cpuprogress_c(0)
        self.timer=QtCore.QTimer()
        self.timer.timeout.connect(self.cpuprogress_b)
        self.timer.start(30)

    def cpuprogress_b(self):                   #for 1st pg bar
        global counter
        value=counter
        cputotal=self.device1_tsize
        cpuused=self.device1_tused     #set your progress value here
        cpupercentage=(cpuused*100)/cputotal
        self.cpuprogress_c(value)
        self.cpu_used.setText(str(value)+"%")
        self.cpu_total.setText(str(cputotal)+"GB")
        if int(value)==int(cpupercentage):
            self.timer.stop()

    def cpuprogress_c(self,value):   #for first pg bar
        global counter
        styleSheet="""
        QFrame{
        border-radius:110%;
        background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{STOP_1} rgba(255, 255, 255, 0), stop:{STOP_2} rgba(85, 170, 255, 255));
        }  """     
        progress=(100-value)/100.0
        stop_1=str(progress-0.001) 
        stop_2=str(progress)
        counter+=0.5
        newStylesheet=styleSheet.replace("{STOP_1}",stop_1).replace("{STOP_2}",stop_2) 
        
        self.cpucircularprogress_a.setStyleSheet(newStylesheet)
     
    def cloudprogress_a(self):
        self.cloudprogress_c(0)
        self.timer_2=QtCore.QTimer()
        self.timer_2.timeout.connect(self.cloudprogress_b)
        self.timer_2.start(30)

    def cloudprogress_b(self):                   #for 1st pg bar
        global cloudcounter
        cloudvalue=cloudcounter
        cloudtotal=self.ctotal
        cloudused=self.cused     #set your progress value here
        cloudpercentage=(cloudused*100)/cloudtotal
        self.cloudprogress_c(cloudvalue)
        self.cloud_used.setText(str(cloudvalue)+"%")
        self.cloud_total.setText(str(cloudtotal)+"GB")
        if int(cloudvalue)==int(cloudpercentage):
            self.timer_2.stop()

    def cloudprogress_c(self,cloudvalue):   #for first pg bar
        global cloudcounter
        styleSheet="""
        QFrame{
        border-radius:110%;
        background-color:qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{STOl_1} rgba(255, 255, 255, 0), stop:{STOl_2} rgba(85, 255, 127, 255));
        }"""
        cloudprogress=(100-cloudvalue)/100.0
        cstop_1=str(cloudprogress-0.001) 
        cstop_2=str(cloudprogress)
        cloudcounter+=0.5
        cnewStylesheet=styleSheet.replace("{STOl_1}",cstop_1).replace("{STOl_2}",cstop_2)
        self.cloudcircularprogress_a.setStyleSheet(cnewStylesheet)
    
    def cloudprogress2_a(self):
        self.cloudprogress2_c(0)
        self.timer_3=QtCore.QTimer()
        self.timer_3.timeout.connect(self.cloudprogress2_b)
        self.timer_3.start(30)

    def cloudprogress2_b(self):                   #for 1st pg bar
        global cloudcounter_2
        cloudvalue_2=cloudcounter_2
        cloudused_2=self.device2_tused         #set your progress value here 
        cloudtotal_2=self.device2_tsize
        cloudpercentage_2=(cloudused_2*100)/cloudtotal_2
        self.cloudprogress2_c(cloudvalue_2)
        self.cloud2_used.setText(str(cloudvalue_2)+"%")
        self.cloud2_total.setText(str(cloudtotal_2)+"GB")
        if int(cloudvalue_2)==int(cloudpercentage_2):
            self.timer_3.stop()

    def cloudprogress2_c(self,cloudvalue_2):   #for first pg bar
        global cloudcounter_2
        styleSheet="""
        QFrame{
        border-radius:110%;
        background-color:qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{STOll_1} rgba(255, 255, 255, 0), stop:{STOll_2} rgba(255, 0, 127, 255));
        }"""
        cloudprogress_2=(100-cloudvalue_2)/100.0
        ccstop_1=str(cloudprogress_2-0.001) 
        ccstop_2=str(cloudprogress_2)
        cloudcounter_2+=0.5
        ccnewStylesheet=styleSheet.replace("{STOll_1}",ccstop_1).replace("{STOll_2}",ccstop_2)
        self.cloudcircularprogress1_a.setStyleSheet(ccnewStylesheet)

    def nest(self):
        self.trying()

    def logut(self):
        from firstwindow import firstwinshow
        try:
            if self.domain != "gmail.com":
                onedrive.delete(self.api,'pindleconfig.json')
                onedrive.delete(self.api,'{}_changes.json'.format(self.config["device1"]["name"]))
                onedrive.delete(self.api, '{}_changes.json'.format(self.config["device2"]["name"]))
            else:
                googledrive.delete(self.api, 'pindleconfig.json','file')
                googledrive.delete(self.api, '{}_changes.json','file'.format(self.config["device1"]["name"]))
                googledrive.delete(self.api, '{}_changes.json','file'.format(self.config["device2"]["name"]))
            self.details = {"localname": "", "mailid": "", "firsttime": 0, "insdir": "", "device2": ""}
            os.system("sudo rm -f {}".format(os.path.join(self.instdir,"paths_settings.json")))
            os.system("sudo rm -f {}".format(os.path.join(self.instdir,"pindleconfig.json")))
            os.system("sudo systemctl stop syncer_local")
            os.system("sudo systemctl disable syncer_local")
            os.system("sudo systemctl stop syncer_remote")
            os.system("sudo systemctl disable syncer_remote")
            with open(os.path.join(self.instdir,'localname.json'), 'w+') as f:
                json.dump(self.details, f)
            self.dis=firstwinshow()
            self.dis.show()
            self.hide()
        except:
            pass

if __name__ == "__main__":
    arr=QtWidgets.QApplication(sys.argv)
    pi=secondwin()
    pi.show()
    arr.exec_()