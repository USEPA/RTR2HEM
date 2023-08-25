from tkinter import *
from .generic_GUI import GUI, FileImport


class SettingsGUI(GUI):
    green = "#69c14c"
    blue = "#00538b"
    white = "#ffffff"

    def __init__(self):
        super().__init__(title="Settings")
        try:
            self.root.configure(background=self.blue)
            self.main()
        except Exception as e:
            self.error(e)

    def main(self):
        gen = self.row_generator()

        option_var = StringVar(self.root, "0")
        read_user_opts = Radiobutton(
            self.root,
            text="Run setup from input fields",
            variable=option_var,
            value=0,
            fg=self.white,
            selectcolor="black",
            background=self.blue,
            command=lambda: self.enableChildren(subroot),
        )
        read_config = Radiobutton(
            self.root,
            text="Run setup from config.json",
            variable=option_var,
            value=1,
            fg=self.white,
            selectcolor="black",
            background=self.blue,
            command=lambda: self.disableChildren(subroot),
        )

        read_user_opts.grid(row=next(gen), column=0, padx=(12, 0), sticky=W)

        config_padx_left = self.width(read_user_opts) + 20
        read_config.grid(
            row=self.current_gen, column=0, padx=(config_padx_left, 0), sticky=W
        )

        ##############################################################

        subroot = LabelFrame(
            self.root,
            text="Settings",
            font=16,
            borderwidth=2,
            relief="groove",
        )
        subroot.grid(row=next(gen), columnspan=10, padx=10)

        ##############################################################

        src_cat_label = Label(subroot, text="Source Catgeory name")
        src_cat_label.grid(row=next(gen), column=0, padx=(0, 0), sticky=W)

        src_cat_textbox = Entry(subroot, width=40)
        src_cat_padx_left = self.width(src_cat_label) + 10
        src_cat_textbox.grid(
            row=self.current_gen, padx=(src_cat_padx_left, 0), sticky=W
        )

        ##############################################################
        # accdb and table select
        import_btn, menu = FileImport(subroot).create()
        import_btn.grid(row=next(gen), padx=(5, 0), sticky=W)

        menu_padx_left = self.width(import_btn) + 10
        menu.grid(row=self.current_gen, sticky=EW, padx=(menu_padx_left, 15))

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
