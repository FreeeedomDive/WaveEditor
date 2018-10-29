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


def reverse(track):
    result = []
    for channel in channels:
        result.append(np.flip(channel))
    return result


def speed_up(track, fast):
    frame_rate = track.getframerate()
    frame_rate = int(frame_rate * fast)
    return frame_rate


def slow_down(track, slow):
    frame_rate = track.getframerate()
    frame_rate = int(frame_rate // slow)
    return frame_rate


file_name = "02. Rammstein – Mein Teil.wav"
print("What u want to do with file?")
print("Reverse - re")
print("Speed up - su")
print("Slow down - sd")

with wave.open(file_name, "rb") as wave_read:
    track = wave_read
    sample_width = wave_read.getsampwidth()
    frame_rate = wave_read.getframerate()
    channels_count = wave_read.getnchannels()
    frames_count = wave_read.getnframes()
    channels = frames_to_channels(
        wave_read.readframes(wave_read.getnframes()),
        sample_width, wave_read.getnchannels())

command = input()
if command == "su":
    print("Enter degree of fast:")
    fast = float(input())
    frame_rate = speed_up(track, fast)
elif command == "sd":
    print("Enter degree of slow:")
    slow = float(input())
    frame_rate = slow_down(track, slow)
elif command == "re":
    channels = reverse(track)

# print(reversed)
with wave.open("result.wav", "wb") as new_file:
    new_file.setnchannels(channels_count)
    new_file.setsampwidth(sample_width)
    new_file.setframerate(frame_rate)
    new_file.setnframes(frames_count)
    result_frames = channels_to_frames(channels, sample_width)
    new_file.writeframes(result_frames)
    length = frames_count / frame_rate
    print(length)

print("Done!")
