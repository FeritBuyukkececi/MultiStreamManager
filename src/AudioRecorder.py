import pyaudio
import wave
import threading
import time
import os
import datetime

class AudioRecorder():
    def __init__(self,bitrate=44100,frames_per_buffer=1024,channels=2):
        self.bitrate=bitrate
        self.frames_per_buffer=frames_per_buffer
        self.channels=channels
        self.audio_format=pyaudio.paInt16
        self.is_recording=False
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.audio_format,
                                      channels=self.channels,
                                      rate=self.bitrate,
                                      input=True,
                                      input_device_index=2,
                                      frames_per_buffer = self.frames_per_buffer)
        self.stream.start_stream()
        self.audio_frames = []
        
        info = self.audio.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')

        for i in range(0, numdevices):
            if (self.audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                print("Input Device id ", i, " - ", self.audio.get_device_info_by_host_api_device_index(0, i).get('name'))

    def start_recording(self,output_path):
        if self.is_recording:
            return
        self.output_path=output_path
        self.record_start_time = time.time()
        self.is_recording=True
        self.record_thread = threading.Thread(target=self.run_record, args=())
        self.record_thread.daemon = True
        self.record_thread.start()      

    def run_record(self):
        while self.is_recording:
            try:
                data = self.stream.read(self.frames_per_buffer) 
                self.audio_frames.append(data)
            except:
                pass       
            
    def stop_recording(self):
        if not self.is_recording:
            return
        self.is_recording=False
        print('Audio recording stopped')
        self.record_end_time=time.time()
        self.record_thread.join()  
        print('Audio record thread ended')
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        print('Audio stream terminated')
        
    # Finishes the audio recording therefore the thread too    
    def stop_and_save(self):
        self.stop_recording() #Just to make sure stop_recording is executed  
        
        waveFile = wave.open(self.output_path+'/Audio.wav', 'wb')
        waveFile.setnchannels(self.channels)
        waveFile.setsampwidth(self.audio.get_sample_size(self.audio_format))
        waveFile.setframerate(self.bitrate)
        waveFile.writeframes(b''.join(self.audio_frames))
        waveFile.close()
        print('Audio file saved')        

        