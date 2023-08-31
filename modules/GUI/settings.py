from tkinter import *
from .generic_GUI import GUI, FileImport
from modules.utils import config


class SettingsGUI(GUI):
    green = "#69c14c"
    blue = "#00538b"
    white = "#ffffff"
    grey = "#d0d0d0"

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
            text="Run setup from config",
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
            bg=self.grey,
            borderwidth=2,
            relief="groove",
        )
        subroot.grid(row=next(gen), columnspan=10, padx=10)

        ##############################################################
        # Source Category (output files) name
        src_cat_label = Label(subroot, text="Source Catgeory name", bg=self.grey)
        src_cat_label.grid(row=next(gen), column=0, padx=(0, 0), sticky=W)

        src_cat_textbox = Entry(subroot, width=40)
        src_cat_padx_left = self.width(src_cat_label) + 10
        src_cat_textbox.grid(
            row=self.current_gen, padx=(src_cat_padx_left, 5), sticky=W
        )

        ##############################################################
        # accdb and table select
        import_obj = FileImport(subroot).create()
        import_obj.import_btn.grid(row=next(gen), padx=(5, 0), sticky=W)

        ##############################################################
        # Import existing EPGs and Source IDs
        import_subroot = LabelFrame(
            subroot,
            text="Import",
            font=16,
            borderwidth=3,
            relief="groove",
        )
        import_subroot.grid(row=next(gen), pady=(5, 5), sticky=W)

        epgs = FileImport(import_subroot).create(
            btn_name="Import previously generated emission process group abbreviations"
        )
        epgs.import_btn.grid(row=next(gen), padx=(5, 5), pady=(5, 5), sticky=W)

        srcid = FileImport(import_subroot).create(
            btn_name="Import previously generated SourceIDs"
        )
        srcid.import_btn.grid(row=next(gen), padx=(5, 5), pady=(5, 5), sticky=W)

        ##############################################################
        # Emissions choice
        emissions_subroot = LabelFrame(
            subroot,
            text="Emissions Type",
            font=16,
            borderwidth=3,
            relief="groove",
        )
        emissions_subroot.grid(row=next(gen), sticky=W)
        emiss_var = StringVar(value="Actual")

        emissions_subroot_row = self.current_gen

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
            emissions_subroot,
            text="Acute Emissions",
            variable=emiss_var,
            value="Acute",
        )
        acute.grid(row=next(gen), sticky=W)

        ##############################################################
        # Category/Whole Records choice
        records_subroot = LabelFrame(
            subroot,
            text="Records Type",
            font=16,
            borderwidth=3,
            relief="groove",
        )
        emiss_subroot_width = self.width(emissions_subroot) + 5
        records_subroot.grid(
            row=emissions_subroot_row, padx=(emiss_subroot_width, 5), sticky=W
        )
        records_var = StringVar(value="Cat")

        cat_only = Radiobutton(
            records_subroot,
            text="File only has category records",
            variable=records_var,
            value="Cat",
        )
        cat_only.grid(sticky=W)

        cat_whole = Radiobutton(
            records_subroot,
            text="File has category and non-category records",
            variable=records_var,
            value="CatWhole",
        )
        cat_whole.grid(sticky=W)

        ##############################################################
        # Submit
        run_setup = Button(
            self.root,
            text="Run setup",
            command=lambda: self.run_setup(
                src_cat_textbox,
                import_obj,
                emiss_var,
                records_var,
                epgs=epgs,
                srcids=srcid,
            ),
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

    def run_setup(
        self, src_cat_name, import_table, emiss_var, record_var, epgs=None, srcids=None
    ):
        if not src_cat_name.get():
            self.warn(msg="Source Category name must not be empty")
            return

        if not import_table.filepath:
            self.warn(msg="No file selected to import")
            return

        settings_json = {
            "settings": {
                "source_category_name": src_cat_name.get(),
                "only_category_records": True if record_var.get() == "Cat" else False,
                "emission_type": emiss_var.get(),
                "emission_abbr": {
                    "import": True if epgs.filepath else False,
                    "file": epgs.filepath,
                    "table": epgs.table_var.get() if epgs.table_var else None,
                },
                "src_ids": {
                    "import": True if srcids.filepath else False,
                    "file": srcids.filepath,
                    "table": srcids.table_var.get() if srcids.table_var else None,
                },
                "input_file": import_table.filepath,
                "input_table": import_table.table_var.get(),
                "static": "./static",
            }
        }
        """
             "processing_columns": {
                "pre": {
                    "emission_process_group": "",
                    "regulatory_code": "",
                    "state_county_fips": "",
                    "sppd_facility_identifier": "",
                    "fugitive_angle_degrees": "",
                    "fugitive_length_sigmax_ft": "",
                    "fugitive_width_sigmay_ft": "",
                    "emission_release_point_type": "",
                    "stack_height (ft)": "",
                    "stack_diameter (ft)": "",
                    "exit_gas_temperature (f)": "",
                    "exit_gas_velocity (ft/sec)": "",
                    "metal_speciation_factor": ""
                }
            }
        """
        config.load_config(settings_json)
