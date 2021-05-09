import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import scipy
from scipy import signal
from scipy.io import wavfile
import pandas as pd
from scipy.signal import savgol_filter


FILENAME = '2021_05_08_203330.903333'


def find_keystrokes_in_amplitude(samples, sample_rate):
    # Find all key downs
    # Might also find some key ups, will be filtered at a later stage
    keystroke_threshold = 2000
    blackout_length = 0.15

    keystrokes = []
    end_of_blackout = 0
    for idx, sample in enumerate(samples):
        current_time = idx / sample_rate

        if current_time > end_of_blackout and sample > keystroke_threshold:
            keystrokes.append(current_time)
            end_of_blackout = current_time + blackout_length

    return keystrokes


def find_keystrokes_in_spectrogram():
    # Find key up and key down in spectrogram
    myfreq = np.max(spectrogram[80:100, :], axis=0)
    myfreq = scipy.signal.medfilt(myfreq, 7)
    myfreq = np.log1p(myfreq) * 1000
    spectrogram_keypress = []
    keypress_threshold = 180
    current_keypress = {
        'state': 'find_start'
    }
    # http://hyperphysics.phy-astr.gsu.edu/hbase/cm.html

    for idx in range(myfreq.shape[0]):
        if current_keypress['state'] == 'find_start':
            if myfreq[idx] > keypress_threshold:
                current_keypress['state'] = 'find_end'
                current_keypress['mx'] = 0
                current_keypress['m'] = 0

        elif current_keypress['state'] == 'find_end':
            if myfreq[idx] > keypress_threshold:
                current_keypress['mx'] += myfreq[idx] * idx
                current_keypress['m'] += myfreq[idx]
            else:
                center_of_mass = current_keypress['mx'] / current_keypress['m']
                spectrogram_keypress.append(center_of_mass)
                current_keypress['state'] = 'find_start'

    print(spectrogram_keypress)


def find_key_down():
    valid_time_range = 0.04
    keystroke_down_offset = -0.03
    keystroke_up_offset = 0.07
    offset_time = 0.0
    keystrokes = []
    current_keystroke = {}

    for idx, logged_keystroke in logged_keystrokes.iterrows():
        if logged_keystroke['direction'] == 'down':
            for audio_timestamp in audio_over_threshold:
                if abs(audio_timestamp - logged_keystroke['timestamp']) < valid_time_range:
                    offset_time = logged_keystroke['timestamp'] - audio_timestamp
                    current_keystroke['down'] = logged_keystroke['timestamp'] - offset_time + keystroke_down_offset
                    break

        elif logged_keystroke['direction'] == 'up':
            current_keystroke['up'] = logged_keystroke['timestamp'] - offset_time + keystroke_up_offset
            current_keystroke['up'] = current_keystroke['down'] + 0.32
            keystrokes.append(current_keystroke)
            current_keystroke = {}


def main():
    # https://stackoverflow.com/questions/44787437/how-to-convert-a-wav-file-to-a-spectrogram-in-python3

    logged_keystrokes = pd.read_csv(f'output/{FILENAME}.csv')
    sample_rate, samples = wavfile.read(f'output/{FILENAME}.wav')

    frequencies, times, spectrogram = signal.spectrogram(samples, fs=sample_rate, nfft=512)

    keystrokes_in_amplitude = find_keystrokes_in_amplitude(samples, sample_rate)
    keystrokes_in_spectrogram = find_keystrokes_in_spectrogram()

    for keypress in keystrokes_in_amplitude:
        plt.plot([keypress*sample_rate, keypress*sample_rate], [0, 10000])

    plt.plot(samples)
    #x = np.arange(0, 250000, 225)
    #plt.plot(x, myfreq[:x.shape[0]])

    """
    plt.pcolormesh(
        times, frequencies, spectrogram,
        norm=colors.LogNorm(vmin=np.min(spectrogram), vmax=np.max(spectrogram))
    )
    """

    plt.show()




    """
    
    
    plt.plot(samples)
    
    for keystroke in keystrokes:
        plt.plot([keystroke['down'] * sample_rate, keystroke['down'] * sample_rate], [5000, -5000], 'r')
        plt.plot([keystroke['up'] * sample_rate, keystroke['up'] * sample_rate], [5000, -5000], 'g')
    
    plt.show()
    
    
    """


    """
    
    print(sample_rate)
    frequencies, times, spectrogram = signal.spectrogram(samples, fs=sample_rate, nfft=512)
    
    plt.pcolormesh(
        times, frequencies, spectrogram,
        norm=colors.LogNorm(vmin=np.min(spectrogram), vmax=np.max(spectrogram))
    )
    
    
    
    
    keystrokes = pd.read_csv('output/2021_05_08_190842.648375_keystroke_recording.csv')
    for idx, keystroke in keystrokes.iterrows():
        timestamp = keystroke['timestamp']
        key = keystroke['key']
        direction = keystroke['direction']
    
        if direction == "up":
            color = 'g'
        elif direction == 'down':
            color = 'r'
        else:
            color = 'b'
    
        plt.plot([timestamp, timestamp], [0.0, 20000.0], color)
    
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    #plt.yscale('log')
    plt.ylim(top=sample_rate / 2)
    plt.ylim(bottom=1)
    plt.show()
    
    #plt.savefig('output/spectrogram.png')
    """


if __name__ == '__main__':
    main()
