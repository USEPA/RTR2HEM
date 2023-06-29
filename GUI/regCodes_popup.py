from tkinter import *
from .generic_GUI import GUI


class RegCodesGUI(GUI):
    def __init__(self, regCode_list):
        self.regCode_list = regCode_list

        super().__init__(title="Regulatory Codes")
        try:
            self.main()
        except Exception as e:
            self.error(e)

    def get_response(self):
        return self.regCode_results

    def clear_all(self, is_checked, regCodes):
        for regCode in regCodes:
            regCode.set(0)
        is_checked.set(0)

    def qa_regCodes(self, regCode_list):
        regCodes = []
        for regCode in regCode_list:
            regCodes.append(regCode.get())

        self.regCode_results = dict(zip(self.regCode_list, regCodes))
        self.close_window()

    def select_all(self, is_checked, regCode_button_list):
        for regCode in regCode_button_list:
            if is_checked.get():
                regCode.set(1)
            else:
                regCode.set(0)

    def main(self):
        regCode_button_list = []

        gen = self.row_generator()

        select_all_var = IntVar()
        select_all_btn = Checkbutton(
            self.root,
            text="Select all",
            height=2,
            onvalue=1,
            offvalue=0,
            variable=select_all_var,
            command=lambda: self.select_all(select_all_var, regCode_button_list),
        )
        select_all_btn.grid(row=next(gen), column=0, padx=(10, 10), sticky=W)

        clear_all_btn = Button(
            self.root,
            text="Clear all",
            command=lambda: self.clear_all(select_all_var, regCode_button_list),
        )
        clear_all_btn.grid(
            row=next(gen), column=0, pady=(0, 5), padx=(10, 10), sticky=W
        )

        run_qa = Button(
            self.root,
            text="Submit",
            command=lambda: self.qa_regCodes(regCode_button_list),
        )
        run_qa.grid(row=next(gen), column=0, pady=(5, 5), padx=(10, 10), sticky=W)

        sbf = self.scrollbar(self.root, bg_color="#f0f0f0")
        frame = sbf.scrolled_frame
        sbf.grid(row=next(gen), column=0, sticky="nsew")

        for i, regCode in enumerate(self.regCode_list):
            regCode_var = IntVar()
            regCode_button = Checkbutton(
                frame, text=regCode, onvalue=1, offvalue=0, variable=regCode_var
            )
            regCode_button.grid(row=next(gen), column=0, padx=(10, 10), sticky=W)
            regCode_button_list.append(regCode_var)

        super().main()
