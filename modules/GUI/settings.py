import os, pathlib
from tkinter import *
from tkinter import filedialog
from .generic_GUI import GUI

from modules.handle_accdb import AccdbHandle


class SettingsGUI(GUI):
    def __init__(self):
        super().__init__(title="Settings")
        try:
            self.main()
        except Exception as e:
            self.error(e)

    def disableChildren(self, parent):
        for child in parent.winfo_children():
            wtype = child.winfo_class()
            if wtype not in ("Frame", "Labelframe"):
                child.configure(state="disable")
            else:
                self.disableChildren(child)

    def enableChildren(self, parent):
        for child in parent.winfo_children():
            wtype = child.winfo_class()
            if wtype not in ("Frame", "Labelframe"):
                child.configure(state="normal")
            else:
                self.enableChildren(child)

    def import_file(self, subroot, gen):
        working_dir = os.getcwd()
        ftypes = [("Microsoft Access Database", "*.accdb"), ("Excel files", ".xlsx")]
        filepath = filedialog.askopenfilename(initialdir=working_dir, filetypes=ftypes)

        if pathlib.Path(filepath).suffix == ".accdb":
            accdb_reader = AccdbHandle(filepath, how="open")
            tables = accdb_reader.get_tables()

            variable = StringVar(subroot)
            variable.set(tables[0])  # default value
            w = OptionMenu(subroot, variable, *tables)
            w.grid(row=next(gen), column=0, columnspan=10)

    def clear_all(self, is_checked, regCodes):
        for regCode in regCodes:
            regCode.set(0)
        is_checked.set(0)

    def select_all(self, is_checked, regCode_button_list):
        for regCode in regCode_button_list:
            if is_checked.get():
                regCode.set(1)
            else:
                regCode.set(0)

    def main(self):
        regCode_button_list = []

        gen = self.row_generator()

        subroot = LabelFrame(
            self.root,
            text="Config options\n",
            font=16,
            borderwidth=2,
            relief="groove",
        )

        option_var = StringVar(self.root, "0")
        read_user_opts = Radiobutton(
            self.root,
            text="Run setup from input fields",
            variable=option_var,
            value=0,
            command=lambda: self.enableChildren(subroot),
        )
        read_config = Radiobutton(
            self.root,
            text="Run setup from config.json",
            variable=option_var,
            value=1,
            command=lambda: self.disableChildren(subroot),
        )
        read_user_opts.grid(row=next(gen), column=0, padx=(12, 0), sticky=W)
        read_config.grid(row=self.current_gen, column=1, pady=(10), sticky=W)
        subroot.grid(row=next(gen), column=0, columnspan=10, padx=10)

        src_cat_name_label = Label(subroot, text="Source Catgeory name")
        src_cat_name_label.grid(row=next(gen), column=0, padx=(0, 0), sticky=W)

        src_cat_name_textbox = Entry(subroot, width=50)
        src_cat_name_textbox.grid(row=self.current_gen, column=1, sticky=W)

        select_input_file_btn = Button(
            subroot,
            text="Import a file",
            command=lambda: self.import_file(subroot, gen),
        )
        select_input_file_btn.grid(row=next(gen), sticky=W)

        select_all_var = IntVar()
        select_all_btn = Checkbutton(
            subroot,
            text="Select all",
            height=2,
            onvalue=1,
            offvalue=0,
            variable=select_all_var,
            command=lambda: self.select_all(select_all_var, regCode_button_list),
        )
        select_all_btn.grid(row=next(gen), column=0, padx=(10, 10), sticky=W)

        clear_all_btn = Button(
            subroot,
            text="Clear all",
            command=lambda: self.clear_all(select_all_var, regCode_button_list),
        )
        clear_all_btn.grid(
            row=next(gen), column=0, pady=(0, 5), padx=(10, 10), sticky=W
        )

        super().main()
