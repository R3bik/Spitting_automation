import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import os
import pandas as pd
import re
import chardet
import sys

class Splitter:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        
    def setup_ui(self):
        self.root.title("Phone Number Splitter")
        self.root.geometry("1100x750")
        
        # Configure window to be resizable
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.entries = {}
        self.default_output_folder = os.path.join(os.path.expanduser("~"), "PhoneNumberSplitter_Output")

        # File Selection Frame
        self.file_frame = tk.LabelFrame(self.root, text="Select Files", padx=10, pady=10)
        self.file_frame.pack(padx=10, pady=5, fill="x")

        self._add_file_selector(self.file_frame, "Main File:", 0, is_company=False)
        self._add_file_selector(self.file_frame, "Company Numbers File:", 1, is_company=True)

        # Input Frame
        self.input_frame = tk.LabelFrame(self.root, text="Input Settings", padx=10, pady=10)
        self.input_frame.pack(padx=10, pady=5, fill="x")

        self._add_input_field(self.input_frame, "SMS Amount:", 0, column=0, key="sms")
        self._add_input_field(self.input_frame, "Days for SMS:", row=1, column=0, key="days_sms")
        self._add_input_field(self.input_frame, "Days for OBD:", row=1, column=2, key="days_obd")

        # Custom Prefix Entry
        tk.Label(self.input_frame, text="Custom Prefix:").grid(row=2, column=0, sticky="e", padx=5)
        self.prefix_entry = tk.Entry(self.input_frame, width=20)
        self.prefix_entry.grid(row=2, column=1, sticky="w", padx=5)
        tk.Label(self.input_frame, text="(Leave blank for no prefix)").grid(row=2, column=2, sticky="w")

        self.obd_amount_label = tk.Label(self.input_frame, text="OBD Amount: N/A")
        self.obd_amount_label.grid(row=0, column=2, padx=10, sticky="w")

        self.total_label = tk.Label(self.input_frame, text="Total: N/A")
        self.total_label.grid(row=0, column=4, padx=10, sticky="w")

        # Output Folder Frame
        self.output_frame = tk.LabelFrame(self.root, text="Select Output Folders", padx=10, pady=10)
        self.output_frame.pack(padx=10, pady=5, fill="x")

        self._add_folder_selector(self.output_frame, "Output Folder for SMS:", 0, key="output_sms")
        self._add_folder_selector(self.output_frame, "Output Folder for OBD:", 1, key="output_obd")

        # Run Button
        self.run_button = tk.Button(self.root, text="Start Splitting", command=self.split_files, 
                                  bg="#4CAF50", fg="white", height=2, width=20, font=('Arial', 10, 'bold'))
        self.run_button.pack(pady=10)

        # Report Frame
        self.report_frame = tk.LabelFrame(self.root, text="Summary Report", padx=10, pady=10)
        self.report_frame.pack(padx=10, pady=5, fill="both", expand=True)

        self.report_text = tk.Text(self.report_frame, state="disabled", height=15, wrap=tk.WORD)
        self.scrollbar = tk.Scrollbar(self.report_frame, command=self.report_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.report_text.config(yscrollcommand=self.scrollbar.set)
        self.report_text.pack(fill="both", expand=True)

        # Status Bar
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Set default output folders
        self.entries['output_sms'].insert(0, os.path.join(self.default_output_folder, "SMS"))
        self.entries['output_obd'].insert(0, os.path.join(self.default_output_folder, "OBD"))

    def _add_file_selector(self, parent, text, row, is_company):
        label = tk.Label(parent, text=text)
        label.grid(row=row, column=0, sticky="e", padx=5)
        entry = tk.Entry(parent, width=70)
        entry.grid(row=row, column=1, padx=5)
        button = tk.Button(parent, text="Browse", command=lambda: self.browse_file(entry, is_company))
        button.grid(row=row, column=2, padx=5)
        key = "company" if is_company else "main"
        self.entries[key] = entry

    def _add_folder_selector(self, parent, text, row, key):
        label = tk.Label(parent, text=text)
        label.grid(row=row, column=0, sticky="e", padx=5)
        entry = tk.Entry(parent, width=70)
        entry.grid(row=row, column=1, padx=5)
        button = tk.Button(parent, text="Browse", command=lambda: self.browse_folder(entry))
        button.grid(row=row, column=2, padx=5)
        self.entries[key] = entry

    def _add_input_field(self, parent, text, row, key, column=0):
        label = tk.Label(parent, text=text)
        label.grid(row=row, column=column, sticky="e", padx=5)
        entry = tk.Entry(parent, width=15)
        entry.grid(row=row, column=column+1, padx=5, sticky="w")
        vcmd = (parent.register(self._validate_positive_int), '%P')
        entry.config(validate='key', validatecommand=vcmd)
        self.entries[key] = entry
        if key == "sms":
            entry.bind("<KeyRelease>", lambda event: self.update_OBD_amount())

    def _validate_positive_int(self, value):
        return value.isdigit() or value == ""

    def browse_file(self, entry, is_company):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
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

    def detect_file_encoding(self, filepath):
        """Detect file encoding using chardet"""
        with open(filepath, 'rb') as f:
            rawdata = f.read(10000)  # Read first 10k bytes to guess encoding
        result = chardet.detect(rawdata)
        return result['encoding']

    def read_csv_with_encoding(self, filepath):
        """Read CSV with automatic encoding detection"""
        try:
            # First try UTF-8 with BOM (common for Excel exports)
            return pd.read_csv(filepath, encoding='utf-8-sig', dtype=str)
        except UnicodeDecodeError:
            try:
                # If UTF-8 fails, try detected encoding
                encoding = self.detect_file_encoding(filepath)
                return pd.read_csv(filepath, encoding=encoding, dtype=str)
            except Exception as e:
                raise ValueError(f"Cannot read file {filepath}. Detected encoding: {encoding}. Error: {str(e)}")

    def detect_phone_column(self, df):
        for col in df.columns:
            if df[col].astype(str).str.contains(r'^(\+?\d{10,})$').any():
                return col
        for col in df.columns:
            if 'phone' in col.lower() or 'number' in col.lower():
                return col
        return df.columns[0]

    def update_OBD_amount(self):
        try:
            main_file = self.entries["main"].get()
            if not main_file or not os.path.exists(main_file):
                raise FileNotFoundError("Main file not selected or doesn't exist")
            
            with open(main_file, 'r', encoding='utf-8-sig') as f:
                total = sum(1 for _ in f) - 1
                
            sms_amount = int(self.entries['sms'].get()) if self.entries['sms'].get().isdigit() else 0
            
            if sms_amount > total:
                self.obd_amount_label.config(text="OBD Amount: Error!", fg="red")
                self.total_label.config(text=f"Total: {total} (SMS exceeds total)", fg="red")
            else:
                obd_amount = total - sms_amount
                self.obd_amount_label.config(text=f"OBD Amount: {obd_amount}", fg="black")
                self.total_label.config(text=f"Total: {total}", fg="black")
                
        except Exception as e:
            self.obd_amount_label.config(text="OBD Amount: N/A", fg="red")
            self.total_label.config(text=f"Error: {str(e)}", fg="red")

    def clean_phone_series(self, series, remove_prefix=True):
        series = series.dropna().astype(str).str.strip()
        series = series.str.replace(r'[^\d\+]', '', regex=True)
        series = series[series != '']
        if remove_prefix:
            series = series.str.replace(r'^\+?977', '', regex=True)
        return series[series.str.match(r'^\d{10,}$')]

    def validate_inputs(self):
        errors = []
        
        if not self.entries["main"].get():
            errors.append("Main file not selected")
        if not self.entries["company"].get():
            errors.append("Company file not selected")
            
        try:
            sms_amount = int(self.entries['sms'].get())
            if sms_amount < 0:
                errors.append("SMS amount must be positive")
        except ValueError:
            errors.append("Invalid SMS amount")
            
        try:
            days_sms = int(self.entries['days_sms'].get())
            days_obd = int(self.entries['days_obd'].get())
            if days_sms <= 0 or days_obd <= 0:
                errors.append("Days must be positive integers")
        except ValueError:
            errors.append("Invalid days value")
            
        if not self.entries['output_sms'].get() or not self.entries['output_obd'].get():
            errors.append("Output folders not specified")
            
        try:
            with open(self.entries["main"].get(), 'r', encoding='utf-8-sig') as f:
                total = sum(1 for _ in f) - 1
            if int(self.entries['sms'].get()) > total:
                errors.append(f"SMS amount exceeds total numbers ({total})")
        except:
            pass
            
        return errors

    def split_files(self):
        self.status_bar.config(text="Processing...", fg="blue")
        self.root.update_idletasks()
        
        try:
            errors = self.validate_inputs()
            if errors:
                messagebox.showerror("Input Error", "\n".join(errors))
                self.status_bar.config(text="Error in inputs", fg="red")
                return
                
            # Get all inputs including custom prefix
            main_file = self.entries["main"].get()
            company_file = self.entries["company"].get()
            sms_amount = int(self.entries['sms'].get())
            days_sms = int(self.entries['days_sms'].get())
            days_obd = int(self.entries['days_obd'].get())
            output_sms = self.entries['output_sms'].get()
            output_obd = self.entries['output_obd'].get()
            prefix = self.prefix_entry.get().strip()
            
            # Format prefix
            if prefix:
                prefix = f"{prefix}_"

            # Read and process main file with encoding detection
            try:
                df_main = self.read_csv_with_encoding(main_file)
                df_main.columns = df_main.columns.str.strip()
                phone_col = self.detect_phone_column(df_main)
                df_main[phone_col] = self.clean_phone_series(df_main[phone_col], remove_prefix=False)
                total_numbers = len(df_main)
                
                if total_numbers == 0:
                    raise ValueError("No valid phone numbers found in main file")
            except Exception as e:
                raise ValueError(f"Error processing main file: {str(e)}")

            # Read and process company file with encoding detection
            try:
                df_company = self.read_csv_with_encoding(company_file)
                df_company.columns = df_company.columns.str.strip()
                company_col = self.detect_phone_column(df_company)
                company_numbers = self.clean_phone_series(df_company[company_col], remove_prefix=False)
                
                if len(company_numbers) == 0:
                    raise ValueError("No valid company numbers found")
            except Exception as e:
                raise ValueError(f"Error processing company file: {str(e)}")

            # Verify SMS amount
            obd_amount = total_numbers - sms_amount
            if obd_amount < 0:
                raise ValueError(f"SMS amount ({sms_amount}) exceeds total numbers ({total_numbers})")

            # Prepare company numbers
            company_sms = company_numbers
            company_obd = self.clean_phone_series(company_numbers, remove_prefix=True)
            
            # Split main data
            df_sms = df_main.iloc[:sms_amount].copy()
            df_obd = df_main.iloc[sms_amount:].copy()
            df_obd[phone_col] = self.clean_phone_series(df_obd[phone_col], remove_prefix=True)

            report = []
            report.append("PROCESSING REPORT")
            report.append("="*50)
            report.append(f"Main numbers processed: {total_numbers}")
            report.append(f"Company numbers found: {len(company_numbers)}")
            report.append(f"Custom prefix used: '{prefix}'" if prefix else "No prefix used")
            report.append("")

            # Create output directories
            os.makedirs(output_sms, exist_ok=True)
            os.makedirs(output_obd, exist_ok=True)

            # Process SMS files
            if sms_amount > 0:
                chunk_size_sms = sms_amount // days_sms
                extra_sms = sms_amount % days_sms
                start = 0
                
                report.append(f"SMS FILES ({sms_amount} numbers across {days_sms} days):")
                for i in range(days_sms):
                    end = start + chunk_size_sms + (1 if i < extra_sms else 0)
                    chunk = df_sms.iloc[start:end]
                    final_chunk = pd.concat([chunk, pd.DataFrame({phone_col: company_sms})], ignore_index=True)
                    
                    filename = f"{prefix}SMS_day{i+1}.txt"
                    filepath = os.path.join(output_sms, filename)
                    final_chunk.to_csv(filepath, index=False, header=False,sep='\t')
                    
                    report.append(f"- {filename}: {len(chunk)} main + {len(company_sms)} company = {len(final_chunk)} total")
                    start = end
                report.append("")
            else:
                report.append("No SMS files created (SMS amount = 0)\n")

            # Process OBD files
            if obd_amount > 0:
                chunk_size_obd = obd_amount // days_obd
                extra_obd = obd_amount % days_obd
                start = 0
                
                report.append(f"OBD FILES ({obd_amount} numbers across {days_obd} days):")
                for i in range(days_obd):
                    end = start + chunk_size_obd + (1 if i < extra_obd else 0)
                    chunk = df_obd.iloc[start:end]
                    final_chunk = pd.concat([chunk, pd.DataFrame({phone_col: company_obd})], ignore_index=True)
                    
                    filename = f"{prefix}OBD_day{i+1}.txt"
                    filepath = os.path.join(output_obd, filename)
                    final_chunk.to_csv(filepath, index=False, header=False,sep='\t')
                    
                    report.append(f"- {filename}: {len(chunk)} main + {len(company_obd)} company = {len(final_chunk)} total")
                    start = end
            else:
                report.append("No OBD files created (OBD amount = 0)")

            # Update report
            self.report_text.config(state="normal")
            self.report_text.delete("1.0", tk.END)
            self.report_text.insert(tk.END, "\n".join(report))
            self.report_text.config(state="disabled")

            # Show success message
            messagebox.showinfo("Success", "Files created successfully!")
            self.status_bar.config(text="Processing completed", fg="green")

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            messagebox.showerror("Processing Error", error_msg)
            self.report_text.config(state="normal")
            self.report_text.insert(tk.END, f"\n\n{error_msg}")
            self.report_text.config(state="disabled")
            self.status_bar.config(text="Processing failed", fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    try:
        app = Splitter(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Application failed to start:\n{str(e)}")
        sys.exit(1)