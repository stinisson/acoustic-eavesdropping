import pyaudio
import wave
import threading


class Audio:
    def __init__(self):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.RECORD_SECONDS = 5
        self.p = pyaudio.PyAudio()
        self.frames = []
        self.recording_running = False
        self.stream = None
        self.thread = None

    def start_recording(self):
        print("* recording")

        self.stream = self.p.open(format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  input=True,
                                  frames_per_buffer=self.CHUNK)
        self.recording_running = True

        self.thread = threading.Thread(target=self.audio_recording)
        self.thread.start()

    def audio_recording(self):
        while self.recording_running:
            data = self.stream.read(self.CHUNK)
            self.frames.append(data)

    def stop_recording(self, time_string):
        print("* done recording")

        self.recording_running = False

        # wait until recording is stopped and the thread is finished
        self.thread.join()

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

        wf = wave.open("output/" + time_string + ".wav", 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()
