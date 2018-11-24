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


class Fragment:

    def __init__(self, channels):
        self.channels = channels

    def reverse(self):
        new_channels = []
        for ch in self.channels:
            new_channels.append(np.flip(ch))
        self.channels = new_channels
