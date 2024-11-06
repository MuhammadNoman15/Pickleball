import pandas as pd

# Load your existing Excel file
file_path = 'USA_Pickleball_org_Complete_Data3.xlsx'  # Replace with your actual file path
df = pd.read_excel(file_path)

# Add the new column with the hardcoded URL
df['Source'] = 'https://usapickleball.org/'

# Save the updated DataFrame back to Excel
df.to_excel('USA_Pickleball_org_Complete_Data3_Updated.xlsx', index=False)  # Replace with desired output file name
