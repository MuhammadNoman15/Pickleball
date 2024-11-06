import pandas as pd

# Load the CSV file
csv_file = 'USA_Pickleball_org_Complete_Data.csv'  # Replace with your CSV file path
df = pd.read_csv(csv_file)

# Save it as an XLSX file
xlsx_file = 'USA_Pickleball_org_Complete_Data2.xlsx'  # Replace with your desired XLSX file path
df.to_excel(xlsx_file, index=False)
