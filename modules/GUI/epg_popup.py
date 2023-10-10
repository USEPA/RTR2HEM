from string import ascii_uppercase
from tkinter import *
from .generic_GUI import GUI, RowGenerator


class EpgGUI(GUI):
    def __init__(self, epg_list):
        self.epg_list = list(epg_list.keys())
        self.epg_vals = list(epg_list.values())
        super().__init__(title="Emission Process Group Abbreviations")
        try:
            self.main()
        except Exception as e:
            self.error()

    def get_response(self):
        return self.epg_results

    def clear_epgs(self, is_checked, entries):
        for entry in entries:
            entry.delete(0, END)
            entry.insert(0, "")
        is_checked.set(0)

    def qa_epgs(self, entries):
        epg_abbr = []
        for entry in entries:
            val = entry.get().upper()
            if not val:
                return self.warn(
                    "Invalid field", "Please fill out missing abbreviations."
                )
            if len(val) != 2:
                return self.warn(
                    "Invalid field", "All abbreviations must be 2 letters long."
                )
            epg_abbr.append(val)

        if len(set(epg_abbr)) != len(self.epg_list):
            return self.warn("Duplicate fields", "All abbreviations must be unique.")

        self.epg_results = dict(zip(self.epg_list, epg_abbr))
        self.close_window()

    def autofill(self, is_checked, epg_entry_list):
        if is_checked.get():
            l1 = 0
            l2 = 0
            for idx, entry in enumerate(epg_entry_list):
                if idx % 26 == 0 and l2 > 0:
                    l1 += 1 % 26
                l2 = idx % 26
                abbr = ascii_uppercase[l1] + ascii_uppercase[l2]
                entry.delete(0, END)
                entry.insert(0, abbr)
        else:
            for entry in epg_entry_list:
                entry.delete(0, END)
                entry.insert(0, "")

    def main(self):
        epg_msg_list = []
        epg_entry_list = []

        gen = RowGenerator()

        title_label = Label(
            self.root,
            text="Supply unique 2-character abbreviations (on the right) for each\nemission process group.",
            justify=LEFT,
        )
        title_label.grid(row=gen.next(), column=0, padx=(10, 10), sticky=W)

        autofill_var = IntVar()
        autofill_abbreviations = Checkbutton(
            self.root,
            text="Autofill abbreviations",
            height=2,
            onvalue=1,
            offvalue=0,
            variable=autofill_var,
            command=lambda: self.autofill(autofill_var, epg_entry_list),
        )
        autofill_abbreviations.grid(row=gen.next(), column=0, padx=(10, 10), sticky=W)

        clear_abbr_button = Button(
            self.root,
            text="Clear abbreviations",
            command=lambda: self.clear_epgs(autofill_var, epg_entry_list),
        )
        clear_abbr_button.grid(
            row=gen.next(), column=0, pady=(0, 5), padx=(10, 10), sticky=W
        )

        run_qa = Button(
            self.root,
            text="Submit",
            command=lambda: self.qa_epgs(epg_entry_list),
        )
        run_qa.grid(row=gen.next(), column=0, pady=(5, 5), padx=(10, 10), sticky=W)

        ################################################

        sbf = self.scrollbar(self.root)
        frame = sbf.scrolled_frame
        sbf.grid(row=gen.next(), column=0, sticky="nsew")

        for i, epg in enumerate(self.epg_list):
            epg, epg_h = self.split_str(40, epg)
            epg_message = Text(
                frame, height=epg_h, width=40, borderwidth=1, relief=SOLID
            )
            epg_message.delete(1.0, END)
            epg_message.insert(END, epg)
            epg_message.config(state=DISABLED)
            epg_msg_list.append(epg_message)
            epg_msg_list[i].grid(
                row=gen.next(),
                column=0,
                pady=(5, 5),
                padx=(5, 0),
                sticky=W,
            )

            # abbreviation
            epg_abbr_entry = Entry(frame, width=5, borderwidth=1, relief=SOLID)
            epg_abbr_entry.delete(0, END)
            epg_abbr_entry.insert(0, self.epg_vals[i])

            epg_entry_list.append(epg_abbr_entry)
            epg_entry_list[i].grid(row=gen.current(), column=1, padx=(10, 10), sticky=W)
        self.bind_entries(epg_entry_list)

        super().main()
