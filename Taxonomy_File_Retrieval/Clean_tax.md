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
