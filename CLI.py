import wave_file
import wx
import sys


class CLI:

    def __init__(self):
        self.file = None

    def start(self):
        mainloop = True
        app = wx.App(False)
        open_file_dialog = wx.FileDialog(None, "Wave files", "", "",
                                         "Wave files (*.wav)|*.wav")
        if open_file_dialog.ShowModal() == wx.ID_CANCEL:
            print("No selected file")
            sys.exit(0)
        path = open_file_dialog.GetPath()
        open_file_dialog.Destroy()
        self.file = wave_file.Wave(path)
        print("Selected file: {0}".format(path))
        while mainloop:
            print("Enter command")
            command = input()
            if command == "save":
                print("Enter name for new file")
                name = input()
                if name[-4:] != ".wav":
                    name += ".wav"
                wave_file.save_changes_in_file(name, self.file)
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
            if self.file.audioFormat != 1:
                print("This feature is unavailable for this file")
                return
            print("Enter length (in seconds) for fade in")
            rate = float(input())
            self.file.fade_in(rate)
        elif command == "fade_out":
            if self.file.audioFormat != 1:
                print("This feature is unavailable for this file")
                return
            print("Enter length (in seconds) for fade out")
            rate = float(input())
            self.file.fade_out(rate)
        elif command == "volume":
            if self.file.audioFormat != 1:
                print("This feature is unavailable for this file")
                return
            print("Enter new value of volume")
            rate = float(input())
            self.file.change_volume(rate)
        elif command == "info":
            print(self.file.get_info())
        else:
            print("Unexpected command!")
