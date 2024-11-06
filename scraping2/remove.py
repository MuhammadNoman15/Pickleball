import pandas as pd

# Load the Excel file
df = pd.read_excel("Allpickleballtournaments_Data_500_1000.xlsx")

# Remove duplicates
df_cleaned = df.drop_duplicates()

# Save the cleaned data back to a new Excel file
df_cleaned.to_excel("Allpickleballtournaments_Data_500_1000_1.xlsx", index=False)

print("Duplicates removed. Cleaned file saved as 'cleaned_file.xlsx'")
