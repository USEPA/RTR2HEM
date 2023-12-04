from tkinter import *
from tkinter.ttk import Progressbar

from modules.GUI.generic_GUI import GUI, RowGenerator
from modules.utils import config


class statusGUI(GUI):
    NUM_STEPS = 5  # 6 if qa
    step_tracker = 0

    def __init__(self, base):
        self.root = base
        self.toplevel = self.create_toplevel(title="RTR2HEM Tool")
        self.toplevel.geometry("230x100")
        try:
            self.main()
        except Exception as e:
            self.error()

    def main(self):
        if config.run_qa:
            self.NUM_STEPS += 1

        self.gen = RowGenerator()

        title_lbl = Label(self.toplevel, text="Running tool...", font=16)
        title_lbl.grid(row=self.gen.next(), padx=(15, 0))

        self.loader = Progressbar(
            self.toplevel,
            orient="horizontal",
            mode="determinate",
            length=200,
            value=0.0,
            maximum=100.0,
        )
        self.loader.grid(column=0, row=self.gen.next(), padx=(15, 0), sticky=EW)

        self.status_msg = Label(self.toplevel, text="", font=("", 9))
        self.status_msg.grid(row=self.gen.next(), padx=(15, 0), sticky=W)

        self.root.withdraw()  # hide root
        self.toplevel.resizable(False, False)

    def update(self, msg):
        if self.step_tracker == 0:
            val = 0
        elif self.step_tracker == self.NUM_STEPS:
            val = 99.9
        else:
            val = 100 / self.NUM_STEPS
        self.step_tracker += 1

        if self.loader["value"] + val >= 100:
            self.loader["value"] = 99.9
        else:
            self.loader.step(val)

        self.status_msg.configure(text=msg, justify=LEFT)
        self.root.update()
