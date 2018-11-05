import wx
import wave_file
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import math

types = {
    1: np.int8,
    2: np.int16,
    4: np.int32
}
peak = 0


class GUI(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800, 800))
        self.Show(True)

        self.files = []

        menu = wx.Menu()
        open_item = menu.Append(wx.ID_ANY, "Open")
        save_item = menu.Append(wx.ID_SAVE, "Save")
        clear_item = menu.Append(wx.ID_ANY, "Clear tracks")
        about_item = menu.Append(wx.ID_ABOUT, "About")
        exit_item = menu.Append(wx.ID_EXIT, "Exit")
        bar = wx.MenuBar()
        bar.Append(menu, "File")
        self.SetMenuBar(bar)
        self.Bind(wx.EVT_MENU, self.on_open, open_item)
        self.Bind(wx.EVT_MENU, self.save, save_item)
        self.Bind(wx.EVT_MENU, self.clear_files, clear_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.opened_files = "No files"
        reverse_button = wx.BitmapButton(self,
                                         bitmap=wx.Bitmap(
                                             "Images/reverse.png"),
                                         pos=(10, 10))
        speed_up_button = wx.BitmapButton(self,
                                          bitmap=wx.Bitmap(
                                              "Images/faster.png"),
                                          pos=(120, 10))
        speed_down_button = wx.BitmapButton(self,
                                            bitmap=wx.Bitmap(
                                                "Images/slower.png"),
                                            pos=(230, 10))
        fade_in_button = wx.BitmapButton(self,
                                         bitmap=wx.Bitmap(
                                             "Images/fade_in.png"),
                                         pos=(340, 10))
        fade_out_button = wx.BitmapButton(self,
                                          bitmap=wx.Bitmap(
                                              "Images/fade_out.png"),
                                          pos=(450, 10))
        volume_button = wx.BitmapButton(self,
                                        bitmap=wx.Bitmap(
                                            "Images/volume.png"),
                                        pos=(560, 10))
        info_button = wx.BitmapButton(self,
                                      bitmap=wx.Bitmap(
                                          "Images/info.png"),
                                      pos=(670, 10))
        self.Bind(wx.EVT_BUTTON, self.increase_speed, speed_up_button)
        self.Bind(wx.EVT_BUTTON, self.decrease_speed, speed_down_button)
        self.Bind(wx.EVT_BUTTON, self.change_volume, volume_button)
        self.Bind(wx.EVT_BUTTON, self.reverse, reverse_button)
        self.Bind(wx.EVT_BUTTON, self.fade_in, fade_in_button)
        self.Bind(wx.EVT_BUTTON, self.fade_out, fade_out_button)
        self.Bind(wx.EVT_BUTTON, self.info, info_button)
        self.draw()

    def on_open(self, e):
        if len(self.files) == 0:
            open_file_dialog = wx.FileDialog(None, "DAI MNE WAV", "", "",
                                             "Wave files (*.wav)|*.wav")
            if open_file_dialog.ShowModal() == wx.ID_OK:
                path = open_file_dialog.GetPath()
                open_file_dialog.Destroy()
                self.files.append(wave_file.Wave(path))
                if len(self.files) == 1:
                    self.opened_files = "Opened files:\n"
                    self.opened_files += path
                else:
                    self.opened_files += "\n" + path
                self.draw()
                if self.files[0].audioFormat != 1:
                    self.show_notification(
                        "File is encrypted! Some functions may not work",
                        "Warning!")
        else:
            self.show_notification("File is already opened", "Error")

    def draw(self):
        if len(self.files) == 0:
            message = "No files!"
        else:
            message = self.files[0].filename
        opened_files_panel = wx.StaticText(self,
                                           label=self.opened_files,
                                           pos=(10, 150),
                                           size=(790, 100))

    def save(self, e):
        dlg = wx.TextEntryDialog(self, 'Enter name of new file', 'Save')

        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.GetValue()
            if name[-4:] != ".wav":
                name += ".wav"
            wave_file.create_file(name, self.files[0])
        dlg.Destroy()

    def on_about(self, e):
        self.show_notification("This is the editor for wav files", "About")

    def clear_files(self, e):
        self.files = []
        self.show_notification("Files list has been cleared", "Notice")
        self.opened_files = "No files!"
        self.draw()

    def on_exit(self, e):
        sys.exit(0)

    def increase_speed(self, e):
        dlg = wx.TextEntryDialog(self, 'Enter speed rate', 'Changing speed')

        if dlg.ShowModal() == wx.ID_OK:
            rate = float(dlg.GetValue())
            self.files[0].speed_up(rate)
        dlg.Destroy()

    def decrease_speed(self, e):
        dlg = wx.TextEntryDialog(self, 'Enter slow rate', 'Changing speed')
        if dlg.ShowModal() == wx.ID_OK:
            rate = float(dlg.GetValue())
            self.files[0].speed_down(rate)
        dlg.Destroy()

    def change_volume(self, e):
        if self.files[0].audioFormat != 1:
            self.show_notification(
                "This file does not support this feature.",
                "Unsupported operation")
            return
        dlg = wx.TextEntryDialog(self, 'Enter new value of volume',
                                 'Volume')
        if dlg.ShowModal() == wx.ID_OK:
            volume = float(dlg.GetValue())
            self.files[0].change_volume(volume)
        dlg.Destroy()

    def fade_in(self, e):
        if self.files[0].audioFormat != 1:
            self.show_notification(
                "This file does not support this feature.",
                "Unsupported operation")
            return
        dlg = wx.TextEntryDialog(self, 'Enter length for fade_in in seconds',
                                 'Fade in')
        if dlg.ShowModal() == wx.ID_OK:
            rate = float(dlg.GetValue())
            self.files[0].fade_in(rate)
        dlg.Destroy()

    def fade_out(self, e):
        if self.files[0].audioFormat != 1:
            self.show_notification(
                "This file does not support this feature.",
                "Unsupported operation")
            return
        dlg = wx.TextEntryDialog(self, 'Enter length for fade_out in seconds',
                                 'Fade out')
        if dlg.ShowModal() == wx.ID_OK:
            rate = float(dlg.GetValue())
            self.files[0].fade_out(rate)
        dlg.Destroy()

    def reverse(self, e):
        self.files[0].reverse()
        self.show_notification("File has been reversed", "Reverse")

    def info(self, e):
        if len(self.files) == 0:
            message = "No files!"
        else:
            message = ""
            for i in range(0, len(self.files)):
                if i != 0:
                    message += "\n\n"
                track = self.files[i]
                message += "Track {0}: {1}\n".format(str(i + 1),
                                                     track.filename)
                message += track.get_info()
        self.show_notification(message, "Files")

    def show_notification(self, message, topic):
        dlg = wx.MessageDialog(self, message, topic, wx.OK)
        dlg.ShowModal()
