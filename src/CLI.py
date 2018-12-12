import src.wave_file as wav
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
        self.file = wav.Wave(path)
        print("Selected file: {0}".format(path))
        while mainloop:
            print("Enter command")
            command = input()
            if command == "save":
                dlg = wx.FileDialog(
                    None, message="Save file as",
                    defaultDir=".",
                    defaultFile="", wildcard="*.*", style=wx.FD_SAVE
                )
                if dlg.ShowModal() == wx.ID_OK:
                    path = dlg.GetPath()
                    if path[-4:] != ".wav":
                        path += ".wav"
                        wav.save_changes_in_file(path, self.file)
                mainloop = False
            else:
                self.execute_command(command)

    def execute_command(self, command):
        args = command.split(" ")
        if args[0] == "reverse":
            self.file.reverse()
        elif args[0] == "speed_up":
            if len(args) == 1:
                print("Usage: speed_up *rate*")
            else:
                rate = float(args[1])
                self.file.speed_up(rate)
        elif args[0] == "speed_down":
            if len(args) == 1:
                print("Usage: speed_down *rate*")
            else:
                rate = float(args[1])
                self.file.speed_down(rate)
        elif args[0] == "fade_in":
            if self.file.audioFormat != 1:
                print("This feature is unavailable for this file")
                return
            if len(args) == 1:
                print("Usage: fade_in *time_in_seconds*")
            else:
                rate = float(args[1])
                self.file.fade_in(rate)
        elif args[0] == "fade_out":
            if self.file.audioFormat != 1:
                print("This feature is unavailable for this file")
                return
            if len(args) == 1:
                print("Usage: fade_out *time_in_seconds*")
            else:
                rate = float(args[1])
                self.file.fade_out(rate)
        elif args[0] == "volume":
            if self.file.audioFormat != 1:
                print("This feature is unavailable for this file")
                return
            if len(args) == 1:
                print("Usage: volume *rate*")
            rate = float(args[1])
            self.file.change_volume(rate)
        elif command == "info":
            print(self.file.get_info())
        else:
            print("Unexpected command!")
