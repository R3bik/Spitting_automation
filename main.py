import tkinter as tk
from tkinter import messagebox, filedialog
import os
import pandas as pd
import re

class Splitter:
    def __init__(self, root):
        root.title("Phone Number Splitter")
        root.geometry("1100x700")
        
        self.entries = {}
        self.default_output_folder = os.path.join(os.path.expanduser("~"), "PhoneNumberSplitter_Output")

        # File Selection Frame
        self.file_frame = tk.LabelFrame(root, text="Select Files", padx=10, pady=10)
        self.file_frame.pack(padx=10, pady=10, fill="x")

        self._add_file_selector(self.file_frame, "Main File:", 0, is_company=False)
        self._add_file_selector(self.file_frame, "Company Numbers File:", 1, is_company=True)

        # Input Frame
        self.input_frame = tk.LabelFrame(root, text="Input Settings", padx=10, pady=10)
        self.input_frame.pack(padx=10, pady=10, fill="x")

        self._add_input_field(self.input_frame, "SMS Amount:", 0, column=0, key="sms")
        self._add_input_field(self.input_frame, "Days for SMS:", row=1, column=0, key="days_sms")
        self._add_input_field(self.input_frame, "Days for OBD:", row=1, column=2, key="days_obd")

        self.obd_amount_label = tk.Label(self.input_frame, text="OBD Amount: N/A")
        self.obd_amount_label.grid(row=0, column=2, padx=10, sticky="w")

        self.total_label = tk.Label(self.input_frame, text="Total: N/A")
        self.total_label.grid(row=0, column=4, padx=10, sticky="w")

        # Output Folder Frame
        self.output_frame = tk.LabelFrame(root, text="Select Output Folders", padx=10, pady=10)
        self.output_frame.pack(padx=10, pady=10, fill="x")

        self._add_folder_selector(self.output_frame, "Output Folder for SMS:", 0, key="output_sms")
        self._add_folder_selector(self.output_frame, "Output Folder for OBD:", 1, key="output_obd")

        # Run Button
        self.run_button = tk.Button(root, text="Start Splitting", command=self.split_files, 
                                  bg="green", fg="white", height=2, width=20)
        self.run_button.pack(pady=10)

        # Report Frame
        self.report_frame = tk.LabelFrame(root, text="Summary Report", padx=10, pady=10)
        self.report_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.report_text = tk.Text(self.report_frame, state="disabled", height=15)
        self.scrollbar = tk.Scrollbar(self.report_frame, command=self.report_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.report_text.config(yscrollcommand=self.scrollbar.set)
        self.report_text.pack(fill="both", expand=True)

        # Set default output folders
        self.entries['output_sms'].insert(0, os.path.join(self.default_output_folder, "SMS"))
        self.entries['output_obd'].insert(0, os.path.join(self.default_output_folder, "OBD"))

    def _add_file_selector(self, parent, text, row, is_company):
        label = tk.Label(parent, text=text)
        label.grid(row=row, column=0, sticky="e")
        entry = tk.Entry(parent, width=70)
        entry.grid(row=row, column=1, padx=5)
        button = tk.Button(parent, text="Browse", command=lambda: self.browse_file(entry, is_company))
        button.grid(row=row, column=2)
        key = "company" if is_company else "main"
        self.entries[key] = entry

    def _add_folder_selector(self, parent, text, row, key):
        label = tk.Label(parent, text=text)
        label.grid(row=row, column=0, sticky="e")
        entry = tk.Entry(parent, width=70)
        entry.grid(row=row, column=1, padx=5)
        button = tk.Button(parent, text="Browse", command=lambda: self.browse_folder(entry))
        button.grid(row=row, column=2)
        self.entries[key] = entry

    def _add_input_field(self, parent, text, row, key, column=0):
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

    def browse_file(self, entry, is_company):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            entry.delete(0, tk.END)
            entry.insert(0, path)
            if not is_company:
                self.update_OBD_amount()

    def browse_folder(self, entry):
        path = filedialog.askdirectory()
        if path:
            entry.delete(0, tk.END)
            entry.insert(0, path)

    def detect_phone_column(self, df):
        for col in df.columns:
            if df[col].astype(str).str.contains(r"\d{10,}").any():
                return col
        return df.columns[0]  # Fallback to first column

    def update_OBD_amount(self):
        try:
            main_file = self.entries["main"].get()
            if not main_file:
                return
                
            # Count lines without loading entire file
            with open(main_file, 'r') as f:
                total = sum(1 for _ in f) - 1  # Subtract header
            
            sms_amount = int(self.entries['sms'].get()) if self.entries['sms'].get().isdigit() else 0
            
            if sms_amount > total:
                self.obd_amount_label.config(text="OBD Amount: Error!", fg="red")
                self.total_label.config(text=f"Total: {total} (SMS exceeds total)", fg="red")
            else:
                obd_amount = total - sms_amount
                self.obd_amount_label.config(text=f"OBD Amount: {obd_amount}", fg="black")
                self.total_label.config(text=f"Total: {total}", fg="black")
                
        except Exception:
            self.obd_amount_label.config(text="OBD Amount: N/A")
            self.total_label.config(text="Total: N/A")

    def clean_phone_series(self, series, remove_prefix=True):
        series = series.dropna().astype(str)
        series = series[~series.str.contains("[a-zA-Z]", regex=True)]
        series = series.str.replace(".0", "", regex=False)
        if remove_prefix:
            series = series.str.replace(r'^977', '', regex=True)
        return series[series.str.match(r'^\d{10,}$')]

    def validate_inputs(self):
        errors = []
        
        # Validate main file
        if not self.entries["main"].get():
            errors.append("Main file not selected")
            
        # Validate company file
        if not self.entries["company"].get():
            errors.append("Company file not selected")
            
        # Validate SMS amount
        try:
            sms_amount = int(self.entries['sms'].get())
            if sms_amount < 0:
                errors.append("SMS amount cannot be negative")
        except ValueError:
            errors.append("Invalid SMS amount")
            
        # Validate days
        try:
            days_sms = int(self.entries['days_sms'].get())
            days_obd = int(self.entries['days_obd'].get())
            if days_sms <= 0 or days_obd <= 0:
                errors.append("Days must be positive numbers")
        except ValueError:
            errors.append("Invalid days value")
            
        # Validate output folders
        if not self.entries['output_sms'].get() or not self.entries['output_obd'].get():
            errors.append("Output folders not specified")
            
        return errors

    def split_files(self):
        try:
            # Validate inputs
            errors = self.validate_inputs()
            if errors:
                messagebox.showerror("Input Error", "\n".join(errors))
                return
                
            # Get inputs
            main_file = self.entries["main"].get()
            company_file = self.entries["company"].get()
            sms_amount = int(self.entries['sms'].get())
            days_sms = int(self.entries['days_sms'].get())
            days_obd = int(self.entries['days_obd'].get())
            output_sms = self.entries['output_sms'].get()
            output_obd = self.entries['output_obd'].get()

            # Read and process main file
            df_main = pd.read_csv(main_file, encoding="utf-8-sig")
            df_main.columns = df_main.columns.str.strip()
            phone_col = self.detect_phone_column(df_main)
            df_main[phone_col] = self.clean_phone_series(df_main[phone_col], remove_prefix=False)
            total_numbers = len(df_main)
            
            # Check if SMS amount exceeds total
            if sms_amount > total_numbers:
                messagebox.showerror("Error", f"SMS amount ({sms_amount}) exceeds total numbers ({total_numbers})")
                return
                
            obd_amount = total_numbers - sms_amount

            # Read and process company file
            df_company = pd.read_csv(company_file, encoding="utf-8-sig")
            df_company.columns = df_company.columns.str.strip()
            company_col = self.detect_phone_column(df_company)
            company_sms = self.clean_phone_series(df_company[company_col], remove_prefix=False)
            company_obd = self.clean_phone_series(df_company[company_col], remove_prefix=True)

            # Split data
            df_sms = df_main.iloc[:sms_amount].copy()
            df_obd = df_main.iloc[sms_amount:].copy()
            df_obd[phone_col] = self.clean_phone_series(df_obd[phone_col], remove_prefix=True)

            # Create output directories
            os.makedirs(output_sms, exist_ok=True)
            os.makedirs(output_obd, exist_ok=True)

            report = []
            report.append("Processing Report")
            report.append("="*50)
            report.append(f"Total main numbers: {total_numbers}")
            report.append(f"Company numbers: {len(company_sms)}")
            report.append("")

            # Process SMS files
            if sms_amount > 0:
                chunk_size = sms_amount // days_sms
                extra = sms_amount % days_sms
                start = 0
                
                report.append(f"SMS Files ({sms_amount} numbers across {days_sms} days):")
                for i in range(days_sms):
                    end = start + chunk_size + (1 if i < extra else 0)
                    chunk = df_sms.iloc[start:end]
                    final = pd.concat([chunk, pd.DataFrame({phone_col: company_sms})], ignore_index=True)
                    
                    filename = f"SMS_Day_{i+1}_of_{days_sms}.csv"
                    final.to_csv(os.path.join(output_sms, filename), index=False)
                    
                    report.append(f"- {filename}: {len(chunk)} main + {len(company_sms)} company = {len(final)} total")
                    start = end
                report.append("")
            else:
                report.append("No SMS files created (SMS amount = 0)\n")

            # Process OBD files
            if obd_amount > 0:
                chunk_size = obd_amount // days_obd
                extra = obd_amount % days_obd
                start = 0
                
                report.append(f"OBD Files ({obd_amount} numbers across {days_obd} days):")
                for i in range(days_obd):
                    end = start + chunk_size + (1 if i < extra else 0)
                    chunk = df_obd.iloc[start:end]
                    final = pd.concat([chunk, pd.DataFrame({phone_col: company_obd})], ignore_index=True)
                    
                    filename = f"OBD_Day_{i+1}_of_{days_obd}.csv"
                    final.to_csv(os.path.join(output_obd, filename), index=False)
                    
                    report.append(f"- {filename}: {len(chunk)} main + {len(company_obd)} company = {len(final)} total")
                    start = end
            else:
                report.append("No OBD files created (OBD amount = 0)")

            # Update report
            self.report_text.config(state="normal")
            self.report_text.delete("1.0", tk.END)
            self.report_text.insert(tk.END, "\n".join(report))
            self.report_text.config(state="disabled")

            messagebox.showinfo("Success", "Processing completed successfully")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            self.report_text.config(state="normal")
            self.report_text.insert(tk.END, f"\n\nERROR: {str(e)}")
            self.report_text.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = Splitter(root)
    root.mainloop()