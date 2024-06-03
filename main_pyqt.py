from src.ADB import AdbThread
from src.Webcam import WebcamThread 
from src.AudioRecorder import AudioRecorder 
from src.WindowRecorder import WindowRecorder
from PIL import ImageTk as PIL_ImageTk
import tkinter as tk
import tkinter.messagebox
from datetime import datetime
import time
import threading
import cv2
import sys
import os
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QVBoxLayout, QHBoxLayout,QMessageBox,QPushButton
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap 
from PyQt5.QtCore import QTimer, QTime, Qt

def returnCameraIndexes():
    # checks the first 10 indexes.
    index = 0
    arr = []
    i = 10
    while i > 0:
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if cap.read()[0]:
            arr.append(index)
            cap.release()
        index += 1
        i -= 1
    return arr
                
class MyApp(QWidget):
    def __init__(self,app):
        super(MyApp, self).__init__()
        print(returnCameraIndexes())

        self.app=app
        self.title = 'Camera'
        self.is_recording=False
        self.session_date=datetime.now().strftime('%Y%m%d_%H%M%S')
        self.initUI(app)
        self.window_recorder=WindowRecorder(self.app.primaryScreen(),self.winId())
        self.audio_recorder=AudioRecorder()
        # creating a timer object
        self.timer = QTimer(self)
        # adding action to timer
        self.timer.timeout.connect(self.showTime)
        # update the timer every second
        self.timer.start(1000)
        
        
    # method called by timer
    def showTime(self):
        current_time = QTime.currentTime()
        label_time = current_time.toString('hh:mm:ss')
        self.timer_label.setText(label_time)

    def closeEvent(self,event):
        print('On close',flush=True)
        self.timer.stop()
        print('Timer stopped',flush=True)
        print('Ending threads',flush=True)
        self.th0.stop()
        self.th1.stop()
        self.th2.stop()
        self.th0.quit()
        self.th1.quit()
        self.th2.quit()
        self.th0.wait()
        self.th1.wait()
        self.th2.wait()
        print('Threads terminated',flush=True)
        event.accept()
        print('Window closed')
     
    def record_button_on_click(self):
        if self.is_recording==False:
            self.is_recording=True
            self.record_button.setEnabled(False)
            if not os.path.isdir(self.session_date):
                os.mkdir(self.session_date)
            self.audio_recorder.start_recording(self.session_date)
            self.window_recorder.start_recording(self.session_date)
            self.record_button.setText(f'End recording')
            self.record_button.setEnabled(True)
        else:
            self.is_recording=False
            self.record_button.setEnabled(False)
            self.record_button.setText('Processing, please wait')
            self.audio_recorder.stop_recording()
            self.window_recorder.stop_recording()
            self.audio_recorder.stop_and_save()
            self.window_recorder.stop_and_save()
            self.window_recorder.mux()
            self.record_button.setText('Processing complete, now you can quit')
    
    def ss_button_on_click(self):
        if not os.path.isdir(self.session_date):
            os.mkdir(self.session_date)
        screen=self.app.primaryScreen()
        p=screen.grabWindow(self.winId())
        p.save(f"{self.session_date}/SS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg", 'jpg')
    
    def initUI(self,app):
        top_layout=QVBoxLayout()
        button_panel=QHBoxLayout()
        window_layout=QHBoxLayout()
        
        self.timer_label = QLabel('Time')
        self.timer_label.setStyleSheet("padding: 5px;font-size: 36px");
        button_panel.addWidget(self.timer_label)
        
        self.record_button = QPushButton('Start record')
        self.record_button.setStyleSheet("padding: 5px;font-size: 36px");
        self.record_button.clicked.connect(self.record_button_on_click)
        button_panel.addWidget(self.record_button)
                
        self.ss_button = QPushButton('Take snapshot')
        self.ss_button.setStyleSheet("padding: 5px;font-size: 36px");
        self.ss_button.clicked.connect(self.ss_button_on_click)
        button_panel.addWidget(self.ss_button)    
        
        left = QVBoxLayout()
        self.label0 = QLabel(self)
        left.addWidget(self.label0)
        
        right = QVBoxLayout()
        self.label1 = QLabel(self)
        right.addWidget(self.label1)
        self.label2 = QLabel(self)
        right.addWidget(self.label2)  
        
        window_layout.addLayout(left)
        window_layout.addLayout(right)
        
        top_layout.addLayout(button_panel)
        top_layout.addLayout(window_layout)
        self.setLayout(top_layout)

        #self.th0 = WebcamThread(0,480,320)#295,640)
        self.th0 = AdbThread(0,295,640)
        self.th0.changePixmap.connect(self.setImage0)
        #self.th0.changePixmap.connect(self.setImage1)
        #self.th0.changePixmap.connect(self.setImage2)
        self.th0.start()
        
        self.th1 = WebcamThread(0,480,320)
        self.th1.changePixmap.connect(self.setImage1)
        self.th1.start()
        
        self.th2 = WebcamThread(2,480,320)
        self.th2.changePixmap.connect(self.setImage2)
        self.th2.start()

        self.show()
        

    @pyqtSlot(QImage)
    def setImage0(self, image):
        self.label0.setPixmap(QPixmap.fromImage(image))
    def setImage1(self, image):
        self.label1.setPixmap(QPixmap.fromImage(image))
    def setImage2(self, image):
        self.label2.setPixmap(QPixmap.fromImage(image))

if __name__ == '__main__':
 #   sm=init_stream_manager()
    app = QApplication(sys.argv)
    ex = MyApp(app)
    sys.exit(app.exec_())
