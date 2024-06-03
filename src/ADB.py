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

class AdbThread(QThread):
    changePixmap = pyqtSignal(QImage)
    def __init__(self,device_id,width,height):
        super(QThread, self).__init__()
        self.device_id=device_id
        self.width=width
        self.height=height
        self.is_running=True
        
    def run(self):
        while self.is_running:
            frame=None
            try:
                pipe = subprocess.Popen('adb shell screencap -p',stdout=subprocess.PIPE, shell=True)
                img_bytes = pipe.stdout.read()
                frame=cv2.imdecode(np.frombuffer(img_bytes.replace(b'\r\n', b'\n'), np.uint8), cv2.IMREAD_COLOR)
                #frame=cv2.resize(self.frame,frame_size,interpolation=cv2.INTER_AREA)
                #frame=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                #frame=PIL_Image.fromarray(frame)
            except:
                pass
            if frame is not None:
            
                rgbimage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbimage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbimage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                image=convertToQtFormat.scaled(self.width,self.height,Qt.KeepAspectRatio) 
                self.changePixmap.emit(image)
            time.sleep(0.03)
            
    def stop(self):
        self.is_running=False