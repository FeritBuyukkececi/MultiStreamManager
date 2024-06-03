import cv2
import time
import imutils
import time
import threading
import subprocess
import numpy as np
import os
from datetime import datetime
from PIL import Image as PIL_Image
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QVBoxLayout, QHBoxLayout,QMessageBox,QPushButton
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap 

class WebcamThread(QThread):
    changePixmap = pyqtSignal(QImage)
    def __init__(self,device_id,width,height):
        print(f'Initializing WebcamThread for device_id:{device_id}', flush=True)
        super(QThread, self).__init__()
        print(f'QThread initialized for WebcamThread for device_id:{device_id}', flush=True)
        self.device_id=device_id
        self.video_capture = cv2.VideoCapture(self.device_id, cv2.CAP_DSHOW)
        self.width=width
        self.height=height
        self.is_running=True
        print(f'Webcam is initialized with device_id:{device_id} and size:{width, height}', flush=True)
    def run(self):
        while self.is_running:
            self.frame=None
            try:
                ret,frame = self.video_capture.read()
                #frame=cv2.resize(frame,(self.width,self.height),interpolation=cv2.INTER_AREA)
                self.frame=frame.copy()
            except:
                pass
            if self.frame is not None:
                rgbimage = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbimage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbimage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                image=convertToQtFormat.scaled(self.width,self.height)#,Qt.KeepAspectRatio) 
                self.changePixmap.emit(image)
            time.sleep(0.03)
    def stop(self):
        self.is_running=False
        
        