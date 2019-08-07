"""The TKGFX module is a simple wrapper over the tkinter interface with
the intent of providing a more streamlined experience for use cases
dealing prodomenantly with graphics."""

__version__ = "1.0.0"

import tkinter as tk

class GWin(tk.Tk):
    def __init__(self, width=640, height=480, title="untitled"):
        super(tk.Tk, self).__init__()
        
        


def main():
    gwin = GWin()
    gwin.mainloop()

if __name__ == "__main__":
    main()
