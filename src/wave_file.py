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


def save_changes_in_file(path, file):
    with open(path, 'wb') as f:
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
        f.write(file.bitsPerSample.to_bytes(2, "little"))
        f.write(file.subchunk2Id.encode("UTF-8"))
        f.write(file.subchunk2Size.to_bytes(4, "little"))
        f.write(bytes(channels_to_frames(file.channels,
                                         file.bitsPerSample)))


def create_file_from_channels(filename, channels):
    path = "Result/" + filename
    chunkID = "RIFF"
    format = "WAVE"
    subchunk1ID = "fmt"
    subchunk2ID = "data"
    subchunk1Size = 16
    audioFormat = 1
    numChannels = len(channels)
    sampleRate = 44100
    byteRate = 176400
    blockAlign = 4
    bitsPerSample = 16
    subchunk2Size = len(channels[0]) * bitsPerSample // 4
    chunkSize = subchunk2Size + 36
    with open(path, 'wb') as f:
        f.write(chunkID.encode("UTF-8"))
        f.write(chunkSize.to_bytes(4, byteorder="little"))
        f.write(format.encode("UTF-8"))
        f.write(subchunk1ID.encode("UTF-8"))
        f.write(subchunk1Size.to_bytes(4, byteorder="little"))
        f.write(audioFormat.to_bytes(2, byteorder="little"))
        f.write(numChannels.to_bytes(2, byteorder="little"))
        f.write(sampleRate.to_bytes(4, byteorder="little"))
        f.write(byteRate.to_bytes(4, byteorder="little"))
        f.write(blockAlign.to_bytes(2, byteorder="little"))
        f.write(bitsPerSample.to_bytes(2, "little"))
        f.write(subchunk2ID.encode("UTF-8"))
        f.write(subchunk2Size.to_bytes(4, "little"))
        f.write(bytes(channels_to_frames(channels,
                                         bitsPerSample)))


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

    def get_frames(self):
        return bytes(channels_to_frames(self.channels,
                                        self.bitsPerSample))

    def fragment_to_frames(self, start, end):
        fragment = self.get_fragment(start, end)
        return bytes(channels_to_frames(fragment,
                                        self.bitsPerSample))

    def get_fragment(self, start, end):
        channels_fragment = []
        for channel in self.channels:
            channels_fragment.append(channel[start:end])
        return channels_fragment

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
        array = np.linspace(0, 1, length)
        for i in range(0, length):
            for channel in self.channels:
                channel[i] *= array[i]

    def fade_out(self, rate):
        length = int(self.sampleRate * rate)
        array = np.linspace(0, 1, length)
        for i in range(0, length):
            for channel in self.channels:
                channel[len(channel) - i - 1] *= array[i]

    def change_volume(self, rate):
        temp_type = self.channels[0].dtype
        min = max = 0
        if temp_type == np.int8:
            min = 0
            max = 255
        elif temp_type == np.int16:
            min = -32768
            max = 32767
        elif temp_type == np.int32:
            min = -2147483648
            max = 2147483647
        temp_channels = []
        for channel in self.channels:
            temp_channels.append(
                np.clip((channel * rate), min, max).astype(temp_type))
        self.channels = temp_channels

    def change_height(self, ratio):
        self.sampleRate = int(self.sampleRate * ratio)
        self.change_channel_length(ratio)

    def change_channel_length(self, ratio):
        ratio = int(ratio * 10)
        temp_channels = []
        for channel in self.channels:
            ch = np.repeat(channel, ratio)[::10]
            temp_channels.append(ch)
        self.channels = temp_channels
        self.subchunk2Size = len(self.channels[0]) * self.bitsPerSample // 4
        self.chunkSize = self.subchunk2Size + 36

    def average_loudness(self, rate):
        window_size = 40000
        new_channels = []
        for channel in self.channels:
            if len(channel) < window_size:
                return channel
            abs_channel = np.absolute(channel)
            total_average = sum(abs_channel) / len(abs_channel)
            cur_sum = sum(abs_channel[0:window_size])
            float_window_size = np.float64(window_size)
            result = np.zeros(len(channel), channel.dtype)
            for i in range(0, len(channel)):
                if i - window_size // 2 >= 0 and \
                        i + window_size // 2 < len(channel):
                    cur_sum -= abs_channel[i - window_size // 2]
                    cur_sum += abs_channel[i + window_size // 2]
                window_average = cur_sum / float_window_size
                ratio = window_average / total_average
                diff = ratio - 1
                diff *= rate
                ratio = 1 + diff
                res = abs_channel[i] / ratio
                if channel[i] < 0:
                    res = -res
                result[i] = res
            new_channels.append(result)
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
