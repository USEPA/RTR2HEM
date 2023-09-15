import os
import gc
import re
import math
import pathlib
import traceback
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

    def error(self, errorMsg=None):
        if not errorMsg:
            errorMsg = traceback.format_exc()
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
        self.frame_id = self.canvas.create_window(
            (4, 4), window=self.scrolled_frame, anchor="nw"
        )

        # Configures the scrollregion of the Canvas dynamically
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.scrolled_frame.bind("<Configure>", self.on_frame_configure)

        # Mousewheel scroll
        self.scrolled_frame.bind("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        if self.vsb.get() == (0, 1):  # disabled
            return
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.frame_id, width=event.width)

    def on_frame_configure(self, event):
        """Set the scroll region to encompass the scrolled frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


class FileImport:
    """
    Creates four widgets:
        1. Import file option
        2. Popup menu that dynamically updates with the tables in the imported file
        3. Two labels for selected choice
    """

    working_dir = os.getcwd()
    ftypes = [
        ("Microsoft Access Database", "*.accdb"),
        ("Excel files", ".xlsx"),
        ("CSV Files", "*.csv"),
    ]

    filepath = ""
    table = ""
    table_var = None

    def __init__(self, root, row, required_columns=None):
        self.root = root
        self.row = row
        if required_columns:
            self.required_columns = "\n".join(required_columns)
        else:
            self.required_columns = None

    def create(self, btn_name="Import File"):
        """Initial button/labels widget create"""
        current_row = next(self.row)

        self.import_btn = Button(
            self.root,
            text=btn_name,
            command=lambda: self.import_file(),
        )
        self.import_btn.grid(row=current_row, padx=(5, 0), pady=(5, 0), sticky=W)
        spacing = GUI.width(self, self.import_btn) + 10

        # filepath
        self.file_lbl = Label(
            self.root, text="", bg="#ffffff", borderwidth=1, relief=GROOVE, width=42
        )
        self.file_lbl.grid(row=current_row, padx=(spacing, 0), sticky=W)

        # filename
        self.table_lbl = Label(
            self.root, text="", bg="#ffffff", borderwidth=1, relief=GROOVE, width=42
        )
        self.table_lbl.grid(
            row=next(self.row), padx=(spacing, 5), pady=(0, 5), sticky=W
        )
        return self

    def toplevel_btns(self, toplevel, type):
        """Close window, update filepath/name labels"""
        self.table = self.table_var.get()
        if type == "Cancel":
            self.filepath = ""
            self.filename = ""
            self.table = ""
        self.file_lbl.config(text=self.filename)
        self.table_lbl.config(text=self.table)
        toplevel.destroy()

    def tables_popup(self, tables):
        """Display list of tables in file"""
        popup_root = Toplevel(self.root)

        x = self.root.winfo_rootx()
        y = self.root.winfo_rooty()
        popup_root.geometry("+%d+%d" % (x - 200, y - 200))

        popup_root.title(f"{self.filename} - Table Select")

        # widgets
        ok_btn = Button(
            popup_root,
            text="OK",
            command=lambda: self.toplevel_btns(popup_root, type="OK"),
        )
        ok_btn.grid(sticky=W, row=0, padx=(5, 5), pady=(5, 1))

        cancel_btn = Button(
            popup_root,
            text="Cancel",
            command=lambda: self.toplevel_btns(popup_root, type="Cancel"),
        )
        cancel_btn.grid(sticky=W, row=0, padx=(40, 5), pady=(5, 1))

        # list of tables
        sbf = ScrollbarFrame(popup_root)
        frame = sbf.scrolled_frame
        sbf.grid(row=1, column=0, sticky="nsew")

        self.table_var = StringVar(frame, tables[0])
        for table in tables:
            Radiobutton(frame, text=table, variable=self.table_var, value=table).grid(
                sticky=W
            )

    def import_file(self):
        """Select file, trigger table popup"""
        if self.required_columns:
            ErrorHandling.warn(
                self,
                title="NOTE",
                msg=f"Imported table must contain the following columns:\n{self.required_columns}",
            )

        filepath = filedialog.askopenfilename(
            initialdir=self.working_dir, filetypes=self.ftypes
        )
        if filepath:
            self.filepath = filepath
            self.filename = pathlib.Path(filepath).stem
            ftype = pathlib.Path(self.filepath).suffix
            tables = []

            if ftype == ".accdb":
                reader = AccdbHandle(self.filepath, how="open")
                tables = reader.get_tables()
            elif ftype == ".xlsx":
                reader = pd.ExcelFile(self.filepath)
                sheets = reader.book.worksheets
                for sheet in sheets:
                    if sheet.sheet_state == "visible":
                        tables.append(sheet.title)
            elif ftype == ".csv":
                self.file_lbl.config(text=self.filename)
                return
            else:
                return

            if not tables:
                return
            self.tables_popup(tables)


class GUI(ErrorHandling):
    root = None
    scrollbar = ScrollbarFrame

    def __init__(self, title="", dimensions=None):
        self.root = Tk()
        self.root.resizable(False, False)
        self.root.eval("tk::PlaceWindow . center")

        self.root.title(title)
        if dimensions:
            self.root.geometry(dimensions)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.focus_force()

    def row_generator(self):
        rownum = 0
        while True:
            self.current_gen = rownum
            yield rownum
            rownum = rownum + 1

    def width(self, widget):
        widget.update()
        return widget.winfo_width()

    def update_box_height(self, widget, w, h=1):
        text_length = str(widget.index("1.end"))
        text_length = int(re.search(".(\d+)", text_length).group(1))
        new_height = math.floor(text_length / w)
        widget.config(height=new_height + h)

    def close_window(self):
        self.root.destroy()
        self.root = None
        gc.collect()

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
