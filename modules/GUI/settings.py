import os
import threading

from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Style

from modules.run import RTR2HEM
from modules.GUI.generic_GUI import GUI, RowGenerator, FileImport
from modules.utils import config


class SettingsGUI(GUI):
    green = "#69c14c"
    blue = "#00538b"
    white = "#ffffff"
    grey = "#d0d0d0"

    def __init__(self):
        super().__init__(title="RTR2HEM Tool")
        try:
            self.root.configure(background=self.blue)
            self.main()
        except Exception as e:
            self.error()

    def main(self):
        self.gen = RowGenerator()
        Style().theme_use("alt")

        subroot = self.settings_option()
        self.config_import()
        self.name_and_base_import(subroot)
        self.import_existing_epg_srcid(subroot)
        self.emissions_type(subroot)
        self.records_type(subroot)

        qa_btn = self.qa()
        qa_btn_width = self.width(qa_btn)

        # Submit
        self.run_setup = Button(
            self.root,
            text="Run setup",
            command=lambda: threading.Thread(
                target=self.run_settings, daemon=True
            ).start(),
        )
        self.run_setup.grid(
            row=self.gen.current(),
            column=0,
            pady=(5, 5),
            padx=(20 + qa_btn_width, 10),
            sticky=W,
        )

        super().main()

    def settings_option(self):
        def enableOptions(parent):
            for child in parent.winfo_children():
                wtype = child.winfo_class()
                if wtype not in ("Frame", "Labelframe"):
                    child.configure(state="normal")
                else:
                    enableOptions(child)

            self.subroot_config.grid_forget()
            subroot.grid(row=subroot_row, columnspan=10, padx=10)

        def disableOptions(parent):
            for child in parent.winfo_children():
                wtype = child.winfo_class()
                if wtype not in ("Frame", "Labelframe"):
                    child.configure(state="disable")
                else:
                    disableOptions(child)

            self.subroot_config.grid(row=subroot_row, columnspan=10, padx=10)
            subroot.grid_forget()

        self.option_var = StringVar(self.root, "0")
        read_user_opts = Radiobutton(
            self.root,
            text="Run setup from input fields",
            variable=self.option_var,
            value=0,
            fg=self.white,
            selectcolor="black",
            background=self.blue,
            command=lambda: enableOptions(subroot),
        )
        read_config = Radiobutton(
            self.root,
            text="Run setup from config",
            variable=self.option_var,
            value=1,
            fg=self.white,
            selectcolor="black",
            background=self.blue,
            command=lambda: disableOptions(subroot),
        )

        read_user_opts.grid(row=self.gen.next(), column=0, padx=(12, 0), sticky=W)

        config_padx_left = self.width(read_user_opts) + 20
        read_config.grid(
            row=self.gen.current(), column=0, padx=(config_padx_left, 0), sticky=W
        )

        subroot = LabelFrame(
            self.root,
            text="Settings",
            font=16,
            bg=self.grey,
            borderwidth=2,
            relief="groove",
        )
        subroot.grid(row=self.gen.next(), columnspan=10, padx=10)
        subroot_row = self.gen.current()
        return subroot

    def config_import(self):
        self.subroot_config = LabelFrame(
            self.root,
            text="Settings",
            font=16,
            bg=self.grey,
            borderwidth=2,
            relief="groove",
        )
        self.subroot_config.grid(row=self.gen.next(), columnspan=10, padx=10)

        self.import_config = FileImport(self.subroot_config, self.gen).create()
        self.import_config.filepath = ".\config.json"
        self.import_config.file_lbl.config(text=".\config.json")

        self.import_config.table_lbl.grid_forget()
        self.subroot_config.grid_forget()

    def name_and_base_import(self, root):
        # Source Category (output files) name
        src_cat_label = Label(root, text="Source Catgeory name", bg=self.grey)
        src_cat_label.grid(row=self.gen.next(), column=0, padx=(0, 0), sticky=W)

        self.src_cat_name = Entry(root, width=40)
        src_cat_padx_left = self.width(src_cat_label) + 10
        self.src_cat_name.grid(
            row=self.gen.current(), padx=(src_cat_padx_left, 5), sticky=W
        )

        # accdb and table select
        self.import_table = FileImport(root, self.gen).create()

        # output dir
        def dir_select():
            self.output_fp = filedialog.askdirectory()
            out_lbl.config(text=GUI.split_str(self, 42, self.output_fp)[0])

        self.output_fp = os.getcwd()
        out_btn = Button(root, text="Output Dir", command=dir_select)
        out_btn.grid(row=self.gen.next(), padx=(5, 0), pady=(5, 5), sticky=W)
        out_lbl = Label(
            root,
            text=GUI.split_str(self, 42, self.output_fp)[0],
            bg="#ffffff",
            borderwidth=1,
            relief=GROOVE,
            width=42,
            justify=LEFT,
        )
        out_lbl.grid(
            row=self.gen.current(), padx=(GUI.width(self, out_btn) + 10, 0), sticky=W
        )

    def import_existing_epg_srcid(self, root):
        # Import existing EPGs and Source IDs
        import_subroot = LabelFrame(
            root,
            text="Import (optional)",
            font=16,
            borderwidth=3,
            relief="groove",
        )
        import_subroot.grid(row=self.gen.next(), padx=(5, 0), pady=(10, 10), sticky=W)

        Label(
            import_subroot,
            text="Import previously generated emission process group abbreviations",
        ).grid(row=self.gen.next(), sticky=W)
        self.epgs = FileImport(
            import_subroot,
            self.gen,
            required_columns=config.epg_required,
        ).create()

        Label(import_subroot, text="Import previously generated SourceIDs").grid(
            row=self.gen.next(), sticky=W
        )
        self.srcids = FileImport(
            import_subroot, self.gen, required_columns=config.srcid_required
        ).create()

        def clear():
            FileImport.toplevel_btns(self.epgs, type="Cancel")
            FileImport.toplevel_btns(self.srcids, type="Cancel")

        Button(import_subroot, text="Clear", command=clear).grid(
            row=self.gen.next(), padx=(5, 0), pady=(0, 5), sticky=W
        )

    def emissions_type(self, root):
        # Emissions choice
        self.emissions_subroot = LabelFrame(
            root,
            text="Emissions Type",
            font=16,
            borderwidth=3,
            relief="groove",
        )
        self.emissions_subroot.grid(row=self.gen.next(), padx=(5, 5), sticky=W)
        self.emiss_var = StringVar(value="Actual")

        self.emissions_subroot_row = self.gen.current()

        actual = Radiobutton(
            self.emissions_subroot,
            text="Actual Emissions",
            variable=self.emiss_var,
            value="Actual",
        )
        actual.grid(row=self.gen.next(), sticky=W)

        allowable = Radiobutton(
            self.emissions_subroot,
            text="Allowable Emissions",
            variable=self.emiss_var,
            value="Allowable",
        )
        allowable.grid(row=self.gen.next(), sticky=W)

        acute = Radiobutton(
            self.emissions_subroot,
            text="Acute Emissions",
            variable=self.emiss_var,
            value="Acute",
        )
        acute.grid(row=self.gen.next(), sticky=W)

    def records_type(self, root):
        # Category/Whole Records choice
        records_subroot = LabelFrame(
            root,
            text="Records Type",
            font=16,
            borderwidth=3,
            relief="groove",
        )
        emiss_subroot_width = self.width(self.emissions_subroot) + 10
        records_subroot.grid(
            row=self.emissions_subroot_row, padx=(emiss_subroot_width, 5), sticky=W
        )
        self.records_var = StringVar(value="Cat")

        cat_only = Radiobutton(
            records_subroot,
            text="File only has category records",
            variable=self.records_var,
            value="Cat",
        )
        cat_only.grid(sticky=W)

        cat_whole = Radiobutton(
            records_subroot,
            text="File has category and non-category records",
            variable=self.records_var,
            value="CatWhole",
        )
        cat_whole.grid(sticky=W)

    def qa(self):
        self.qa_var = IntVar()
        qa_btn = Checkbutton(
            self.root,
            text="Include QA",
            height=1,
            onvalue=1,
            offvalue=0,
            variable=self.qa_var,
        )
        qa_btn.grid(row=self.gen.next(), column=0, padx=(10, 10), sticky=W)
        return qa_btn

    def run_settings(self):
        self.run_setup.config(state=DISABLED)
        config.run_qa = self.qa_var.get()

        # load from file
        if self.option_var.get() == "1":
            config.load_config(fp=self.import_config.filepath)
        else:
            if not self.src_cat_name.get():
                self.warn(msg="Source Category name must not be empty")
                self.run_setup.config(state=NORMAL)
                return

            if not self.import_table.filepath:
                self.warn(msg="No file selected to import")
                self.run_setup.config(state=NORMAL)
                return

            settings_json = {
                "settings": {
                    "source_category_name": self.src_cat_name.get(),
                    "only_category_records": True
                    if self.records_var.get() == "Cat"
                    else False,
                    "emission_type": self.emiss_var.get(),
                    "emission_abbr": {
                        "import": True if self.epgs.filepath else False,
                        "file": self.epgs.filepath,
                        "table": self.epgs.table,
                    },
                    "src_ids": {
                        "import": True if self.srcids.filepath else False,
                        "file": self.srcids.filepath,
                        "table": self.srcids.table,
                    },
                    "input_file": self.import_table.filepath,
                    "input_table": self.import_table.table,
                    "output_dir": self.output_fp,
                    "static": "./static",
                }
            }

            try:
                config.load_config(obj=settings_json)
            except Exception as e:
                self.error(e)
                self.run_setup.config(state=NORMAL)
                return

        columns_need_mapping = self.option_var.get() == "0"
        RTR2HEM(self.root, columns_need_mapping)
        self.close_window()
        exit()
