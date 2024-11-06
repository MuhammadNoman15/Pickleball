import pandas as pd
from datetime import datetime

# Function to sort dates based on the start date of the range
def sort_by_start_date(df, date_column):
    # Extract the start date for each range
    df['Start_Date'] = df[date_column].apply(lambda x: x.split(" - ")[0])
    # Convert the start dates to datetime format for sorting
    df['Start_Date'] = pd.to_datetime(df['Start_Date'], format="%b %d, %Y")
    # Sort by the extracted start dates
    df = df.sort_values(by='Start_Date')
    # Drop the auxiliary 'Start_Date' column after sorting
    df = df.drop(columns=['Start_Date'])
    return df

# Load the Excel file
input_file = "Complete_Data_Updated.xlsx"  # Replace with your file path
output_file = "Complete_Data_Updated_Sorted.xlsx"  # File to save the sorted data
df = pd.read_excel(input_file)

# Apply the function to format and sort the 'Date' column
df = sort_by_start_date(df, 'Date')

# Save the modified DataFrame back to a new Excel file
df.to_excel(output_file, index=False)

print("Date formatted, sorted in ascending order, and saved to output_sorted.xlsx.")
