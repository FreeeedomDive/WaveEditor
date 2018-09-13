import numpy as np
import wave

TYPES = {
    1: np.int8,
    2: np.int16,
    4: np.int32
}


def frames_to_channels(frames, sample_width, channels_number):
    return samples_to_channels(frames_to_samples(frames, sample_width),
                               channels_number)


def samples_to_channels(samples, channels_number):
    return [samples[channel_index::channels_number]
            for channel_index in range(channels_number)]


def frames_to_samples(frames, sample_width):
    return np.fromstring(frames,
                         dtype=TYPES[sample_width]).astype(dtype=np.int64)


def channels_to_frames(channels, sample_width):
    return samples_to_frames(channels_to_samples(channels), sample_width)


def channels_to_samples(channels):
    result = np.zeros(sum(map(len, channels)), dtype=np.int64)
    for channel_index in range(len(channels)):
        np.put(result, np.arange(channel_index, len(result),
                                 len(channels)), channels[channel_index])
    return result


def samples_to_frames(samples, sample_width):
    return samples.astype(TYPES[sample_width]).tostring()


def reverse(channels):
    result = []
    for channel in channels:
        result.append(np.flip(channel))
    return result


file_name = "new.wav"
with wave.open(file_name, "rb") as wave_read:
    sample_width = wave_read.getsampwidth()
    frame_rate = wave_read.getframerate()
    channels_count = wave_read.getnchannels()
    frames = wave_read.getnframes()
    channels = frames_to_channels(
        wave_read.readframes(wave_read.getnframes()),
        sample_width, wave_read.getnchannels())
    # print(wave_read.getparams())
# print(sample_width)
# print(frame_rate)
# print(channels_count)
# print(channels)
# for channel in channels:
#     for i in channel:
#         print(i)
reversed = reverse(channels)
# print(reversed)
with wave.open("result.wav", "wb") as new_file:
    new_file.setnchannels(channels_count)
    new_file.setsampwidth(sample_width)
    new_file.setframerate(frame_rate)
    new_file.setnframes(frames)
    result_frames = channels_to_frames(reversed, sample_width)
    new_file.writeframes(result_frames)
    length = frames / frame_rate
    print(length)

print("Done!")
