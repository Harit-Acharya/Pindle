import sys
from keyword import iskeyword

from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QCheckBox, QScrollArea, QComboBox, QErrorMessage, \
    QSizeGrip, QLabel
import json
import secondpage
import sip


class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        uic.loadUi("categorization.ui", self)
        self.setFixedSize(1020,850)
        self.setWindowTitle("Pindle Categorizer")
        self.setWindowIcon(QIcon("icon.png"))
        self.categories, self.extensions = self.file_to_dict()
        self.verticallayoutlist = {"Documents":"verticalLayout",
                             "Pictures":"verticalLayout_2",
                             "Musics":"verticalLayout_3",
                             "Videos":"verticalLayout_4"}

        self.error_dialog = QErrorMessage()
        self.update_scrollview()

        self.Documents = self.findChild(QCheckBox,"Documents")
        self.Musics = self.findChild(QCheckBox, "Musics")
        self.Pictures = self.findChild(QCheckBox, "Pictures")
        self.Videos = self.findChild(QCheckBox, "Videos")

        self.type = self.findChild(QComboBox,"comboBox")
        self.secondpage = self.findChild(QPushButton,"pushButton_4")
        self.add = self.findChild(QPushButton, "pushButton_2")
        self.remove = self.findChild(QPushButton, "pushButton_3")
        self.secondpage.clicked.connect(self.next)
        self.add.clicked.connect(self.additem)
        self.remove.clicked.connect(self.removeitem)

    def next(self):
        self.window = secondpage.UI()
        self.window.show()
        self.save_config()
        self.hide()

    def additem(self):
        value = self.lineEdit.text()
        if value[0] == '.': value = value[1:]
        if (not value in self.extensions[self.type.currentText()].keys()) and (not iskeyword(value)):
            value = self.lineEdit.text()
            setattr(self, value, QCheckBox(value))
            eval('self.'+value).setChecked(True)
            eval('self.'+value).setCheckable(True)
            eval('self.'+self.verticallayoutlist[self.type.currentText()]).addWidget(eval('self.'+value))
            self.setObjectName(value)
            self.extensions[self.type.currentText()][value] = 1
        else:
            self.error_dialog.showMessage('Extension is already in list or this is python keyword')

    def removeitem(self):
        value = self.lineEdit.text()
        if value[0] == '.': value = value[1:]
        if not value in self.extensions[self.type.currentText()].keys():
            self.error_dialog.showMessage('Extension n is not in list!!')
        else:
            eval('self.' + self.verticallayoutlist[self.type.currentText()]).removeWidget(eval('self.' + value))
            sip.delete(eval('self.'+value))
            vars()[eval("self."+value)]=None
            del self.extensions[self.type.currentText()][value]

    def update_scrollview(self):
        for key,value in self.extensions.items():
            for name,state in value.items():
                setattr(self, name, QCheckBox(name))
                if state: eval('self.'+name).setChecked(True)
                else: eval('self.'+name).setChecked(False)
                eval('self.'+self.verticallayoutlist[key]).addWidget(eval('self.'+name))
                eval('self.' + name).setCheckable(True)
                self.setObjectName(name)

        for key,state in self.categories.items():
            if state: eval('self.' + key).setChecked(True)
            else: eval('self.' + key).setChecked(False)
            eval('self.' + key).setCheckable(True)

    def file_to_dict(self):
        with open('category_settings.json') as f:
            categories = json.load(f)

        with open('extension_settings.json') as f:
            extensions = json.load(f)

        return categories,extensions

    def save_config(self):
        for key,value in self.extensions.items():
            for name,state in value.items():
                check = eval('self.' + name).isChecked()
                if check == False:
                    self.extensions[key][name] = 0
                else:
                    self.extensions[key][name] = 1

        self.categories['Documents'] = int(self.Documents.isChecked())
        self.categories['Pictures'] = int(self.Pictures.isChecked())
        self.categories['Musics'] = int(self.Musics.isChecked())
        self.categories['Videos'] = int(self.Videos.isChecked())

        with open('category_settings.json', 'w+') as json_file:
            json.dump(self.categories, json_file)

        with open('extension_settings.json', 'w+') as json_file:
            json.dump(self.extensions, json_file)


if "__main__" == __name__:
    app = QApplication(sys.argv)
    window = UI()
    window.show()
    app.exec_()