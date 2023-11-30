import os

from tkinter import *
from tkinter.ttk import Progressbar

from modules.GUI.generic_GUI import GUI, RowGenerator, FileImport
from modules.utils import config


class SpinnerGUI(GUI):
    def __init__(self, base):
        self.base = base
        self.root = GUI.create_toplevel(root=base, title="RTR2HEM Tool")
        try:
            self.main()
        except Exception as e:
            self.error()

    def main(self):
        self.gen = RowGenerator()

        title_lbl = Label(self.root, text="Running tool...", font=16, justify=LEFT)
        title_lbl.grid(row=self.gen.next(), columnspan=10, padx=10)

        self.loader = Progressbar(
            self.root,
            orient="horizontal",
            mode="determinate",
            length=280,
            value=0,
            maximum=100,
        )
        self.loader.grid(column=0, row=self.gen.next(), sticky=EW)

        self.status_msg = Label(self.root, text="", font=("", 11), justify=LEFT)
        self.status_msg.grid(row=self.gen.next(), sticky=W)

    def update(self, msg, val):
        if val >= 100:
            val = 99.9
        self.status_msg.configure(text=msg)
        self.loader.step(val)
        self.base.update()
