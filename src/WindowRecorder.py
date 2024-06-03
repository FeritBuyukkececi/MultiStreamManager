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

class WindowRecorder():
    def __init__(self,screen,winId,fps=30,video_format='avi',fourcc='DIVX'):
        self.screen=screen
        self.winId=winId
        self.fps=30
        self.is_recording=False
        self.video_format=video_format
        self.fourcc=fourcc        # capture images (with no decrease in speed over time; testing is required)

        
    def start_recording(self,output_path):
        if self.is_recording:
            return
        self.output_path=output_path
        window=self.screen.grabWindow(self.winId)
        self.window_size=(window.width(),window.height())
        self.video_filename = f"{self.output_path}/Video.{self.video_format}"
        #self.video_writer_fourcc = cv2.VideoWriter_fourcc(*self.fourcc)
        self.video_writer_fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
        self.video_writer = cv2.VideoWriter(self.video_filename, self.video_writer_fourcc, self.fps, self.window_size)
        #print(self.window_size)
        self.record_start_time = time.time()
        self.is_recording=True
        self.record_frame_counts=0
        self.frame_duration=int(1000000/self.fps)
        self.record_thread = threading.Thread(target=self.run_record, args=())
        self.record_thread.daemon = True
        self.record_thread.start()  
        
    def run_record(self):
        last_frame_time=datetime.now()
        while self.is_recording:
            current_time=datetime.now()
            if (current_time-last_frame_time).microseconds<self.frame_duration:
                continue
            last_frame_time=current_time
            window=self.screen.grabWindow(self.winId)
            #print(window.width(),window.height())
            if window is not None:
                #print('Frame recorded')
                #window.save(f"{self.output_path}/Window_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg", 'jpg')
                #frame=cv2.resize(self.frame,self.record_frame_size,interpolation=cv2.INTER_AREA)
                #window.save(f"{self.output_path}/{self.record_frame_counts}.jpg", 'jpg')
                img=window.toImage()
                ptr = img.bits()
                ptr.setsize(img.byteCount())
                arr = np.array(ptr).reshape(img.height(), img.width(), 4)
                rgbimage = cv2.cvtColor(arr, cv2.COLOR_RGBA2RGB)
                self.video_writer.write(rgbimage)
                self.record_frame_counts+=1
                
    def stop_recording(self):
        if not self.is_recording:
            return
        self.is_recording=False
        self.record_end_time=time.time()
        self.record_thread.join()
    
    def stop_and_save(self):
        self.stop_recording()
        self.video_writer.release()
        print(self.record_start_time, self.record_end_time, self.record_end_time-self.record_start_time)
        print(self.record_frame_counts)
        print("recording stopped")

    def mux(self):
        actual_fps=np.round(self.record_frame_counts/(self.record_end_time-self.record_start_time),3)
        correction_rate=self.fps/actual_fps
        cmd=f'ffmpeg -i {self.output_path}/Video.avi -i {self.output_path}/Audio.wav -filter_complex "[0:v]setpts=PTS*{correction_rate}[v]" -map "[v]" -map 1:a -shortest {self.output_path}/Output.mp4'
        subprocess.call(cmd, shell=True)
        #os.remove(f'{self.output_path}/Video.avi')
        #os.remove(f'{self.output_path}/Audio.wav')