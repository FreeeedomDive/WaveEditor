class wave:
    def __init__(self, filename):
        file = open(filename, 'rb')
        content = file.read()

        self.chunkId = content[0:4].decode("UTF-8")
        self.chunkSize = int.from_bytes(content[4:8], "little")
        self.format = content[8:12].decode("UTF-8")
        self.subchunk1Id = content[12:16].decode("UTF-8")
        self.subchunk1Size = int.from_bytes(content[16:20], "little")
        self.audioFormat = int.from_bytes(content[20:21], "little")
        self.numChannels = int.from_bytes(content[22:24], "little")
        self.sampleRate = int.from_bytes(content[24:28], "little")
        self.byteRate = int.from_bytes(content[28:32], "little")
        self.blockAlign = int.from_bytes(content[32:34], "little")
        self.bitsPerSample = int.from_bytes(content[34:36], "little")
        self.subchunk2Id = content[36:40].decode("UTF-8")
        self.subchunk2Size = int.from_bytes(content[40:44], "little")
        self.data = content[44:]

        file.close()

    def get_all(self):
        s = self.chunkId + "\n"
        s += str(self.chunkSize) + "\n"
        s += self.format + "\n"
        s += self.subchunk1Id + "\n"
        s += str(self.subchunk1Size) + "\n"
        s += str(self.audioFormat) + "\n"
        s += str(self.numChannels) + "\n"
        s += str(self.sampleRate) + "\n"
        s += str(self.byteRate) + "\n"
        s += str(self.blockAlign) + "\n"
        s += str(self.bitsPerSample) + "\n"
        s += self.subchunk2Id + "\n"
        s += str(self.subchunk2Size) + "\n"
        return s
