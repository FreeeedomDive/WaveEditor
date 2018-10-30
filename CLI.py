import wave_file
import wx
import sys


class CLI:

    def __init__(self):
        self.file = None

    def start(self):
        mainloop = True
        app = wx.App(False)
        openFileDialog = wx.FileDialog(None, "DAI MNE WAV", "", "",
                                       "Wave files (*.wav)|*.wav")
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            print("No selected file")
            sys.exit(0)
        path = openFileDialog.GetPath()
        openFileDialog.Destroy()
        self.file = wave_file.Wave(path)
        print("Selected file: {0}".format(path))
        while mainloop:
            print("Enter command")
            command = input()
            if command == "save":
                print("Enter name for new file")
                wave_file.create_file(input(), self.file)
                mainloop = False
            else:
                self.execute_command(command)

    def execute_command(self, command):
        if command == "reverse":
            self.file.reverse()
        elif command == "speed_up":
            print("Enter speed rate")
            rate = float(input())
            self.file.speed_up(rate)
        elif command == "speed_down":
            print("Enter slow rate")
            rate = float(input())
            self.file.speed_down(rate)
        elif command == "fade_in":
            print("Enter length (in seconds) for fade in")
            rate = float(input())
            self.file.fade_in(rate)
        elif command == "fade_out":
            print("Enter length (in seconds) for fade out")
            rate = float(input())
            self.file.fade_out(rate)
        elif command == "volume":
            print("Enter new value of volume")
            rate = float(input())
            self.file.change_volume(rate)
        else:
            print("Unexpected command!")
