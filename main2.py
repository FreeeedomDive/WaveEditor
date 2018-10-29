import wave_file
import numpy as np

TYPES = {
    1: np.int8,
    2: np.int16,
    4: np.int32
}


wav = wave_file.Wave("12 - Opshop - Nothing Can Wait.wav")

wav.reverse()

wave_file.create_file("result2.wav", wav)
