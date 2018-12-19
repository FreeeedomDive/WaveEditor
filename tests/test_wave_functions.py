import unittest
import numpy as np
from src import wave_file
from src import fragment


class TestWave(unittest.TestCase):

    def test_create_wave(self):
        test_file = wave_file.Wave("../Files/01 Bloody Nose.wav")
        self.assertEqual(test_file.chunkId, "RIFF")
        self.assertEqual(test_file.chunkSize, 44251779)
        self.assertEqual(test_file.format, "WAVE")
        self.assertEqual(test_file.subchunk1Id, "fmt ")
        self.assertEqual(test_file.subchunk1Size, 16)
        self.assertEqual(test_file.audioFormat, 1)
        self.assertEqual(test_file.numChannels, 2)
        self.assertEqual(test_file.sampleRate, 44100)
        self.assertEqual(test_file.byteRate, 176400)
        self.assertEqual(test_file.blockAlign, 4)
        self.assertEqual(test_file.bitsPerSample, 16)
        self.assertEqual(test_file.subchunk2Id, "data")
        self.assertEqual(test_file.subchunk2Size, 44126396)

    def test_get_fragment(self):
        test_file = wave_file.Wave("../Files/01 Bloody Nose.wav")
        fr = fragment.Fragment(test_file.get_fragment(150000, 1500000))
        for channel in fr.channels:
            self.assertEqual(len(channel), 1350000)

    def test_reverse(self):
        test_file = wave_file.Wave("../Files/01 Bloody Nose.wav")
        test_value = (test_file.channels[0][12345],
                      test_file.channels[1][12345])
        test_file.reverse()
        test_reversed_value = \
            (test_file.channels[0][len(test_file.channels[0]) - 12345 - 1],
             test_file.channels[1][len(test_file.channels[1]) - 12345 - 1])
        self.assertEqual(test_value[0], test_reversed_value[0])
        self.assertEqual(test_value[1], test_reversed_value[1])

    def test_speed_up(self):
        test_file = wave_file.Wave("../Files/01 Bloody Nose.wav")
        first_sample_rate = test_file.sampleRate
        rate = 1.5
        test_file.speed_up(rate)
        second_sample_rate = int(first_sample_rate * rate)
        self.assertEqual(second_sample_rate, test_file.sampleRate)

    def test_speed_down(self):
        test_file = wave_file.Wave("../Files/01 Bloody Nose.wav")
        first_sample_rate = test_file.sampleRate
        rate = 1.5
        test_file.speed_down(rate)
        second_sample_rate = int(first_sample_rate // rate)
        self.assertEqual(second_sample_rate, test_file.sampleRate)

    def test_fade_in_and_out(self):
        test_file = wave_file.Wave("../Files/01 Bloody Nose.wav")
        array = np.linspace(0, 1, test_file.sampleRate * 3)
        test_value = test_file.channels[0][12345]
        test_file.fade_in(3)
        self.assertEqual(test_file.channels[0][12345],
                         int(test_value * array[12345]))
        test_value2 = test_file.channels[0][len(test_file.channels[0]) - 12346]
        test_file.fade_out(3)
        self.assertEqual(
            test_file.channels[0][len(test_file.channels[0]) - 12346],
            int(test_value2 * array[12345]))

    def test_change_volume(self):
        test_file = wave_file.Wave("../Files/01 Bloody Nose.wav")
        test_value = test_file.channels[0][55555]
        test_value = int(test_value * 0.7)
        test_file.change_volume(0.7)
        self.assertEqual(test_file.channels[0][55555], test_value)
        test_value = int(test_value * 1.5)
        test_file.change_volume(1.5)
        self.assertEqual(test_file.channels[0][55555], test_value)
