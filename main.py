import pandas as pd

df = pd.read_csv('Sample_data.csv')
cdf = pd.read_csv('Company_numbers.csv',header= None)

# flattining of the raw csv into list.
number_list = cdf.values.ravel()

# Filter out unwanted rows
cleaned_numbers = [
    str(num).replace(".0", "")  # remove .0 float endings
    for num in number_list
    if pd.notna(num) and "Phone" not in str(num) and str(num).strip() != ""
]

# Create a clean DataFrame with a single correct column
company_df = pd.DataFrame(cleaned_numbers, columns=["Phone number"])

company_df_SMS = company_df.copy()
company_df_OCD = company_df.copy()
company_df_SMS["Phone number"] = company_df_SMS["Phone number"].astype(str).str.replace(".0", "", regex=False)
company_df_OCD["Phone number"] = company_df_OCD["Phone number"].astype(str).str.replace(".0", "", regex=False)

company_df_OCD['Phone number'] = company_df_OCD['Phone number'].astype(str).str.replace("^977", "", regex=True)



# taking users input to split data
Total = len(df)
Sms_input = int(input('Enter the amount for SMS : '))

if (Sms_input>Total):
    print("Input number is greater than total number")
else:
    OCD_input = Total - Sms_input


print(Sms_input)
print(OCD_input)

# slicing data

SMS_dataframe = df.iloc[0:Sms_input,0:1]
OCD_dataframe = df.iloc[Sms_input:Total,0:1]
# Step 1: convert to string first, remove .0 if present
OCD_dataframe["Phone number"] = OCD_dataframe["Phone number"].astype(str).str.replace(".0", "", regex=False)

# Step 2: remove the '977' prefix
OCD_dataframe["Phone number"] = OCD_dataframe["Phone number"].str.replace("^977", "", regex=True)



print(f'SMS Dataframe \n',SMS_dataframe)
print(f'OCD Dataframe \n',OCD_dataframe)

# Saving Dataframes
filepath_SMS = "D:\MERN_Projects\Github_desktop\Spitting_automation\Outputs\SMS.csv"
filepath_OCD = "D:\MERN_Projects\Github_desktop\Spitting_automation\Outputs\OCD.csv"
SMS_dataframe.to_csv(filepath_SMS, index=False,float_format='%.0f')
OCD_dataframe.to_csv(filepath_OCD, index=False,float_format='%.0f')

# spiting sms and ocd data according to the days provided the users
SMS_dataframe = pd.read_csv('D:\\MERN_Projects\\Github_desktop\\Spitting_automation\\Outputs\\SMS.csv')
OCD_dataframe = pd.read_csv('D:\\MERN_Projects\\Github_desktop\\Spitting_automation\\Outputs\\OCD.csv')
SMS_total = len(SMS_dataframe)
OCD_total = len(OCD_dataframe)

days = int(input('Enter number of days : '))

# splitting for SMS
per_day = SMS_total//days
extra = SMS_total%days

# slicing the dataframe by looping for SMS
start = 0
for i in range(days):
    chunk = per_day + 1 if i < extra else per_day
    end = start + chunk
    chunk_df = SMS_dataframe.iloc[start:end]
    # appending company number
    chunk_df = pd.concat([chunk_df,company_df_SMS], ignore_index=False)
    filepath = f"D:\\MERN_Projects\\Github_desktop\\Spitting_automation\\split_days_SMS\\SMS_split_day{i+1}.txt"
    chunk_df.to_csv(filepath, index=False)
    start = end

# for OBD
per_day_OCD = OCD_total//days
extra_OCD = OCD_total%days


str = 0
for i in range(days):
    chunk_OCD = per_day_OCD + 1 if i < extra_OCD else per_day_OCD
    ed = str + chunk_OCD
    chunk_df_OCD = OCD_dataframe.iloc[str:ed]
    # appending company number
    chunk_df_OCD = pd.concat([chunk_df_OCD,company_df_OCD], ignore_index=False)
    filepath = f"D:\\MERN_Projects\\Github_desktop\\Spitting_automation\\split_days_OCD\\OCD_split_day{i+1}.txt"
    chunk_df_OCD.to_csv(filepath, index=False)
    str = ed