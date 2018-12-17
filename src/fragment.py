import numpy as np


def concatenate_fragments(fragments):
    min_channels = 100
    for fragment in fragments:
        if len(fragment.channels) < min_channels:
            min_channels = len(fragment.channels)
    new_channels = []
    for i in range(0, min_channels):
        channel = fragments[0].channels[i]
        for f in range(1, len(fragments)):
            channel = np.concatenate((channel, fragments[f].channels[i]))
        new_channels.append(channel)
    return new_channels


def collect_fragments_to_one(fragments, type):
    min_channels = 100
    min = max = 0
    if type == np.int8:
        min = 0
        max = 255
    elif type == np.int16:
        min = -32768
        max = 32767
    elif type == np.int32:
        min = -2147483648
        max = 2147483647
    for f in fragments:
        if len(f.channels) < min_channels:
            min_channels = len(f.channels)
    result = []
    for channel in fragments[0].channels:
        result.append(channel.copy())
    for i in range(1, len(fragments)):
        temp_fragment = []
        for channel in fragments[i].channels:
            temp_fragment.append(channel.copy())
        difference = abs(len(result[0]) - len(temp_fragment[0]))
        zeros = np.zeros(difference).astype(result[0].dtype)
        if len(result[0]) < len(temp_fragment[0]):
            remaked = []
            for channel in result:
                new = np.concatenate((channel, zeros))
                remaked.append(new)
            result = remaked
        elif len(result[0]) > len(temp_fragment[0]):
            remaked = []
            for channel in temp_fragment:
                new = np.concatenate((channel, zeros))
                remaked.append(new)
            temp_fragment = remaked
        for c in range(0, len(result)):
            result[c] += np.clip((result[c] + temp_fragment[c]), min,
                                 max).astype(type)
    return result


class Fragment:

    def __init__(self, channels):
        self.channels = channels

    def reverse(self):
        new_channels = []
        for ch in self.channels:
            new_channels.append(np.flip(ch))
        self.channels = new_channels
