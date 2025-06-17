import tkinter as tk
from tkinter import messagebox, filedialog
import os
import pandas as pd

class Splitter:
    def __init__(self, root):
        root.title("Phone Number Splitter")
        root.geometry("1100x650")

        self.entries = {}

        # File Selection Frame
        self.file_frame = tk.LabelFrame(root, text="Select Files", padx=10, pady=10)
        self.file_frame.pack(padx=10, pady=10, fill="x")

        self._add_file_selector(self.file_frame, "Main File:", 0, is_company=False)
        self._add_file_selector(self.file_frame, "Company Numbers File:", 1, is_company=True)

        # Input Frame
        self.input_frame = tk.LabelFrame(root, text="Input Settings", padx=10, pady=10)
        self.input_frame.pack(padx=10, pady=10, fill="x")

        self._add_input_field(self.input_frame, "SMS Amount:", 0, column=0, key="sms")
        self._add_input_field(self.input_frame, "Days for SMS:", 1, column=0, key="days_sms")
        self._add_input_field(self.input_frame, "Days for OBD:", 1, column=2, key="days_obd")

        self.obd_amount_label = tk.Label(self.input_frame, text="OBD Amount: N/A")
        self.obd_amount_label.grid(row=0, column=2, padx=10, sticky="w")

        # Output Folder Frame
        self.output_frame = tk.LabelFrame(root, text="Select Output Folders", padx=10, pady=10)
        self.output_frame.pack(padx=10, pady=10, fill="x")

        self._add_folder_selector(self.output_frame, "Output Folder for SMS:", 0, key="output_sms")
        self._add_folder_selector(self.output_frame, "Output Folder for OBD:", 1, key="output_obd")

        # Run Button
        self.run_button = tk.Button(root, text="Start Splitting", command=self.split_files, bg="green", fg="white", height=2, width=20)
        self.run_button.pack(pady=10)

        # Report Frame
        self.report_frame = tk.LabelFrame(root, text="Summary Report", padx=10, pady=10)
        self.report_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.report_text = tk.Text(self.report_frame, state="disabled", height=15)
        self.report_text.pack(fill="both", expand=True)

    def _add_file_selector(self, parent, text, row, is_company):
        label = tk.Label(parent, text=text)
        label.grid(row=row, column=0, sticky="e")
        entry = tk.Entry(parent, width=70)
        entry.grid(row=row, column=1, padx=5)
        button = tk.Button(parent, text="Browse", command=lambda: self.browse_file(entry))
        button.grid(row=row, column=2)
        key = "company" if is_company else "main"
        self.entries[key] = entry
        if not is_company:
            entry.bind("<FocusOut>", lambda event: self.update_OBD_amount())

    def _add_folder_selector(self, parent, text, row, key):
        label = tk.Label(parent, text=text)
        label.grid(row=row, column=0, sticky="e")
        entry = tk.Entry(parent, width=70)
        entry.grid(row=row, column=1, padx=5)
        button = tk.Button(parent, text="Browse", command=lambda: self.browse_folder(entry))
        button.grid(row=row, column=2)
        self.entries[key] = entry

    def _add_input_field(self, parent, text, row, key, column=0, on_change=None, readonly=False, is_label=False):
        label = tk.Label(parent, text=text)
        label.grid(row=row, column=column, sticky="e")
        entry = tk.Entry(parent)
        entry.grid(row=row, column=column + 1, padx=5, sticky="w")
        vcmd = (parent.register(self._validate_positive_int), '%P')
        entry.config(validate='key', validatecommand=vcmd)
        self.entries[key] = entry
        if key == "sms":
            entry.bind("<KeyRelease>", lambda event: self.update_OBD_amount())

    def _validate_positive_int(self, value):
        return value.isdigit() or value == ""

    def browse_file(self, entry):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            entry.delete(0, tk.END)
            entry.insert(0, path)

    def browse_folder(self, entry):
        path = filedialog.askdirectory()
        if path:
            entry.delete(0, tk.END)
            entry.insert(0, path)

    def update_OBD_amount(self):
        try:
            main_file = self.entries["main"].get()
            sms_amount = int(self.entries['sms'].get())
            df = pd.read_csv(main_file)
            total = len(df)
            obd_amount = total - sms_amount
            if obd_amount < 0:
                self.obd_amount_label.config(text="OBD Amount: Error")
            else:
                self.obd_amount_label.config(text=f"OBD Amount: {obd_amount}")
        except:
            self.obd_amount_label.config(text="OBD Amount: N/A")

    def split_files(self):
        try:
            main_file = self.entries["main"].get()
            company_file = self.entries["company"].get()
            sms_amount = int(self.entries['sms'].get()) if self.entries['sms'].get().isdigit() else 0
            days_sms = int(self.entries['days_sms'].get())
            days_obd = int(self.entries['days_obd'].get())
            output_sms = self.entries['output_sms'].get()
            output_obd = self.entries['output_obd'].get()

            df_main = pd.read_csv(main_file)
            df_company = pd.read_csv(company_file)

            total_numbers = len(df_main)
            obd_amount = total_numbers - sms_amount

            df_company_cleaned = df_company.dropna()
            company_numbers = df_company_cleaned[df_company_cleaned.columns[0]].astype(str)
            company_numbers = company_numbers[~company_numbers.str.contains("[a-zA-Z]", regex=True)]

            df_sms = df_main.iloc[:sms_amount].copy()
            df_obd = df_main.iloc[sms_amount:].copy()

            df_sms['Phone number'] = df_sms['Phone number'].astype(str).str.replace(".0", "", regex=False)
            df_obd['Phone number'] = df_obd['Phone number'].astype(str).str.replace(".0", "", regex=False)
            df_obd['Phone number'] = df_obd['Phone number'].str.replace("^977", "", regex=True)

            company_sms = pd.DataFrame(company_numbers, columns=["Phone number"])
            company_obd = company_sms.copy()
            company_obd['Phone number'] = company_obd['Phone number'].str.replace("^977", "", regex=True)

            report = []

            # SMS
            if sms_amount > 0:
                chunk_size_sms = sms_amount // days_sms
                extra_sms = sms_amount % days_sms
                start = 0
                report.append(f"Files created for SMS ({sms_amount} numbers):")
                for i in range(days_sms):
                    end = start + chunk_size_sms + (1 if i < extra_sms else 0)
                    chunk = df_sms.iloc[start:end]
                    final_chunk = pd.concat([chunk, company_sms], ignore_index=True)
                    filepath = os.path.join(output_sms, f"SMS_Day{i+1}.txt")
                    final_chunk.to_csv(filepath, index=False, header=False)
                    report.append(f" - SMS_Day{i+1}.txt ({len(final_chunk)} numbers)")
                    start = end
            else:
                report.append("\u26a0\ufe0f SMS amount is 0. No SMS files were created.")

            # OBD
            if obd_amount > 0:
                chunk_size_obd = obd_amount // days_obd
                extra_obd = obd_amount % days_obd
                start = 0
                report.append(f"\nFiles created for OBD ({obd_amount} numbers):")
                for i in range(days_obd):
                    end = start + chunk_size_obd + (1 if i < extra_obd else 0)
                    chunk = df_obd.iloc[start:end]
                    final_chunk = pd.concat([chunk, company_obd], ignore_index=True)
                    filepath = os.path.join(output_obd, f"OBD_Day{i+1}.txt")
                    final_chunk.to_csv(filepath, index=False, header=False)
                    report.append(f" - OBD_Day{i+1}.txt ({len(final_chunk)} numbers)")
                    start = end
            else:
                report.append("\u26a0\ufe0f OBD amount is 0. No OBD files were created.")

            self.report_text.config(state="normal")
            self.report_text.delete("1.0", tk.END)
            self.report_text.insert(tk.END, "\n".join(report))
            self.report_text.config(state="disabled")

            messagebox.showinfo("Success", "Splitting completed successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = Splitter(root)
    root.mainloop()
