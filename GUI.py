import wx
import wave_file
import sys
import numpy as np
import pickle
import datetime

types = {
    1: np.int8,
    2: np.int16,
    4: np.int32
}


class GUI(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(1200, 800))
        self.Show(True)

        self.file = None

        menu = wx.Menu()
        open_item = menu.Append(wx.ID_ANY, "Open file")
        save_item = menu.Append(wx.ID_SAVE, "Save file")
        open_project_item = menu.Append(wx.ID_ANY, "Open project")
        save_project_item = menu.Append(wx.ID_ANY, "Save current project")
        clear_item = menu.Append(wx.ID_ANY, "Clear tracks")
        about_item = menu.Append(wx.ID_ABOUT, "About")
        exit_item = menu.Append(wx.ID_EXIT, "Exit")
        bar = wx.MenuBar()
        bar.Append(menu, "File")
        self.SetMenuBar(bar)
        self.Bind(wx.EVT_MENU, self.on_open, open_item)
        self.Bind(wx.EVT_MENU, self.save, save_item)
        self.Bind(wx.EVT_MENU, self.open_project, open_project_item)
        self.Bind(wx.EVT_MENU, self.save_project, save_project_item)
        self.Bind(wx.EVT_MENU, self.clear_files, clear_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.opened_files = "No file!"
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
        if self.file is None:
            open_file_dialog = wx.FileDialog(None, "Wave files", "", "",
                                             "Wave files (*.wav)|*.wav")
            if open_file_dialog.ShowModal() == wx.ID_OK:
                path = open_file_dialog.GetPath()
                open_file_dialog.Destroy()
                self.file = wave_file.Wave(path)
                self.opened_files = "Opened file:\n"
                self.opened_files += path
                self.draw()
                if self.file.audioFormat != 1:
                    self.show_notification(
                        "File is encrypted! Some functions may not work",
                        "Warning!")
        else:
            self.show_notification("File is already opened", "Error")

    def open_project(self, e):
        open_file_dialog = wx.FileDialog(None, "Pickle files", "", "",
                                         "Pickle files (*.pickle)|*.pickle")
        if open_file_dialog.ShowModal() == wx.ID_OK:
            path = open_file_dialog.GetPath()
            open_file_dialog.Destroy()
            with open(path, "rb") as file:
                self.file = pickle.load(file)
                self.opened_files = "Opened file:\n"
                self.opened_files += self.file.filename
                self.draw()
                if self.file.audioFormat != 1:
                    self.show_notification(
                        "File is encrypted! Some functions may not work",
                        "Warning!")

    def save_project(self, e):
        if self.file is not None:
            d = datetime.datetime.now()
            filename = "SavedProjects/save-{0}-{1}-{2}-{3}-{4}-{5}.pickle" \
                .format(d.year, d.month, d.day, d.hour,
                        d.minute, d.second)
            with open(filename, 'wb') as file:
                    pickle.dump(self.file, file)

    def draw(self):
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
            wave_file.save_changes_in_file(name, self.file)
        dlg.Destroy()

    def on_about(self, e):
        self.show_notification("This is the editor for wav files", "About")

    def clear_files(self, e):
        self.file = None
        self.show_notification("Files list has been cleared", "Notice")
        self.opened_files = "No file!"
        self.draw()

    def on_exit(self, e):
        sys.exit(0)

    def increase_speed(self, e):
        dlg = wx.TextEntryDialog(self, 'Enter speed rate', 'Changing speed')

        if dlg.ShowModal() == wx.ID_OK:
            rate = float(dlg.GetValue())
            self.file.speed_up(rate)
        dlg.Destroy()

    def decrease_speed(self, e):
        dlg = wx.TextEntryDialog(self, 'Enter slow rate', 'Changing speed')
        if dlg.ShowModal() == wx.ID_OK:
            rate = float(dlg.GetValue())
            self.file.speed_down(rate)
        dlg.Destroy()

    def change_volume(self, e):
        if self.file.audioFormat != 1:
            self.show_notification(
                "This file does not support this feature.",
                "Unsupported operation")
            return
        dlg = wx.TextEntryDialog(self, 'Enter new value of volume',
                                 'Volume')
        if dlg.ShowModal() == wx.ID_OK:
            volume = float(dlg.GetValue())
            self.file.change_volume(volume)
        dlg.Destroy()

    def fade_in(self, e):
        if self.file.audioFormat != 1:
            self.show_notification(
                "This file does not support this feature.",
                "Unsupported operation")
            return
        dlg = wx.TextEntryDialog(self, 'Enter length for fade_in in seconds',
                                 'Fade in')
        if dlg.ShowModal() == wx.ID_OK:
            rate = float(dlg.GetValue())
            self.file.fade_in(rate)
        dlg.Destroy()

    def fade_out(self, e):
        if self.file.audioFormat != 1:
            self.show_notification(
                "This file does not support this feature.",
                "Unsupported operation")
            return
        dlg = wx.TextEntryDialog(self, 'Enter length for fade_out in seconds',
                                 'Fade out')
        if dlg.ShowModal() == wx.ID_OK:
            rate = float(dlg.GetValue())
            self.file.fade_out(rate)
        dlg.Destroy()

    def reverse(self, e):
        self.file.reverse()
        self.show_notification("File has been reversed", "Reverse")

    def info(self, e):
        if self.file is None:
            message = "No file!"
        else:
            message = ""
            message += "Track: {0}\n".format(self.file.filename)
            message += self.file.get_info()
        self.show_notification(message, "Files")

    def show_notification(self, message, topic):
        dlg = wx.MessageDialog(self, message, topic, wx.OK)
        dlg.ShowModal()
