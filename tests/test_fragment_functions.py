import unittest
from src import fragment
from src import wave_file


class TestFragment(unittest.TestCase):
    def test_concatenation(self):
        test_file = wave_file.Wave("../Files/01 Bloody Nose.wav")
        fragment1 = fragment.Fragment(test_file.get_fragment(0, 550000))
        fragment2 = fragment.Fragment(test_file.get_fragment(1000000, 1250000))
        temp = fragment.concatenate_fragments((fragment1, fragment2))
        concat = fragment.Fragment(temp)
        self.assertEqual(len(concat.channels), 2)
        self.assertEqual(len(concat.channels[0]), 800000)
        self.assertEqual(len(concat.channels[1]), 800000)

    def test_union_with_same_length(self):
        test_file = wave_file.Wave("../Files/01 Bloody Nose.wav")
        fragment1 = fragment.Fragment(test_file.get_fragment(0, 550000))
        fragment2 = fragment.Fragment(test_file.get_fragment(550000, 1100000))
        union = fragment.collect_fragments_to_one((fragment1, fragment2),
                                                  test_file.channels[0].dtype)
        union_fragment = fragment.Fragment(union)
        self.assertEqual(len(union_fragment.channels), 2)
        self.assertEqual(len(union_fragment.channels[0]), 550000)
        test_value = fragment1.channels[0][12345] + fragment2.channels[0][
            12345]
        self.assertEqual(union_fragment.channels[0][12345], test_value)

    def test_union_with_different_length(self):
        test_file = wave_file.Wave("../Files/01 Bloody Nose.wav")
        fragment1 = fragment.Fragment(test_file.get_fragment(0, 600000))
        fragment2 = fragment.Fragment(test_file.get_fragment(550000, 900000))
        union = fragment.collect_fragments_to_one((fragment1, fragment2),
                                                  test_file.channels[0].dtype)
        union_fragment = fragment.Fragment(union)
        self.assertEqual(len(union_fragment.channels), 2)
        self.assertEqual(len(union_fragment.channels[0]), 600000)
        test_value = fragment1.channels[0][12345] + fragment2.channels[0][
            12345]
        self.assertEqual(union_fragment.channels[0][12345], test_value)

    def test_reverse_fragment(self):
        test_file = wave_file.Wave("../Files/01 Bloody Nose.wav")
        fragment1 = fragment.Fragment(test_file.get_fragment(0, 600000))
        self.assertEqual(len(fragment1.channels[0]), 600000)
        test_value = fragment1.channels[0][12345]
        fragment1.reverse()
        self.assertEqual(
            fragment1.channels[0][len(fragment1.channels[0]) - 12346],
            test_value)
