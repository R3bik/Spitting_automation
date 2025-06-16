import pandas as pd

df = pd.read_csv('Sample_data.csv')

# # printing csv
# print(df)

# # for printing 5 rows
# print(df.head(5))

# # check numbers of rows
# print(len(df))

# # check what columns are present
# print(df.columns)

# # getting column as list
# print(list(df.columns))


# taking users input to split data
# Total = len(df)
# Sms_input = int(input('Enter the amount for SMS : '))

# if (Sms_input>Total):
#     print("Input number is greater than total number")
# else:
#     OCD_input = Total - Sms_input


# print(Sms_input)
# print(OCD_input)

# # slicing data

# SMS_dataframe = df.iloc[0:Sms_input,0:1]
# OCD_dataframe = df.iloc[Sms_input:Total,0:1]

# print(f'SMS Dataframe \n',SMS_dataframe)
# print(f'OCD Dataframe \n',OCD_dataframe)

# # Saving Dataframes
# filepath_SMS = "D:\MERN_Projects\Github_desktop\Spitting_automation\Outputs\SMS.csv"
# filepath_OCD = "D:\MERN_Projects\Github_desktop\Spitting_automation\Outputs\OCD.csv"
# SMS_dataframe.to_csv(filepath_SMS, index=False)
# OCD_dataframe.to_csv(filepath_OCD, index=False)

# spiting sms and ocd data according to the days provided the users
SMS_dataframe = pd.read_csv('D:\\MERN_Projects\\Github_desktop\\Spitting_automation\\Outputs\\SMS.csv')
OCD_dataframe = pd.read_csv('D:\\MERN_Projects\\Github_desktop\\Spitting_automation\\Outputs\\OCD.csv')
SMS_total = len(SMS_dataframe)
OCD_total = len(OCD_dataframe)

days = int(input('Enter number of days : '))

# splitting for SMS
per_day = SMS_total//days
extra = SMS_total%days

# slicing the dataframe by looping
start = 0
for i in range(days):
    chunk = per_day + 1 if i < extra else per_day
    end = start + chunk
    chunk_df = SMS_dataframe.iloc[start:end]
    filepath = f"D:\\MERN_Projects\\Github_desktop\\Spitting_automation\\split_days\\SMS_split_day{i+1}.csv"
    chunk_df.to_csv(filepath, index=False)
    start = end
