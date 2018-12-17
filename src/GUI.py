import math

import wx
import src.wave_file as wav
import sys
import numpy as np
import pickle
import datetime
import src.fragment as fragment
import src.work_state as work_state
import pyaudio
import threading

types = {
    1: np.int8,
    2: np.int16,
    4: np.int32
}


class GUI(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(1050, 800))
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
        play_item = menu2.Append(wx.ID_ANY, "Play")
        self.Bind(wx.EVT_MENU, self.play, play_item)
        bar.Append(menu2, "Audio")
        self.SetMenuBar(bar)
        self.Bind(wx.EVT_MENU, self.on_open, open_item)
        self.Bind(wx.EVT_MENU, self.save, save_item)
        self.Bind(wx.EVT_MENU, self.open_project, open_project_item)
        self.Bind(wx.EVT_MENU, self.save_project, save_project_item)
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
        delete_fragments_button = wx.Button(self, id=wx.ID_ANY,
                                            label="Delete\nfragments",
                                            pos=(810, 10),
                                            size=(210, 50), style=0,
                                            validator=wx.DefaultValidator,
                                            name=wx.ButtonNameStr)
        self.Bind(wx.EVT_BUTTON, self.clear_fragments,
                  delete_fragments_button)
        collect_fragments_button = wx.Button(self, id=wx.ID_ANY,
                                             label="Collect all fragments\n"
                                                   "to one",
                                             pos=(810, 70),
                                             size=(100, 50), style=0,
                                             validator=wx.DefaultValidator,
                                             name=wx.ButtonNameStr)
        concat_and_move_button = wx.Button(self, id=wx.ID_ANY,
                                           label="Concatenate\n"
                                                 "fragments",
                                           pos=(920, 70),
                                           size=(100, 50), style=0,
                                           validator=wx.DefaultValidator,
                                           name=wx.ButtonNameStr)
        self.Bind(wx.EVT_BUTTON, self.concat_and_move,
                  concat_and_move_button)
        self.Bind(wx.EVT_BUTTON, self.collect_all_fragments_to_one,
                  collect_fragments_button)
        self.drawing_lines = []
        for i in range(0, 770):
            self.drawing_lines.append(wx.StaticLine(self, id=wx.ID_ANY,
                                                    pos=(11 + i, 500),
                                                    size=(1, 1),
                                                    style=wx.LI_VERTICAL,
                                                    name=wx.StaticLineNameStr))

        self.is_playing = False
        self.draw_track()
        self.draw_fragments()

    def on_open(self, e):
        open_file_dialog = wx.FileDialog(None, "Wave files", ".", "",
                                         "Wave files (*.wav)|*.wav")
        if open_file_dialog.ShowModal() == wx.ID_OK:
            path = open_file_dialog.GetPath()
            open_file_dialog.Destroy()
            self.file = wav.Wave(path)
            self.draw_track()
            if self.file.audioFormat != 1:
                self.show_notification(
                    "File is encrypted! Some functions may not work",
                    "Warning!")

    def open_project(self, e):
        open_file_dialog = wx.FileDialog(None, "Pickle files", ".", "",
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
                    if self.file.audioFormat != 1:
                        self.show_notification(
                            "File is encrypted! Some functions may not work",
                            "Warning!")
                else:
                    self.opened_files = "No file!\n"
                self.draw_track()
                self.draw_fragments()

    def save_project(self, e):
        d = datetime.datetime.now()
        filename = "SavedProjects/save-{0}-{1}-{2}-{3}-{4}-{5}.pickle" \
            .format(d.year, d.month, d.day, d.hour,
                    d.minute, d.second)
        state = work_state.WorkState(self.file, self.fragments)
        with open(filename, 'wb') as file:
            pickle.dump(state, file)

    def draw_track(self):
        if self.file is None:
            opened_files = "No file!"
            elements_to_draw = np.ones(770)
        else:
            opened_files = self.file.filename
            elements_to_draw = self.file.channels[0][::770]
        for i in range(0, 770):
            if i >= len(elements_to_draw):
                length = 0
            else:
                length = math.fabs(elements_to_draw[i] // 150 + 1)
            self.drawing_lines[i].SetSize((1, length))
            self.drawing_lines[i].SetPosition((11 + i, 500 - length // 2))
        opened_files_panel = wx.StaticText(self,
                                           label=opened_files,
                                           pos=(10, 150),
                                           size=(500, 50))

    def draw_fragments(self):
        if len(self.fragments) == 0:
            active_fragments = wx.StaticText(self,
                                             label="No fragments available",
                                             pos=(810, 150),
                                             size=(200, 750))
            return
        text = ""
        for i in range(0, len(self.fragments)):
            text += "Fragment {0}\n".format(i + 1)
            text += "Length: {0}\n\n".format(
                len(self.fragments[i].channels[0]))
        active_fragments = wx.StaticText(self,
                                         label=text,
                                         pos=(810, 150),
                                         size=(200, 750))

    def save(self, e):
        if self.file is not None:
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
                left_border, right_border = right_border, left_border
            length = len(self.file.channels[0])
            left_index = length // self.start_slider.GetMax() * left_border
            right_index = length // self.start_slider.GetMax() * right_border
            fragment_channels = self.file.get_fragment(left_index, right_index)
            self.fragments.append(fragment.Fragment(fragment_channels))
            self.draw_fragments()

    def cut_fragment(self, e):
        if self.file is not None:
            max = self.start_slider.GetMax()
            left_border = self.start_slider.GetValue()
            right_border = self.end_slider.GetValue()
            if left_border > right_border:
                left_border, right_border = right_border, left_border
            if left_border == 0 and right_border == max:
                self.show_notification(
                    "You can't delete all track!",
                    "Deleting")
                return
            length = len(self.file.channels[0])
            left_index = length // max * left_border
            right_index = length // max * right_border
            if left_border == 0:
                end = fragment.Fragment(
                    self.file.get_fragment(right_index + 1, length))
                self.file.channels = end.channels
            elif right_border == max:
                start = fragment.Fragment(
                    self.file.get_fragment(0, left_index - 1))
                self.file.channels = start.channels
            else:
                start = fragment.Fragment(
                    self.file.get_fragment(0, left_index - 1))
                end = fragment.Fragment(
                    self.file.get_fragment(right_index + 1, length))
                self.file.channels = fragment.concatenate_fragments(
                    [start, end])
            self.file.subchunk2Size = len(
                self.file.channels[0]) * self.file.bitsPerSample // 4
            self.file.chunkSize = self.file.subchunk2Size + 36
            self.draw_track()

    def reverse_fragment(self, e):
        if self.file is not None:
            max = self.start_slider.GetMax()
            left_border = self.start_slider.GetValue()
            right_border = self.end_slider.GetValue()
            if left_border > right_border:
                left_border, right_border = right_border, left_border
            if left_border == 0 and right_border == max:
                self.show_notification(
                    "For reversing all the track use \"reverse\" button",
                    "Reverse")
                return
            length = len(self.file.channels[0])
            left_index = length // max * left_border
            right_index = length // max * right_border
            if left_border == 0:
                start = fragment.Fragment(
                    self.file.get_fragment(0, right_index))
                start.reverse()
                end = fragment.Fragment(
                    self.file.get_fragment(right_index + 1, length))
                self.file.channels = fragment.concatenate_fragments(
                    [start, end])
            elif right_border == max:
                start = fragment.Fragment(
                    self.file.get_fragment(0, left_index - 1))
                end = fragment.Fragment(
                    self.file.get_fragment(left_index, length))
                end.reverse()
                self.file.channels = fragment.concatenate_fragments(
                    [start, end])
            else:
                start = fragment.Fragment(
                    self.file.get_fragment(0, left_index - 1))
                fr = fragment.Fragment(
                    self.file.get_fragment(left_index, right_index))
                fr.reverse()
                end = fragment.Fragment(
                    self.file.get_fragment(right_index + 1, length))
                self.file.channels = fragment.concatenate_fragments(
                    [start, fr, end])
            self.draw_track()

    def clear_fragments(self, e):
        self.fragments = []
        self.draw_fragments()

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

    def collect_all_fragments_to_one(self, e):
        if len(self.fragments) < 2:
            self.show_notification("There must be 2+ fragments to collect",
                                   "Error!")
            return
        temp_type = self.file.channels[0].dtype
        self.file.channels = fragment.collect_fragments_to_one(self.fragments,
                                                               temp_type)
        self.file.filename = "United mix"
        self.file.subchunk2Size = len(
            self.file.channels[0]) * self.file.bitsPerSample // 4
        self.file.chunkSize = self.file.subchunk2Size + 36
        self.draw_track()

    def concat_and_move(self, e):
        if len(self.fragments) < 2:
            self.show_notification("There must be 2+ fragments to collect",
                                   "Error!")
            return
        compilation = fragment.concatenate_fragments(self.fragments)
        self.file.filename = "Concatenated mix"
        self.file.channels = compilation
        self.file.subchunk2Size = len(
            self.file.channels[0]) * self.file.bitsPerSample // 4
        self.file.chunkSize = self.file.subchunk2Size + 36
        self.draw_track()

    def info(self, e):
        if self.file is None:
            message = "No file!"
        else:
            message = "Track: {0}\n".format(self.file.filename)
            message += self.file.get_info()
        self.show_notification(message, "Files")

    def show_notification(self, message, topic):
        dlg = wx.MessageDialog(self, message, topic, wx.OK)
        dlg.ShowModal()

    def play(self, e):
        if self.file is None:
            return
        thread = threading.Thread(target=self.start_player,
                                  daemon=True)
        thread.start()
        self.show_player_dialog()

    def show_player_dialog(self):
        dlg = wx.MessageDialog(self, "Playing highlighted fragment",
                               "Player", wx.OK)
        if dlg.ShowModal() == wx.ID_OK:
            if not self.is_playing:
                dlg.Close()
            else:
                self.show_player_dialog()

    def start_player(self):
        self.is_playing = True
        try:
            player = pyaudio.PyAudio()
            stream = player.open(
                format=player.get_format_from_width(
                    self.file.bitsPerSample // 8),
                channels=self.file.numChannels,
                rate=self.file.sampleRate,
                output=True)
            max = self.start_slider.GetMax()
            left_border = self.start_slider.GetValue()
            right_border = self.end_slider.GetValue()
            if left_border > right_border:
                left_border, right_border = right_border, left_border
            length = len(self.file.channels[0])
            start = length // max * left_border
            end = length // max * right_border
            stream.write(self.file.fragment_to_frames(start, end))
            stream.stop_stream()
            stream.close()
            player.terminate()
        except Exception:
            self.show_notification("Something went wrong!", "Error!")
        self.is_playing = False
