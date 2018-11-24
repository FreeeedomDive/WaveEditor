import wx
import wave_file
import sys
import numpy as np
import pickle
import datetime
import fragment
import work_state

types = {
    1: np.int8,
    2: np.int16,
    4: np.int32
}


class GUI(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(1000, 800))
        self.Show(True)

        self.file = None
        self.fragments = []

        menu = wx.Menu()
        open_item = menu.Append(wx.ID_ANY, "Open file")
        save_item = menu.Append(wx.ID_ANY, "Save file")
        open_project_item = menu.Append(wx.ID_ANY, "Open project")
        save_project_item = menu.Append(wx.ID_ANY, "Save current project")
        about_item = menu.Append(wx.ID_ABOUT, "About")
        exit_item = menu.Append(wx.ID_EXIT, "Exit")
        bar = wx.MenuBar()
        bar.Append(menu, "File")
        menu2 = wx.Menu()
        save_fragments_item = menu2.Append(wx.ID_ANY, "Save fragments to file")
        bar.Append(menu2, "Fragments")
        self.SetMenuBar(bar)
        self.Bind(wx.EVT_MENU, self.on_open, open_item)
        self.Bind(wx.EVT_MENU, self.save, save_item)
        self.Bind(wx.EVT_MENU, self.open_project, open_project_item)
        self.Bind(wx.EVT_MENU, self.save_project, save_project_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self.concatenate_saved_fragments,
                  save_fragments_item)
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
        self.start_slider = wx.Slider(self, id=wx.ID_ANY, value=0,
                                      minValue=0, maxValue=1000,
                                      pos=(10, 300),
                                      size=(770, 20),
                                      style=wx.SL_HORIZONTAL,
                                      validator=wx.DefaultValidator,
                                      name=wx.SliderNameStr)
        self.end_slider = wx.Slider(self, id=wx.ID_ANY, value=1000,
                                    minValue=0, maxValue=1000,
                                    pos=(10, 325),
                                    size=(770, 20),
                                    style=wx.SL_HORIZONTAL,
                                    validator=wx.DefaultValidator,
                                    name=wx.SliderNameStr)
        separator = wx.StaticLine(self, id=wx.ID_ANY, pos=(790, 0),
                                  size=(5, 800),
                                  style=wx.LI_VERTICAL,
                                  name=wx.StaticLineNameStr)
        save_fragment_button = wx.Button(self, id=wx.ID_ANY,
                                         label="Save fragment",
                                         pos=(180, 240),
                                         size=(120, 50), style=0,
                                         validator=wx.DefaultValidator,
                                         name=wx.ButtonNameStr)
        self.Bind(wx.EVT_BUTTON, self.save_fragment, save_fragment_button)
        reverse_fragment_button = wx.Button(self, id=wx.ID_ANY,
                                            label="Reverse fragment",
                                            pos=(340, 240),
                                            size=(120, 50), style=0,
                                            validator=wx.DefaultValidator,
                                            name=wx.ButtonNameStr)
        self.Bind(wx.EVT_BUTTON, self.reverse_fragment,
                  reverse_fragment_button)
        delete_fragment_button = wx.Button(self, id=wx.ID_ANY,
                                           label="Delete fragment",
                                           pos=(500, 240),
                                           size=(120, 50), style=0,
                                           validator=wx.DefaultValidator,
                                           name=wx.ButtonNameStr)
        self.Bind(wx.EVT_BUTTON, self.cut_fragment, delete_fragment_button)
        self.draw_track()

    def on_open(self, e):
        open_file_dialog = wx.FileDialog(None, "Wave files", "", "",
                                         "Wave files (*.wav)|*.wav")
        if open_file_dialog.ShowModal() == wx.ID_OK:
            path = open_file_dialog.GetPath()
            open_file_dialog.Destroy()
            self.file = wave_file.Wave(path)
            self.draw_track()
            if self.file.audioFormat != 1:
                self.show_notification(
                    "File is encrypted! Some functions may not work",
                    "Warning!")

    def open_project(self, e):
        open_file_dialog = wx.FileDialog(None, "Pickle files", "", "",
                                         "Pickle files (*.pickle)|*.pickle")
        if open_file_dialog.ShowModal() == wx.ID_OK:
            path = open_file_dialog.GetPath()
            open_file_dialog.Destroy()
            with open(path, "rb") as file:
                state = pickle.load(file)
                self.file = state.file
                self.fragments = state.fragments
                if self.file is not None:
                    self.opened_files = "Opened file:\n"
                    self.opened_files += self.file.filename
                    self.draw_track()
                    if self.file.audioFormat != 1:
                        self.show_notification(
                            "File is encrypted! Some functions may not work",
                            "Warning!")
                else:
                    self.opened_files = "No file!\n"
                    self.draw_track()

    def save_project(self, e):
        d = datetime.datetime.now()
        filename = "SavedProjects/save-{0}-{1}-{2}-{3}-{4}-{5}.pickle" \
            .format(d.year, d.month, d.day, d.hour,
                    d.minute, d.second)
        state = work_state.WorkState(self.file, self.fragments)
        with open(filename, 'wb') as file:
            pickle.dump(state, file)

    def draw_track(self):
        # lines = []
        if self.file is None:
            opened_files = "No file!"
        #    elements_to_draw = np.ones(770)
        else:
            opened_files = self.file.filename
        #    elements_to_draw = self.file.channels[0][::770]
        # for i in range(0, 770):
        #    length = elements_to_draw[i] // 150
        #    lines.append(wx.StaticLine(self, id=wx.ID_ANY,
        #                               pos=(11 + i, 500 - length // 2),
        #                               size=(1, length),
        #                               style=wx.LI_VERTICAL,
        #                               name=wx.StaticLineNameStr))
        opened_files_panel = wx.StaticText(self,
                                           label=opened_files,
                                           pos=(10, 150),
                                           size=(500, 50))

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

    def on_exit(self, e):
        sys.exit(0)

    def save_fragment(self, e):
        if self.file is not None:
            left_border = self.start_slider.GetValue()
            right_border = self.end_slider.GetValue()
            if left_border > right_border:
                temp = left_border
                left_border = right_border
                right_border = temp
            length = len(self.file.channels[0])
            left_index = length // self.start_slider.GetMax() * left_border
            right_index = length // self.start_slider.GetMax() * right_border
            fragment_channels = self.file.get_fragment(left_index, right_index)
            self.fragments.append(fragment.Fragment(fragment_channels))
            print(len(fragment_channels[0]))

    def cut_fragment(self, e):
        if self.file is not None:
            max = self.start_slider.GetMax()
            left_border = self.start_slider.GetValue()
            right_border = self.end_slider.GetValue()
            if left_border > right_border:
                temp = left_border
                left_border = right_border
                right_border = temp
            if left_border == 0 and right_border == max:
                self.show_notification(
                    "You can't delete all track!",
                    "Deleting")
                return
            length = len(self.file.channels[0])
            left_index = length // self.start_slider.GetMax() * left_border
            right_index = length // self.start_slider.GetMax() * right_border
            start = fragment.Fragment(
                self.file.get_fragment(0, left_index - 1))
            end = fragment.Fragment(
                self.file.get_fragment(right_index + 1, length))
            self.file.channels = fragment.concatenate_fragments((start, end))
            self.file.subchunk2Size = len(
                self.file.channels[0]) * self.file.bitsPerSample // 4
            self.file.chunkSize = self.file.subchunk2Size + 36

    def reverse_fragment(self, e):
        print("reverse")
        if self.file is not None:
            max = self.start_slider.GetMax()
            left_border = self.start_slider.GetValue()
            right_border = self.end_slider.GetValue()
            if left_border > right_border:
                temp = left_border
                left_border = right_border
                right_border = temp
            if left_border == 0 and right_border == max:
                self.show_notification(
                    "For reversing all the track use \"reverse\" button",
                    "Reverse")
                return
            length = len(self.file.channels[0])
            left_index = length // self.start_slider.GetMax() * left_border
            right_index = length // self.start_slider.GetMax() * right_border
            start = fragment.Fragment(
                self.file.get_fragment(0, left_index - 1))
            fr = fragment.Fragment(
                self.file.get_fragment(left_index, right_index))
            fr.reverse()
            end = fragment.Fragment(
                self.file.get_fragment(right_index + 1, length))
            self.file.channels = fragment.concatenate_fragments(
                [start, fr, end])

    def concatenate_saved_fragments(self, e):
        if len(self.fragments) != 0:
            compilation = fragment.concatenate_fragments(self.fragments)
            dlg = wx.TextEntryDialog(self, 'Enter name of new file', 'Save')

            if dlg.ShowModal() == wx.ID_OK:
                name = dlg.GetValue()
                if name[-4:] != ".wav":
                    name += ".wav"
                # self.file.channels = compilation
                # self.file.subchunk2Size = len(
                #     self.file.channels[0]) * self.file.bitsPerSample // 4
                # self.file.chunkSize = self.file.subchunk2Size + 36
                # wave_file.save_changes_in_file(name, self.file)
                wave_file.create_file_from_channels(name, compilation)
            dlg.Destroy()

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
