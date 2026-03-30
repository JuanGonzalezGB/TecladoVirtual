#!/usr/bin/env python3
import sys
import tkinter as tk

from modelo import config
from vista.app import App


def main():
    # override opcional desde CLI
    if len(sys.argv) > 1:
        config.set_theme(sys.argv[1])

    root = tk.Tk()
    app = App(root, config)

    root.mainloop()


if __name__ == "__main__":
    main()