import wave_file
import wx


class CLI:

    def __init__(self):
        self.file = None

    def start(self):
        mainloop = True
        app = wx.App(False)
        openFileDialog = wx.FileDialog(None, "DAI MNE WAV", "", "",
                                       "Wave files (*.wav)|*.wav")
        openFileDialog.ShowModal()
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
        if command == "re":
            self.file.reverse()
        elif command == "su":
            print("Enter speed rate")
            rate = float(input())
            self.file.speed_up(rate)
        elif command == "sd":
            print("Enter slow rate")
            rate = float(input())
            self.file.speed_down(rate)
        elif command == "fi":
            print("Enter length (in seconds for fade in")
            length = float(input())
        else:
            print("Unexpected command!")
