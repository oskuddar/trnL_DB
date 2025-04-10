**Clean the taxonomy file if needed**
\
*(use python)*

```{python}
import pandas as pd
# File path
file_path = "All_taxonomy_combined.csv"

# List of symbols
symbols = ['!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~']

# Read the CSV file
df = pd.read_csv(file_path, low_memory=False)


# Replace "." with an empty string and "_" with a space in the DataFrame
for column in df.columns:
    if column == 'Species':
        df[column] = df[column].apply(lambda x: x.replace(".", "").replace("_", " ").replace("#", "").
                 replace("'", "").replace("(", " ").replace("[", "").replace(")", "").
                 replace(":", " ").
                 replace("]", "").replace("&", "").replace(",", "").replace("/", " ") if isinstance(x, str) else x)
                 
for column in df.columns:
    if column == 'Genus':
        df[column] = df[column].apply(lambda x: x.replace("'", "").replace("[", "").
                                      replace("]", "") if isinstance(x, str) else x)

# Remove after 2nd word
df['Species'] = df['Species'].apply(lambda x: ' '.join(x.split()[:3]) if isinstance(x, str) and len(x.split()) > 2 and x.split()[1] == "x" else ' '.join(x.split()[:2]) if isinstance(x, str) else x)

# Print the count of each symbol in each column
# for symbol in symbols:
#     for column in df.columns:
#         count = df[column].astype(str).str.count('\\' + symbol).sum()
#         if count > 0:
#             print(f"The symbol {symbol} is present {count} times in the column {column}.")

df.to_csv("All_taxonomy_Jan122024.csv", index=False)
```

Then filter the taxonomy 

```{python}
import pandas as pd

# File path
taxonomy_file = "All_taxonomy_Jan122024.csv"
output_file = "All_taxonomy_Jan122024_clean.csv"

# Load taxonomy data
taxonomy_df = pd.read_csv(taxonomy_file)

# Replace string 'NAN' with actual NaN
taxonomy_df.replace("NAN", pd.NA, inplace=True)

# Remove rows where Phylum is 'Prasinodermophyta' or 'Chlorophyta'
filtered_df = taxonomy_df[~taxonomy_df['Phylum'].isin(['Prasinodermophyta', 'Chlorophyta'])]

# Remove rows where both Genus and Species are blank or NaN
filtered_df = filtered_df[~(filtered_df['Genus'].isna() & filtered_df['Species'].isna())]

# Remove rows containing specific words
keywords = ["environmental", "uncultured", "unclassified", "unidentified", "unverified", "nan mycorrhizal", "nan sp", "nan Chlorophyta", "nan bequaertii","nan Ceiba","nan Cylindrocystis", "nan environmental", "nan Klebsormidium", "nan plant", "nan poilanei", "nan prasinophyte", "nan Streptophyta"]
filtered_df = filtered_df[~filtered_df.apply(lambda row: any(keyword in str(row).lower() for keyword in keywords), axis=1)]

# Save the filtered DataFrame to a new CSV file
filtered_df.to_csv(output_file, index=False)

print(f"Filtered taxonomy saved to: {output_file}")
```
