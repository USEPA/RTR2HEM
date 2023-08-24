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

    def main(self):
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
        src_cat_name_textbox.grid(row=self.current_gen, padx=(150, 0), sticky=W)

        ##############################################################
        # accdb and table select

        tables_var = StringVar(subroot)
        tables_var.set("")  # default value
        tables_menu = OptionMenu(subroot, tables_var, *[""])

        select_input_file_btn = Button(
            subroot,
            text="Import File",
            command=lambda: self.import_file(tables_menu, tables_var),
        )
        select_input_file_btn.grid(row=next(gen), sticky=W)
        tables_menu.grid(row=next(gen), sticky=W, columnspan=10)

        ##############################################################
        # Import existing

        epg_var = IntVar()
        import_epg_btn = Checkbutton(
            subroot,
            text="Import previously generated emission process group abbreviations",
            height=1,
            onvalue=1,
            offvalue=0,
            variable=epg_var,
            # command=lambda: self.select_all(select_all_var, regCode_button_list),
        )
        import_epg_btn.grid(row=next(gen), column=0, padx=(10, 10), sticky=W)

        srcid_var = IntVar()
        import_srcid_btn = Checkbutton(
            subroot,
            text="Import previously generated SourceIDs",
            height=1,
            onvalue=1,
            offvalue=0,
            variable=srcid_var,
            # command=lambda: self.select_all(select_all_var, regCode_button_list),
        )
        import_srcid_btn.grid(row=next(gen), column=0, padx=(10, 10), sticky=W)

        ##############################################################
        # Emissions choice

        emissions_subroot = LabelFrame(
            subroot,
            text="Emissions Type",
            font=16,
            borderwidth=2,
            relief="groove",
        )
        emissions_subroot.grid(row=next(gen), sticky=W)
        emiss_var = StringVar(value="Actual")

        actual = Radiobutton(
            emissions_subroot,
            text="Actual Emissions",
            variable=emiss_var,
            value="Actual",
        )
        actual.grid(row=next(gen), sticky=W)

        allowable = Radiobutton(
            emissions_subroot,
            text="Allowable Emissions",
            variable=emiss_var,
            value="Allowable",
        )
        allowable.grid(row=next(gen), sticky=W)

        acute = Radiobutton(
            emissions_subroot, text="Acute Emissions", variable=emiss_var, value="Acute"
        )
        acute.grid(row=next(gen), sticky=W)

        ##############################################################

        run_setup = Button(
            self.root,
            text="Run setup",
            # command=lambda: self.run_setup(option_var, rename_args),
        )
        run_setup.grid(row=next(gen), column=0, pady=(5, 5), padx=(10, 10), sticky=W)

        super().main()

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

    def import_file(self, dropdown, var):
        menu = dropdown["menu"]
        menu.delete(0, "end")

        working_dir = os.getcwd()
        ftypes = [("Microsoft Access Database", "*.accdb"), ("Excel files", ".xlsx")]
        filepath = filedialog.askopenfilename(initialdir=working_dir, filetypes=ftypes)

        # TODO add handling for an excel file + sheet name as well
        # if pathlib.Path(filepath).suffix == ".accdb":

        accdb_reader = AccdbHandle(filepath, how="open")
        tables = accdb_reader.get_tables()
        for table in tables:
            menu.add_command(label=table, command=lambda name=table: var.set(name))
        var.set(tables[0])
