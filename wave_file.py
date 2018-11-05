import numpy as np

TYPES = {
    8: np.int8,
    16: np.int16,
    32: np.int32
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
        f.write(file.chunkId.encode("UTF-8"))
        f.write(file.chunkSize.to_bytes(4, byteorder="little"))
        f.write(file.format.encode("UTF-8"))
        f.write(file.subchunk1Id.encode("UTF-8"))
        f.write(file.subchunk1Size.to_bytes(4, byteorder="little"))
        f.write(file.audioFormat.to_bytes(2, byteorder="little"))
        f.write(file.numChannels.to_bytes(2, byteorder="little"))
        f.write(file.sampleRate.to_bytes(4, byteorder="little"))
        f.write(file.byteRate.to_bytes(4, byteorder="little"))
        f.write(file.blockAlign.to_bytes(2, byteorder="little"))
        f.write(int(file.bitsPerSample).to_bytes(2, "little"))
        f.write(file.subchunk2Id.encode("UTF-8"))
        f.write(file.subchunk2Size.to_bytes(4, "little"))
        f.write(bytes(channels_to_frames(file.channels,
                                         file.bitsPerSample)))


class Wave:

    def __init__(self, filename):
        file = open(filename, 'rb')
        self.filename = filename
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
        self.bitsPerSample = int.from_bytes(file.read(2), "little")
        self.subchunk2Id = file.read(4).decode("UTF-8")
        self.subchunk2Size = int.from_bytes(file.read(4), "little")
        self.data = file.read(self.subchunk2Size)

        self.channels = frames_to_channels(self.data, self.bitsPerSample,
                                           self.numChannels)

        self.duration = self.subchunk2Size / self.sampleRate
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

    def fade_in(self, rate):
        length = int(self.sampleRate * rate)
        amount = 1 / length
        array = []
        for i in range(0, length):
            array.append(amount * i)
            for channel in self.channels:
                channel[i] *= array[i]

    def fade_out(self, rate):
        length = int(self.sampleRate * rate)
        amount = 1 / length
        array = []
        for i in range(0, length):
            array.append(amount * i)
            for channel in self.channels:
                channel[len(channel) - i - 1] *= array[i]

    def change_volume(self, rate):
        new_channels = []
        for channel in self.channels:
            new_channels.append(channel * rate)
        self.channels = new_channels

    def get_info(self):
        info = "chunkID: " + self.chunkId
        info += "\nchunkSize: " + str(self.chunkSize)
        info += "\nformat: " + self.format
        info += "\nsubchunk1ID: " + self.subchunk1Id
        info += "\nsubchunk1Size: " + str(self.subchunk1Size)
        info += "\naudioFormat: " + str(self.audioFormat)
        info += "\nnumChannels: " + str(self.numChannels)
        info += "\nsampleRate: " + str(self.sampleRate)
        info += "\nbyteRate: " + str(self.byteRate)
        info += "\nblockAlign: " + str(self.blockAlign)
        info += "\nbitsPerSample: " + str(self.bitsPerSample)
        info += "\nsubchunk2ID: " + self.subchunk2Id
        info += "\nsubChunk2Size: " + str(self.subchunk2Size)
        return info
