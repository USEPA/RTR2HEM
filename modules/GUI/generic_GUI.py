import os, pathlib
from tkinter import *
from tkinter import filedialog
import tkinter.messagebox

import pandas as pd
from modules.handle_accdb import AccdbHandle


class ErrorHandling:
    def __init__(self):
        pass

    def warn(self, title="Warning", msg=""):
        tkinter.messagebox.showwarning(
            title=title,
            message=msg,
        )
        return

    def error(self, errorMsg):
        root = Tk()
        tkinter.messagebox.showinfo("Exception", errorMsg)
        root.destroy()
        root.mainloop()

        raise Exception(errorMsg)


class ScrollbarFrame(Frame):
    """
    Extends class Frame to support a scrollable Frame
    This class is independent from the widgets to be scrolled and
    can be used to replace a standard Frame

    https://stackoverflow.com/questions/3085696/adding-a-scrollbar-to-a-group-of-widgets-in-tkinter/3092341#3092341
    """

    def __init__(self, parent, bg_color="#ffffff", **kwargs):
        Frame.__init__(self, parent, **kwargs)

        # The Scrollbar, layout to the right
        self.vsb = Scrollbar(self, orient="vertical")
        self.vsb.pack(side="right", fill="y")

        # The Canvas which supports the Scrollbar Interface, layout to the left
        self.canvas = Canvas(self, borderwidth=0, background=bg_color)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Bind the Scrollbar to the self.canvas Scrollbar Interface
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.configure(command=self.canvas.yview)

        # The Frame to be scrolled, layout into the canvas
        # All widgets to be scrolled have to use this Frame as parent
        self.scrolled_frame = Frame(self.canvas, background=self.canvas.cget("bg"))
        self.canvas.create_window((4, 4), window=self.scrolled_frame, anchor="nw")

        # Configures the scrollregion of the Canvas dynamically
        self.scrolled_frame.bind("<Configure>", self.on_configure)

        # Mousewheel scroll
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        if self.vsb.get() == (0, 1):  # disabled
            return
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_configure(self, event):
        """Set the scroll region to encompass the scrolled frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


class FileImport:
    """
    Creates two widgets:
        1. Import file option
        2. Dropdown menu that dynamically updates with the tables in the imported file
    """

    working_dir = os.getcwd()
    ftypes = [("Microsoft Access Database", "*.accdb"), ("Excel files", ".xlsx")]

    def __init__(self, root, init_list=None):
        self.opts = [""] if not init_list else init_list
        self.root = root

    def create(self):
        tables_var = StringVar(self.root)
        tables_var.set(self.opts[0])  # default value
        tables_menu = OptionMenu(self.root, tables_var, *self.opts)

        import_btn = Button(
            self.root,
            text="Import File",
            command=lambda: self.import_file(tables_menu, tables_var),
        )

        return import_btn, tables_menu

    def import_file(self, dropdown, var):
        menu = dropdown["menu"]
        menu.delete(0, "end")

        filepath = filedialog.askopenfilename(
            initialdir=self.working_dir, filetypes=self.ftypes
        )
        tables = []

        if pathlib.Path(filepath).suffix == ".accdb":
            reader = AccdbHandle(filepath, how="open")
            tables = reader.get_tables()
        elif pathlib.Path(filepath).suffix == ".xlsx":
            reader = pd.ExcelFile(filepath)
            sheets = reader.book.worksheets
            for sheet in sheets:
                if sheet.sheet_state == "visible":
                    tables.append(sheet.title)
        else:
            return

        for table in tables:
            menu.add_command(label=table, command=lambda name=table: var.set(name))
        var.set(tables[0])


class GUI(ErrorHandling):
    root = None
    scrollbar = ScrollbarFrame

    def __init__(self, title="", dimensions=None):
        self.root = Tk()

        self.root.eval("tk::PlaceWindow . center")
        self.root.title(title)
        if dimensions:
            self.root.geometry(dimensions)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def row_generator(self):
        rownum = 0
        while True:
            self.current_gen = rownum
            yield rownum
            rownum = rownum + 1

    def width(self, widget):
        widget.update()
        return widget.winfo_width()

    def close_window(self):
        self.root.destroy()

    def bind_entries(self, entries):
        """
        Hitting 'enter' will move typing to next entry
        """

        def go_to_next_entry(event, entry_list, this_index):
            next_index = (this_index + 1) % len(entry_list)
            entry_list[next_index].focus_set()

        for idx, entry in enumerate(entries):
            entry.bind("<Return>", lambda e, idx=idx: go_to_next_entry(e, entries, idx))

    def main(self):
        def on_closing():
            self.root.withdraw()  # Close Tkinter window
            os._exit(0)  # Forecefully quit PY

        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        self.root.mainloop()
