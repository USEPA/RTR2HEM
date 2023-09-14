from tkinter import *
from tkinter.ttk import Combobox
from .generic_GUI import GUI
from modules.utils import config


class ColumnMapGUI(GUI):
    def __init__(self):
        super().__init__(title="Field Mapper")
        try:
            self.main()
        except Exception as e:
            self.error(e)

    def main(self):
        input_columns = list(config.input_df.columns)
        renamed_column_list = []
        gen = self.row_generator()

        ##################################################

        title_label = Label(
            self.root, text="Map Fields from Import File to Current Database:"
        )
        title_label.grid(row=next(gen), column=0, padx=(10, 10), sticky=W)

        submit_mapping = Button(
            self.root,
            text="Import Table",
            command=lambda: self.submit(renamed_column_list),
        )
        submit_mapping.grid(
            row=next(gen), column=0, pady=(5, 5), padx=(10, 10), sticky=W
        )

        ##################################################

        local_label = Label(self.root, text="Local Field Name")
        local_label.grid(row=next(gen), column=0, padx=(10, 10), sticky=W)

        import_spacing = self.width(local_label) + 160
        import_label = Label(self.root, text="Imported Field Name")
        import_label.grid(
            row=self.current_gen, column=0, padx=(import_spacing, 10), sticky=W
        )

        ##################################################

        sbf = self.scrollbar(self.root)
        frame = sbf.scrolled_frame
        sbf.grid(row=next(gen), column=0, sticky="nsew")

        for i, column in enumerate(config.columns_map):
            column_txtbox = Text(frame, height=1, width=30, borderwidth=1, relief=SOLID)

            column_txtbox.delete(1.0, END)
            column_txtbox.insert(END, column)
            column_txtbox.config(state=DISABLED)
            column_txtbox.grid(
                row=next(gen),
                column=0,
                pady=(5, 5),
                padx=(5, 0),
                sticky=W,
            )

            ##################################################

            menu = Combobox(frame, values=input_columns, width=30, state="readonly")
            menu.bind("<MouseWheel>", self._on_mousewheel)
            menu.current(0)
            menu.grid(
                row=self.current_gen,
                column=1,
                padx=(10, 10),
                sticky=W,
            )

            # see if column name matches
            if column in input_columns:
                menu.set(column)
            else:
                menu.set("")
            renamed_column_list.append(menu)

        sbf.canvas.config(width=470)
        super().main()

    def _on_mousewheel(self, event):
        return "break"

    def submit(self, columns_to_map):
        for i, key in enumerate(config.columns_map):
            renamed_col = columns_to_map[i].get()
            if not renamed_col and key != "emission_process_group":
                self.warn(msg="Field name could not be found and must be selected.")
                return
            if key != renamed_col:
                config.columns_map[key] = renamed_col

        self.close_window()
