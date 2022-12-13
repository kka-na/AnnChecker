'''
1) when resource modified
pyrcc5 -o resources_rc.py resources.qrc
2) when ui modified
pyuic5 -o mainwindow.py mainwindow.ui
'''

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from mainwindow import Ui_MainWindow


import getdata
import vtkwidget


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.getData = None
        self.set_connect()
        self.vtkWidget = None
        self.imgLabel = None

    def setting(self):
        tasks = ['2D Object Detection',
                 '2D Semantic Segmentation', '3D Object Detection']
        item, ok = QInputDialog().getItem(self, "Select Task", "Task:", tasks, 0, False)
        if ok:
            if item == tasks[0]:
                self.task = 0
                self.getData = getdata.GetData()
                self.getData.task = self.task
                self.getData.send_img.connect(self.disp_img)
                self.set_layout()
            elif item == tasks[2]:
                self.task = 2
                self.getData = getdata.GetData()
                self.getData.task = self.task
                self.getData.send_bin.connect(self.disp_bin)
                self.vtkWidget = vtkwidget.VTKWidget()
                self.set_layout()

    def set_connect(self):
        self.ui.settingButton.clicked.connect(self.setting)
        self.ui.dataButton.clicked.connect(self.data)
        self.ui.upButton.clicked.connect(self.go_up)
        self.ui.downButton.clicked.connect(self.go_down)

    def clear_layout(self, layout):
        for i in range(layout.count()):
            layout.itemAt(i).widget().close()
            layout.takeAt(i)

    def set_layout(self):
        if self.task == 0:
            self.clear_layout(self.ui.dataLayout)
            self.imgLabel = QLabel()
            self.imgLabel.setAlignment(Qt.AlignCenter)
            self.ui.dataLayout.addWidget(self.imgLabel)
        elif self.task == 2:
            self.clear_layout(self.ui.dataLayout)
            self.ui.dataLayout.addWidget(self.vtkWidget.vtkWidget)
            self.vtkWidget.init()

    def data(self):
        path = str(QFileDialog.getExistingDirectory(None, 'Select Directory of top of datasets', QDir.currentPath(),
                                                    QFileDialog.ShowDirsOnly))
        self.getData.set_path(path)

    def disp_img(self, _object):
        self.imgLabel.setPixmap(
            QPixmap.fromImage(_object).scaled(self.imgLabel.width(), self.imgLabel.height(), aspectRatioMode=1))
        QCoreApplication.processEvents()

    def disp_bin(self, _bin, _label):
        self.vtkWidget.set_point_cloud(_bin, _label)

    def go_up(self):
        self.getData.move(-1)

    def go_down(self):
        self.getData.move(1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
