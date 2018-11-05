import CLI
import GUI
import wx


def main():
    # cli = CLI.CLI()
    # cli.start()
    app = wx.App()
    window = GUI.GUI(None, "WAV editor")
    app.MainLoop()


if __name__ == '__main__':
    main()
