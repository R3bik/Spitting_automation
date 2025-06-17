import tkinter as tk
import tkinter.filedialog as fd
from tkinter import messagebox
import csv
import pandas as pd

class Splitter:
    def __init__(self,root):
        root.title("Splitter")
        root.geometry("700x400")

        self.mainfile_frame = tk.Frame(root)
        self.mainfile_frame.pack(side='top', pady=20)

        self.input_frame = tk.Frame(root)
        self.input_frame.pack()

        self.output_frame = tk.Frame(root)
        self.output_frame.pack()

        # Main file
        self.browse_button = tk.Button(self.mainfile_frame, text='Browse', command= self.browse_file)
        self.browse_button.grid(row=0, column=2 ,padx=5,pady=5)
        self.file_entry = tk.Entry(self.mainfile_frame, width=50)
        self.file_entry.grid(row=0,column=1,padx=5,pady=5)
        self.file_label = tk.Label(self.mainfile_frame, text="Main file")
        self.file_label.grid(row=0 ,column=0,padx=5,pady=5)
        self.total_rows_label = tk.Label(self.mainfile_frame, text="Total Rows: N/A")
        self.total_rows_label.grid(row=0, column=3, padx=5, pady=5)


        # Company numbers
        self.browse_company = tk.Button(self.mainfile_frame, text='Browse', command= self.company_file)
        self.browse_company.grid(row=1, column=2 ,padx=5,pady=5)
        self.company_entry = tk.Entry(self.mainfile_frame, width=50)
        self.company_entry.grid(row=1,column=1,padx=5,pady=5)
        self.company_label = tk.Label(self.mainfile_frame, text="Company numbers")
        self.company_label.grid(row=1 ,column=0,padx=5,pady=5)

        # SMS amount
        
        self.sms_entry = tk.Entry(self.input_frame,width=20)
        self.sms_entry.grid(row=1, column = 1, padx=4,pady=2)
        self.sms_entry.bind("<KeyRelease>", lambda event: self.update_OBD_amount())  # 👈 Add this line
        self.sms_label = tk.Label(self.input_frame,text="SMS amount")
        self.sms_label.grid(row=1,column=0, padx=5,pady=2)


        # OBD amount
        self.OBD_label = tk.Label(self.input_frame,text="OBD amount : ")
        self.OBD_label.grid(row=1,column=2, padx=5,pady=2)
        self.OBD_amount_label = tk.Label(self.input_frame,text="")
        self.OBD_amount_label.grid(row=1,column=3, padx=5,pady=2)

        # Days for SMS
        self.days_entry_SMS = tk.Entry(self.input_frame,width=20)
        self.days_entry_SMS.grid(row=2, column = 1, padx=4,pady=2)
        self.days_label_SMS = tk.Label(self.input_frame,text="Days for SMS")
        self.days_label_SMS.grid(row=2,column=0, padx=4,pady=2)

        # Days for OBD
        self.days_entry_OBD = tk.Entry(self.input_frame,width=20)
        self.days_entry_OBD.grid(row=2, column = 3, padx=4,pady=2)
        self.days_label_OBD = tk.Label(self.input_frame,text="Days for OBD")
        self.days_label_OBD.grid(row=2,column=2, padx=4,pady=2)

        # Start button
        self.split_button = tk.Button(self.output_frame,text="Start Splitting",command=self.split_files)
        self.split_button.grid(row=3,column=1,pady=20)

        # SMS output folder
        self.sms_output_entry = tk.Entry(self.output_frame,width=50)
        self.sms_output_entry.grid(row=0, column = 1, padx=5,pady=5)
        self.sms_output_label = tk.Label(self.output_frame,text="Output for SMS")
        self.sms_output_label.grid(row=0,column=0, padx=5,pady=5)
        self.sms_output_button = tk.Button(self.output_frame,text="Browse",command=self.browse_sms_output_folder)
        self.sms_output_button.grid(row=0,column=2,padx=5,pady=5)

        # OBD output folder
        self.OBD_output_entry = tk.Entry(self.output_frame,width=50)
        self.OBD_output_entry.grid(row=1, column = 1, padx=5,pady=5)
        self.OBD_output_label = tk.Label(self.output_frame,text="Output for OBD")
        self.OBD_output_label.grid(row=1,column=0, padx=5,pady=5)
        self.OBD_output_button = tk.Button(self.output_frame,text="Browse",command=self.browse_ocd_output_folder)
        self.OBD_output_button.grid(row=1,column=2,padx=5,pady=5)

    def browse_file(self):
        file_path = fd.askopenfilename(filetypes=(("CSV File","*.csv"),("All Files","*.*")))
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

        try:
            df = pd.read_csv(file_path)
            total_rows = len(df)
            self.total_rows_label.config(text=f"Total Rows: {total_rows}")
        except Exception as e:
            self.total_rows_label.config(text="Total Rows: Error")

    def company_file(self):
        file_path = fd.askopenfilename(filetypes=(("CSV File","*.csv"),("All Files","*.*")))
        if file_path:
            self.company_entry.delete(0, tk.END)
            self.company_entry.insert(0, file_path)

    def browse_sms_output_folder(self):
        folder_path = fd.askdirectory()
        if folder_path:
            self.sms_output_entry.delete(0, tk.END)
            self.sms_output_entry.insert(0, folder_path)

    def browse_ocd_output_folder(self):
        folder_path = fd.askdirectory()
        if folder_path:
            self.OBD_output_entry.delete(0, tk.END)
            self.OBD_output_entry.insert(0, folder_path)
    def update_OBD_amount(self):
        try:
            sms_val = self.sms_entry.get()
            file_path = self.file_entry.get()

            if sms_val.strip() == "" or file_path.strip() == "":
                self.OBD_amount_label.config(text="")
                return

            SMS_amount = int(sms_val)
            df = pd.read_csv(file_path)
            OBD_amount = len(df) - SMS_amount
            self.OBD_amount_label.config(text=str(OBD_amount))
        except Exception as e:
                self.OBD_amount_label.config(text="Error")

    def split_files(self):
        try:
            main_file = self.file_entry.get()
            company_file = self.company_entry.get()
            SMS_amount = int(self.sms_entry.get())
            days = int(self.days_entry_SMS.get())
            days_OBD = int(self.days_entry_OBD.get())
            output_sms = self.sms_output_entry.get()
            output_obd = self.OBD_output_entry.get()

            df = pd.read_csv(main_file)
            cdf = pd.read_csv(company_file)

            number_list = cdf.values.ravel()
            cleaned_numbers = [
                str(num).replace(".0", "")
                for num in number_list
                if pd.notna(num) and "Phone" not in str(num) and str(num).strip() != ""
            ]

            company_df = pd.DataFrame(cleaned_numbers, columns=["Phone number"])
            company_df_SMS = company_df.copy()
            company_df_OCD = company_df.copy()

            company_df_SMS["Phone number"] = company_df_SMS["Phone number"].astype(str).str.replace(".0", "", regex=False)
            company_df_OCD["Phone number"] = company_df_OCD["Phone number"].astype(str).str.replace(".0", "", regex=False)
            company_df_OCD['Phone number'] = company_df_OCD['Phone number'].astype(str).str.replace("^977", "", regex=True)

            total_number = len(df)
            if SMS_amount > total_number:
                messagebox.showerror("Error", "SMS amount exceeds total phone numbers!")
                return

            OBD_amount = total_number - SMS_amount

            SMS_dataframe = df.iloc[0:SMS_amount, 0:1]
            OCD_dataframe = df.iloc[SMS_amount:total_number, 0:1]

            OCD_dataframe["Phone number"] = OCD_dataframe["Phone number"].astype(str).str.replace(".0", "", regex=False)
            OCD_dataframe["Phone number"] = OCD_dataframe["Phone number"].str.replace("^977", "", regex=True)

            # SMS splitting
            per_day = SMS_amount // days
            extra = SMS_amount % days
            start = 0
            for i in range(days):
                chunk = per_day + 1 if i < extra else per_day
                end = start + chunk
                chunk_df = SMS_dataframe.iloc[start:end]
                chunk_df = pd.concat([chunk_df, company_df_SMS], ignore_index=False)
                filename = f"SMS_split_day{i+1}.txt"
                filepath = f"{output_sms}/{filename}"
                with open(filepath, "w") as f:
                    f.write("Phone number\n")
                    for number in chunk_df["Phone number"]:
                        f.write(str(number).strip() + "\n")
                start = end

            # OBD splitting
            per_day_OCD = OBD_amount // days_OBD
            extra_OCD = OBD_amount % days_OBD
            start_OBD = 0
            for i in range(days_OBD):
                chunk_OCD = per_day_OCD + 1 if i < extra_OCD else per_day_OCD
                ed = start_OBD + chunk_OCD
                chunk_df_OCD = OCD_dataframe.iloc[start_OBD:ed]
                chunk_df_OCD = pd.concat([chunk_df_OCD, company_df_OCD], ignore_index=False)
                filename = f"OBD_split_day{i+1}.txt"
                filepath = f"{output_obd}/{filename}"
                with open(filepath, "w") as f:
                    f.write("Phone number\n")
                    for number in chunk_df_OCD["Phone number"]:
                        f.write(str(number).strip() + "\n")
                start_OBD = ed

            # ✅ Success popup
            messagebox.showinfo("Success", "✅ Process completed successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Something went wrong:\n{str(e)}")

if __name__ == "__main__":
    window = tk.Tk()
    app = Splitter(window)
    window.mainloop()
