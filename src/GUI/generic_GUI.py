import os
import gc
import pathlib
import traceback
import logging
from tkinter import *
from tkinter import filedialog
import tkinter.messagebox

import pandas as pd
from src.accdb_manager import AccdbManager


class ErrorHandling:
    def __init__(self):
        pass

    @staticmethod
    def note(title, msg):
        tkinter.messagebox.showinfo(
            title=title,
            message=msg,
        )

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
        tkinter.messagebox.showerror("Exception", errorMsg)
        root.destroy()
        root.mainloop()
        logging.exception(errorMsg)


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
        ("JSON Source File", ".json"),
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
        self.import_btn = Button(
            self.root,
            text=btn_name,
            command=lambda: self.import_file(),
        )
        self.import_btn.grid(row=self.row.next(), padx=(5, 0), pady=(5, 0), sticky=W)
        spacing = GUI.width(self, self.import_btn) + 10

        # filepath
        self.file_lbl = Label(
            self.root, text="", bg="#ffffff", borderwidth=1, relief=GROOVE, width=42
        )
        self.file_lbl.grid(row=self.row.current(), padx=(spacing, 0), sticky=W)

        # filename
        self.table_lbl = Label(
            self.root, text="", bg="#ffffff", borderwidth=1, relief=GROOVE, width=42
        )
        self.table_lbl.grid(
            row=self.row.next(), padx=(spacing, 5), pady=(0, 5), sticky=W
        )
        return self

    def toplevel_btns(self, toplevel=None, type="OK"):
        """Close window, update filepath/name labels"""
        if self.table_var:
            self.table = self.table_var.get()
        if type == "Cancel":
            self.filepath = ""
            self.filename = ""
            self.table = ""

        self.file_lbl.config(
            text=GUI.split_str(self, 42, self.filename)[0],
            justify=LEFT,
        )
        self.table_lbl.config(
            text=GUI.split_str(self, 42, self.table)[0],
            justify=LEFT,
        )

        if toplevel:
            toplevel.destroy()

    def tables_popup(self, tables):
        """Display list of tables in file"""
        popup_root = Toplevel(self.root)
        gen = RowGenerator()

        x = self.root.winfo_rootx()
        y = self.root.winfo_rooty()
        popup_root.geometry("+%d+%d" % (x - 200, y - 200))

        popup_root.attributes("-topmost", True)
        popup_root.title(f"{self.filename} - Table Select")

        Label(
            popup_root,
            text="Select the table for the emission inventory file.",
        ).grid(row=gen.next(), sticky=W)

        # widgets
        ok_btn = Button(
            popup_root,
            text="OK",
            command=lambda: self.toplevel_btns(popup_root, type="OK"),
        )
        ok_btn.grid(sticky=W, row=gen.next(), padx=(5, 5), pady=(5, 1))

        cancel_btn = Button(
            popup_root,
            text="Cancel",
            command=lambda: self.toplevel_btns(popup_root, type="Cancel"),
        )
        cancel_btn.grid(sticky=W, row=gen.current(), padx=(40, 5), pady=(5, 1))

        # list of tables
        sbf = ScrollbarFrame(popup_root)
        frame = sbf.scrolled_frame
        sbf.grid(row=gen.next(), column=0, sticky="nsew")

        self.table_var = StringVar(frame, tables[0])
        for table in tables:
            Radiobutton(frame, text=table, variable=self.table_var, value=table).grid(
                sticky=W
            )

    def import_file(self):
        """Select file, trigger table popup"""
        if self.required_columns:
            GUI.note(
                title="NOTE",
                msg=f"Imported table must contain the following columns:\n{self.required_columns}",
            )

        filepath = filedialog.askopenfilename(
            initialdir=self.working_dir  # , filetypes=self.ftypes
        )
        if filepath:
            self.filepath = filepath
            self.filename = pathlib.Path(filepath).stem
            ftype = pathlib.Path(self.filepath).suffix
            tables = []

            if ftype == ".accdb":
                reader = AccdbManager(self.filepath, how="open")
                tables = reader.get_tables()
            elif ftype == ".xlsx":
                reader = pd.ExcelFile(self.filepath)
                sheets = reader.book.worksheets
                for sheet in sheets:
                    if sheet.sheet_state == "visible":
                        tables.append(sheet.title)
            elif ftype == ".csv":
                file_str, h = GUI.split_str(self, 40, self.filename)
                self.file_lbl.config(text=file_str)
                return
            elif ftype == ".json":
                file_str, h = GUI.split_str(self, 40, self.filename)
                self.file_lbl.config(text=file_str)
                return
            else:
                GUI.warn(self, msg=f"Invalid filetype '{ftype}'.")
                return

            if not tables:
                return
            self.tables_popup(tables)


class RowGenerator:
    def __init__(self, start=-1):
        self.row = start

    def next(self):
        self.row += 1
        return self.row

    def current(self):
        return self.row

    def prev(self):
        if self.row > 0:
            self.row -= 1
        return self.row


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
        self.root.attributes("-topmost", True)

    def width(self, widget):
        widget.update()
        return widget.winfo_width()

    def split_str(self, w, val):
        """Resize widgets and split strings based on width constraint"""
        result = ""
        height = 1
        while len(val) > w:
            height += 1
            result += f"{val[:w]}\n"
            val = val[w:]
        result += val
        return result, height

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

    """
    toplevel specific helper methods
    """

    def pause_for_toplevel(self, toplevel):
        toplevel.grab_set()
        self.root.wait_window(toplevel)
        toplevel.grab_release()
        gc.collect()

    def create_toplevel(self, title=""):
        popup_root = Toplevel(self.root)

        x = self.root.winfo_x()
        y = self.root.winfo_y()
        popup_root.geometry("+%d+%d" % (x - 100, y - 100))
        self.root.update_idletasks()
        popup_root.attributes("-topmost", True)
        popup_root.title(title)

        def on_closing():
            self.root.destroy()  # Close Tkinter window
            os._exit(0)  # Forecefully quit PY

        popup_root.protocol("WM_DELETE_WINDOW", on_closing)
        return popup_root
