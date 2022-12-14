# Annotation Checker

Simple GUI based on PyQT that can check Annotation information of Dataset such as 2D Object Detection and 3D Object Detection.

### Installation

```
git clone https://github.com/kka-na/AnnChecker.git
cd AnnChecker

# If pyrcc5 not found,
sudo apt-get install pyqt5-dev-tools

# for use resource
pyrcc5 -o resources_rc.py resources.qrc 

# linking with ui file
pyuic5 -o mainwindow.py mainwindow.ui

# excution
python3 main.py
```

### Target folder structure

image or pointcloud and label structured with same file name 

    2D Object Detection ( YOLO Format )
    ├── image.jpg ( / png )
    ├── label.txt 
    └── classes.txt 

    3D Object Detection ( KITTI Format )
    ├── pointcloud.bin
    ├── label.txt 
    └── classes.txt 

### Usage

**2D Object Detection**
<p align="center">
  <img width="800" src="/documentation/test_multiple.gif"/>
</p>

**3D Object Detection**
<p align="center">
  <img width="800" src="/documentation/test_3d.gif"/>
</p>