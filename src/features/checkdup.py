import polars as pl
import re
import os 

# Define the directory path where the files are located
directory = r'D:\Private\Work\Program\MRO_craw\output\Craw'

# List all files in the specified directory
files = os.listdir(directory)

# Create an empty list to store information items
infor_items = []

# Iterate through each file in the directory
for file in files:
    # Create the full file path by joining the directory path and the file name
    f = os.path.join(directory, file)

    # Read the contents of the CSV file using pandas
    web_df = pl.read_csv(f)

    # Extract the 'Item information' column from the DataFrame and convert it to a list
    info_items = pl.Series(web_df['Item information']).to_list()

    # Add the extracted information items to the existing list
    infor_items = info_items + infor_items

def check_dup(infor_items):
    # Function checks for duplicate IDs in a list of information items.
    # Define a regular expression pattern to extract the 'Mã hệ thống' value from each item.
    pattern = r"'Mã hệ thống:\s*([^']*)'"

    # Create an empty list to store the extracted ID values.
    id_link = []

    # Iterate through each item in the 'infor_items' list.
    for i in infor_items:
        # Use regular expression 're.search' to find a match for the pattern in the item.
        match = re.search(pattern, i)

        # Check if a match was found.
        if match:
            # Extract the ID value from the match group.
            id_value = match.group(1)

            # Append the ID value to the 'id_link' list.
            id_link.append(id_value)

    # Check if there are any duplicate IDs in the 'id_link' list.
    if len(id_link) == len(set(id_link)):
        # If no duplicates are found, print a message indicating that there are no duplicate IDs.
        print('Khong bi trung id')
        df = None
    else:
        # If duplicate IDs are found, print a message indicating that there are duplicate IDs.
        print('Co id bi trung')
        
        # Create a pandas DataFrame with the duplicate 'ID' values.
        df = pl.DataFrame({'ID': id_link})
        
        # Filter the DataFrame to keep only the duplicated rows.
        df.filter(df.is_duplicated())

    # Return the resulting DataFrame that may contain duplicate 'ID' values.
    return df

if __name__ == "__main__":
    id_link = check_dup(infor_items)
    print(id_link)