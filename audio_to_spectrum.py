import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import scipy
from scipy import signal
from scipy.io import wavfile
import pandas as pd


FILENAME = '2021_05_09_122120.809920'


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


def find_keystrokes_in_spectrogram(frequencies, times, spectrogram):
    # Find center of keystrokes, important for key up
    # Will also find key down but will not be used

    # Look at a frequency band where key presses are distinct
    frequency_range = (6500, 8000)
    frequency_idx_start = np.argmax(frequencies > frequency_range[0])
    frequency_idx_end = np.argmax(frequencies > frequency_range[1])

    frequency_band = spectrogram[frequency_idx_start:frequency_idx_end, :]
    amplitudes = np.max(frequency_band, axis=0)
    amplitudes = scipy.signal.medfilt(amplitudes, 7)

    keystrokes = []
    keypress_threshold = 0.15
    current_keypress = {
        'state': 'find_start'
    }

    # Center of mass algorithm to find center of keystroke:
    # http://hyperphysics.phy-astr.gsu.edu/hbase/cm.html

    for idx in range(amplitudes.shape[0]):
        if current_keypress['state'] == 'find_start':
            if amplitudes[idx] > keypress_threshold:
                current_keypress['state'] = 'find_end'
                current_keypress['mx'] = 0
                current_keypress['m'] = 0

        elif current_keypress['state'] == 'find_end':
            if amplitudes[idx] > keypress_threshold:
                current_keypress['mx'] += amplitudes[idx] * idx
                current_keypress['m'] += amplitudes[idx]
            else:
                center_of_mass = math.floor(current_keypress['mx'] / current_keypress['m'])
                keystrokes.append(times[center_of_mass])
                current_keypress['state'] = 'find_start'

    return keystrokes


def match_keystrokes(keystrokes_in_amplitude, keystrokes_in_spectrogram):
    # Match key up from amplitude and key down from spectrogram
    key_up_match_threshold = 0.025
    key_down_match_range = (0.1, 0.3)

    keystrokes = []
    amp_idx, spec_idx = 0, 0

    while amp_idx < len(keystrokes_in_amplitude) and spec_idx + 1 < len(keystrokes_in_spectrogram):
        amp_keystroke_down = keystrokes_in_amplitude[amp_idx]
        spec_keystroke_down = keystrokes_in_spectrogram[spec_idx]
        spec_keystroke_up = keystrokes_in_spectrogram[spec_idx + 1]

        key_up_match = abs(amp_keystroke_down - spec_keystroke_down) < key_up_match_threshold
        key_down_match = key_down_match_range[0] < spec_keystroke_up - amp_keystroke_down < key_down_match_range[1]

        if key_up_match and key_down_match:
            keystrokes.append({
                'down': amp_keystroke_down,
                'up': spec_keystroke_up
            })
            amp_idx += 1
            spec_idx += 2
        else:
            if amp_keystroke_down > spec_keystroke_down:
                spec_idx += 1
            else:
                amp_idx += 1

    return keystrokes


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
    keystrokes_in_spectrogram = find_keystrokes_in_spectrogram(frequencies, times, spectrogram)

    matched_keystrokes = match_keystrokes(keystrokes_in_amplitude, keystrokes_in_spectrogram)

    x = np.arange(0, len(samples) / sample_rate, 1 / sample_rate)
    plt.plot(x, samples / 100)

    # plt.plot(times, amplitudes)

    for keystroke in matched_keystrokes:
        plt.plot([keystroke['down'], keystroke['down']], [0, 100])
        plt.plot([keystroke['up'], keystroke['up']], [0, 50])

    #for keypress in keystrokes_in_amplitude:
    #    plt.plot([keypress, keypress], [0, 100])

    #for keypress in keystrokes_in_spectrogram:
    #    plt.plot([keypress, keypress], [0, 100])
    plt.show()


    """
    for keypress in keystrokes_in_amplitude:
        plt.plot([keypress*sample_rate, keypress*sample_rate], [0, 10000])

    plt.plot(samples)
    #x = np.arange(0, 250000, 225)
    #plt.plot(x, myfreq[:x.shape[0]])

    plt.pcolormesh(
        times, frequencies, spectrogram,
        norm=colors.LogNorm(vmin=np.min(spectrogram), vmax=np.max(spectrogram))
    )

    plt.show()
    """




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
