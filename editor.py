import CLI
import GUI
import wx
import sys


def main():
    if len(sys.argv) == 1:
        print("USAGE:")
        print("-c or --console - Launch editor with console control")
        print("-g or --gui - Launch editor in user interface")
        return
    if sys.argv[1] == "-c" or sys.argv[1] == "--console":
        cli = CLI.CLI()
        cli.start()
    elif sys.argv[1] == "-g" or sys.argv[1] == "--gui":
        app = wx.App()
        window = GUI.GUI(None, "WAV editor")
        app.MainLoop()


if __name__ == '__main__':
    main()
