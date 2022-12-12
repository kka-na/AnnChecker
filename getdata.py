import os
from pathlib import Path
from operator import itemgetter


from PyQt5.QtCore import *
from PyQt5.QtGui import *


class GetData(QObject):
    def __init__(self):
        super(GetData, self).__init__()
        self.task = None
        self.base_path = ""
        self.data_paths = []
        self.data_len = 0

    def set_path(self, path):
        self.base_path = str(path)
        self.data_paths = []
        self.now_idx = 0
        if self.task == 0:
            self.data_paths.extend(os.path.basename(x)
                                   for x in sorted(Path(path).glob("*.jpg")))
            self.data_paths.extend(os.path.basename(x)
                                   for x in sorted(Path(path).glob("*.png")))

        self.data_len = len(self.data_paths)
        fr = open(str(path + "/classes.txt"))
        lines = fr.readlines()
        self.class_list = []
        for line in lines:
            self.class_list.append(line)

        self.send_datum()

    send_img = pyqtSignal(object)

    def send_datum(self):
        if self.task == 0:
            self.set_img()

    def set_img(self):
        data_path = self.base_path+"/{}".format(self.data_paths[self.now_idx])
        text_path = "{}.txt".format(data_path.split('.')[0])
        if self.task == 0:
            img = QImage(data_path)

        self.width = img.width()
        self.height = img.height()

        bboxes = self.get_label_list(text_path)
        img = self.draw_boxes(img, bboxes)
        self.send_img.emit(img)

    def get_label_list(self, file):
        bboxes = []
        if os.path.isfile(file):
            fr = open(file)
            lines = fr.readlines()
            for line in lines:
                val = line.split()
                if len(val) == 5:
                    conf = 1.0
                    calc_box = self.calc_boxes(val[1:])
                    _center = [float(val[1]) * self.width,
                               float(val[2]) * self.height]
                else:
                    conf = float(val[1])
                    calc_box = self.calc_boxes(val[2:])
                    _center = [float(val[2]) * self.width,
                               float(val[3]) * self.height]
                bbox = {'cls': val[0], 'conf': conf, 'size': calc_box[0:2],
                        'bbox': calc_box[2:], 'center': _center}
                bboxes.append(bbox)

        bboxes = sorted(bboxes, key=itemgetter('conf'), reverse=True)
        return bboxes

    def calc_boxes(self, _object):
        lx = (float(_object[0]) - float(_object[2]) / 2) * self.width
        ly = (float(_object[1]) - float(_object[3]) / 2) * self.height
        rx = (float(_object[0]) + float(_object[2]) / 2) * self.width
        ry = (float(_object[1]) + float(_object[3]) / 2) * self.height
        return [float(_object[2]) * self.width, float(_object[3]) * self.height, lx, ly, rx, ry]

    def draw_boxes(self, img, bboxes):
        if len(bboxes) > 0:
            painter = QPainter(img)
            f = QFont("Helvetica [Cronyx]", img.height() / 30)
            for bbox in bboxes:
                pen = self.get_bbox_pen(int(bbox['cls']))
                painter.setPen(pen)
                qrect = QRect(bbox['bbox'][0], bbox['bbox']
                              [1], bbox['size'][0], bbox['size'][1])
                painter.drawRect(qrect)
                painter.setFont(f)
                class_name = self.class_list[int(bbox['cls'])]
                painter.drawText(
                    bbox['bbox'][0], bbox['bbox'][1] - 10, class_name)
            painter.end()
        return img

    def get_bbox_pen(self, _object):
        pen = QPen()
        pen.setWidth(5)
        if _object % 6 == 0:
            qb = QBrush(QColor('yellow'))
            pen.setBrush(qb)
        elif _object % 6 == 1:
            qb = QBrush(QColor('magenta'))
            pen.setBrush(qb)
        elif _object % 6 == 2:
            qb = QBrush(QColor('cyan'))
            pen.setBrush(qb)
        elif _object % 6 == 3:
            qb = QBrush(QColor('red'))
            pen.setBrush(qb)
        elif _object % 6 == 4:
            qb = QBrush(QColor('blue'))
            pen.setBrush(qb)
        else:
            qb = QBrush(QColor('green'))
            pen.setBrush(qb)
        return pen

    def move(self, idx):
        self.now_idx += idx
        if self.now_idx < 0:
            self.now_idx = 0
        elif self.now_idx > self.data_len - 1:
            self.now_idx = self.data_len - 1

        self.send_datum()
