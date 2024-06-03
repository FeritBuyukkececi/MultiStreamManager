from src.WindowRecorder import WindowRecorder
from src.AudioRecorder import AudioRecorder
from src.Audio import Audio
import os
from datetime import datetime
import cv2

class StreamManager():
    def __init__(self,screen,winId):
        self.video_stream=WindowRecorder(screen,winId)
        self.audio_stream=AudioRecorder()
        self.is_recording=False
    
    def start_recording(self,session_date):
        if self.is_recording:
            return
        if not os.path.isdir(self.output_path):
            os.mkdir(self.output_path)
    
    def register_stream(self,stream_class,stream_type,**kwargs):
        stream=stream_class(**kwargs)
        args=kwargs
        if stream_type=='video':
            self.video_streams.update({args['stream_name']:stream})
        elif stream_type=='audio':
            self.audio_streams.update({args['stream_name']:stream})
        else:
            raise('No such stream type')

    def set_video_record_size(self,stream_name,frame_size):
        self.record_frame_sizes.update({stream_name:frame_size})
        
    def start(self):
        for stream in self.video_streams:
            self.video_streams[stream].start()
        for stream in self.audio_streams:
            self.audio_streams[stream].start()
            
    def start_recording(self,output_path,video_format='avi',fourcc='DIVX'):
        if self.is_recording:
            return
        self.is_recording=True
        if not os.path.isdir(output_path):
            os.mkdir(output_path)
        for stream in self.video_streams:
            self.video_streams[stream].start_recording(output_path,self.record_frame_sizes[stream],video_format,fourcc)
        for stream in self.audio_streams:
            self.audio_streams[stream].start_recording(output_path)

    def get_current_frame(self,stream,frame_size):
        return self.video_streams[stream].get_current_frame(frame_size)
    
    def take_screenshots(self,output_path):
        if not os.path.isdir(output_path):
            os.mkdir(output_path)
        folder_path=f'{output_path}\\screenshots'
        if not os.path.isdir(folder_path):
            os.mkdir(folder_path)
        ss_name=datetime.now().strftime('%Y%m%d_%H%M%S')
        for stream in self.video_streams:
            frame=self.get_current_frame(stream,self.record_frame_sizes[stream])    
            if frame is not None:
                print(f'{folder_path}/{ss_name}_{stream}.png')
                cv2.imwrite(f'{folder_path}/{ss_name}_{stream}.png',frame)
            
    def stop_recording(self):
        if not self.is_recording:
            return
        self.is_recording=False
        print('stop video streams')
        for stream in self.video_streams:
            self.video_streams[stream].stop_recording()
        print('stop audio streams')
        for stream in self.audio_streams:
            self.audio_streams[stream].stop_recording()
        print('readjust video fps')
        for stream in self.video_streams:
            self.video_streams[stream].readjust_fps()
        print('ended')
            
    def stop(self):
        for stream in self.video_streams:
            self.video_streams[stream].stop()
        for stream in self.audio_streams:
            self.audio_streams[stream].stop()