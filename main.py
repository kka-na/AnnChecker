'''
1) when resource modified
pyrcc5 -o resources_rc.py resources.qrc
2) when ui modified
pyuic5 -o mainwindow.py mainwindow.ui
'''

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import shutil
import os
from pathlib import Path

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from mainwindow import Ui_MainWindow

import getdata

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.getData = None
        self.set_connect()

    def setting(self):
        tasks = ['2D Object Detection', '2D Semantic Segmentation', '3D Object Detection']
        item, ok = QInputDialog().getItem(self, "Select Task", "Task:", tasks, 0, False)
        if ok:
            if item == tasks[0]:
                self.task = 0
                self.getData = getdata.GetData()
                self.getData.task = self.task
                self.getData.send_img.connect(self.disp_img)


    def set_connect(self):
        self.ui.settingButton.clicked.connect(self.setting)
        self.ui.dataButton.clicked.connect(self.data)

    def data(self):
        path = str(QFileDialog.getExistingDirectory(None, 'Select Directory of top of datasets', QDir.currentPath(),
                                                    QFileDialog.ShowDirsOnly))
        self.getData.set_path(path)

    def clear_layout(self, layout):
        for i in range(layout.count()):
            layout.itemAt(i).widget().close()
            self.layout.takeAt(i)
  
    def disp_img(self, _object):
        self.ui.label.setPixmap(
            QPixmap.fromImage(_object).scaled(self.ui.label.width(), self.ui.label.height(), aspectRatioMode=0))
        QCoreApplication.processEvents()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
