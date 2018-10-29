import numpy as np

TYPES = {
    1: np.int8,
    2: np.int16,
    4: np.int32
}


def frames_to_channels(frames, sample_width, channels_number):
    return samples_to_channels(
        frames_to_samples(frames, sample_width),
        channels_number)


def samples_to_channels(samples, channels_number):
    return [samples[channel_index::channels_number]
            for channel_index in range(channels_number)]


def frames_to_samples(frames, sample_width):
    return np.fromstring(frames,
                         dtype=TYPES[sample_width])


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


def create_file(filename, file):
    with open(filename, 'wb') as f:
        f.write(file.chunkId.encode())
        f.write(bytes(file.chunkSize))
        f.write(file.format.encode())
        f.write(file.subchunk1Id.encode())
        f.write(bytes(file.subchunk1Size))
        f.write(bytes(file.audioFormat))
        f.write(bytes(file.numChannels))
        f.write(bytes(file.sampleRate))
        f.write(bytes(file.byteRate))
        f.write(bytes(file.blockAlign))
        f.write(bytes(file.bitsPerSample * 8))
        f.write(file.subchunk2Id.encode())
        f.write(bytes(file.subchunk2Size))
        f.write(bytes(channels_to_frames(file.channels,
                                         file.bitsPerSample)))


class Wave:

    def __init__(self, filename):
        file = open(filename, 'rb')

        self.chunkId = file.read(4).decode("UTF-8")
        self.chunkSize = int.from_bytes(file.read(4), "little")
        self.format = file.read(4).decode("UTF-8")
        self.subchunk1Id = file.read(4).decode("UTF-8")
        self.subchunk1Size = int.from_bytes(file.read(4), "little")
        self.audioFormat = int.from_bytes(file.read(2), "little")
        self.numChannels = int.from_bytes(file.read(2), "little")
        self.sampleRate = int.from_bytes(file.read(4), "little")
        self.byteRate = int.from_bytes(file.read(4), "little")
        self.blockAlign = int.from_bytes(file.read(2), "little")
        self.bitsPerSample = int.from_bytes(file.read(2), "little") // 8
        self.subchunk2Id = file.read(4).decode("UTF-8")
        self.subchunk2Size = int.from_bytes(file.read(4), "little")
        self.data = file.read(self.subchunk2Size)

        self.channels = frames_to_channels(self.data, self.numChannels,
                                           self.bitsPerSample)
        file.close()

    def reverse(self):
        new_channels = []
        for ch in self.channels:
            new_channels.append(np.flip(ch))
        self.channels = new_channels

    def speed_up(self, rate):
        self.sampleRate = int(self.sampleRate * rate)

    def speed_down(self, rate):
        self.sampleRate = int(self.sampleRate // rate)
