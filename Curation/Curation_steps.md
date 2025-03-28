All codes are written in Python except CD-HIT sbatch run\
**Users should consider changing the input and output file names and directories*\
\
\
**Convert the sequences to uppercase and add the version number to the accession number (Used specifically for OBITools3)**

```{python}
import os
from Bio import SeqIO
import pandas as pd

# File paths
input_fasta = "All_trnl_CD.fasta"
output_fasta = "All_trnl_CD_uppercase.fasta"
taxonomy_file = "All_taxonomy_Jan162024.csv"

# Load taxonomy data
taxonomy_df = pd.read_csv(taxonomy_file)

# Create a dictionary for fast lookup of versioned accession numbers
taxonomy_dict = {acc.split('.')[0]: acc for acc in taxonomy_df['Acc'] if '.' in acc and not acc.endswith('.1')}

# Process the FASTA file in a single pass: update headers and convert sequences to uppercase
with open(input_fasta) as infile, open(output_fasta, "w") as outfile:
    for record in SeqIO.parse(infile, "fasta"):
        header = record.id.split()[0]
        record.id = taxonomy_dict.get(header, f"{header}.1")  # Assign version if found, else default to .1
        record.description = ""  # Remove description
        record.seq = record.seq.upper()  # Convert sequence to uppercase
        SeqIO.write(record, outfile, "fasta")

print(f"Processed FASTA file created at: {output_fasta}")
```
\
**Filter ambiguous sequences**
```{python}
import os
import pandas as pd
from Bio import SeqIO

# File paths
fasta_file = "All_trnl_CD_uppercase.fasta"
taxonomy_file = "All_taxonomy_Jan162024.csv"
output_fasta = "All_trnl_CD_uppercase_cleaned.fasta"
unfound_accessions_file = "All_trnl_CD_uppercase_unfound_acc.txt"
invalid_sequences_file = "All_trnl_CD_uppercase_invalid.fasta"

# Load taxonomy data
taxonomy_df = pd.read_csv(taxonomy_file)
taxonomy_df['Acc'] = taxonomy_df['Acc'].str.strip()  # Ensure no leading/trailing whitespace
taxonomy_df['BaseAcc'] = taxonomy_df['Acc'].str.split('.').str[0]  # Extract base accessions

# Create mapping dictionaries
base_to_full_acc = dict(zip(taxonomy_df['BaseAcc'], taxonomy_df['Acc']))  # Base to full accession
acc_to_species = dict(zip(taxonomy_df['Acc'], taxonomy_df['Species']))  # Full accession to species

# Initialize containers
valid_sequences = []  # To store valid sequences for the final FASTA
unfound_accessions = set()
invalid_sequences = []

# Function to validate sequences
def is_valid_sequence(record):
    seq = str(record.seq)
    n_count = seq.count("N")
    invalid_bases = [char for char in seq if char not in "ATGCN"]  # Detect non-IUPAC bases
    if n_count > 0 or len(invalid_bases) > 0:
        invalid_sequences.append(f">{record.id}\n{seq}\n")  # Add '>' for invalid sequences
        return False
    return True

# Process FASTA file and resolve accessions
with open(fasta_file) as fasta:
    for record in SeqIO.parse(fasta, "fasta"):
        acc = record.id.split()[0].strip()  # Clean and extract accession number
        acc = acc.lstrip('>')  # Remove any leading '>' character
        base_acc = acc.split('.')[0]  # Extract base accession (without version)
        full_acc = base_to_full_acc.get(base_acc)  # Resolve to full accession using base accession

        if is_valid_sequence(record):
            if full_acc and full_acc in acc_to_species:
                valid_sequences.append(record)  # Add valid record to the final list
            else:
                unfound_accessions.add(acc)  # Add only the cleaned accession number to the unfound list

# Write all valid sequences to a single FASTA file
with open(output_fasta, "w") as outfile:
    SeqIO.write(valid_sequences, outfile, "fasta")

# Write invalid sequences to a file
if invalid_sequences:
    with open(invalid_sequences_file, "w") as invalid_file:
        invalid_file.writelines(invalid_sequences)

# Write unfound accession numbers to a file (cleaned of '>'): 
if unfound_accessions:
    with open(unfound_accessions_file, "w") as outfile:
        outfile.write("\n".join(sorted(unfound_accessions)) + "\n")  # Write only cleaned accession numbers

print(f"Cleaned FASTA file saved to: {output_fasta}")
print(f"Unmatched accessions written to: {unfound_accessions_file}")
print(f"Invalid sequences written to: {invalid_sequences_file}")
print(f"Total sequences in FASTA: {len(valid_sequences) + len(unfound_accessions)}")
print(f"Valid sequences: {len(valid_sequences)}")
print(f"Unfound accessions: {len(unfound_accessions)}")

```
\
**Create a taxonomy file for each fasta folder**

```{python}
import os
from Bio import SeqIO
import pandas as pd

# Input file paths
fasta_file = "All_trnl_CD_uppercase_cleaned.fasta"  # Single FASTA file
taxonomy_file = "All_taxonomy_Jan162024.csv"
output_csv = "All_trnl_CD_uppercase_cleaned_taxonomy.csv"  # Output CSV file

# Load taxonomy data
taxonomy_df = pd.read_csv(taxonomy_file)
taxonomy_df['Acc'] = taxonomy_df['Acc'].str.strip()  # Ensure no leading/trailing whitespace
valid_accessions = set(taxonomy_df['Acc'])  # Set of valid accessions from the taxonomy file

# Prepare a set to store matching accessions
matching_accessions = set()

# Process the single FASTA file
with open(fasta_file) as fasta:
    for record in SeqIO.parse(fasta, "fasta"):
        header = record.id.split()[0]  # Extract accession number from the header
        if header in valid_accessions:  # Check if the header is in the taxonomy file
            matching_accessions.add(header)  # Add to the set of matching accessions

# Filter the taxonomy DataFrame for matching accessions
filtered_taxonomy = taxonomy_df[taxonomy_df['Acc'].isin(matching_accessions)]

# Save the filtered taxonomy to a new CSV file
filtered_taxonomy.to_csv(output_csv, index=False)

print(f"Filtered taxonomy written to: {output_csv}")

```
\
**Clean taxonomy file [remove if phylum is 'Prasinodermophyta' or 'Chlorophyta'], also remove rows if both species and genus are blank or NaN**


```{python}
import pandas as pd

# File path
taxonomy_file = "All_trnl_CD_uppercase_cleaned_taxonomy.csv"
output_file = "All_trnl_CD_uppercase_cleaned_taxonomy_clean.csv"

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
\
**Remove the fasta entries if they are not present in the clean taxonomy file**

```{python}
import os
from Bio import SeqIO
import pandas as pd

# File paths
taxonomy_file = "All_trnl_CD_uppercase_cleaned_taxonomy_clean.csv"
input_fasta_file = "All_trnl_CD_uppercase_cleaned.fasta"  # Original FASTA file
output_fasta_file = "All_trnl_CD_uppercase_cleaned_filtered.fasta"  # New filtered FASTA file

# Load taxonomy data
taxonomy_df = pd.read_csv(taxonomy_file)
valid_accessions = set(taxonomy_df['Acc'].str.strip())  # Set of valid accessions from taxonomy

# Process the single FASTA file and write to a new file
filtered_sequences = []
with open(input_fasta_file) as fasta, open(output_fasta_file, "w") as outfile:
    for record in SeqIO.parse(fasta, "fasta"):
        header = record.id.split()[0].strip()  # Extract accession number from the header
        if header in valid_accessions:  # Keep only matching accessions
            SeqIO.write(record, outfile, "fasta")  # Write directly to new FASTA file

print(f"Filtered FASTA file created: {output_fasta_file}")

```
\
**Filter by Length**

```{python}
from Bio import SeqIO

# Input file paths
fasta_files = [
    "All_trnl_CD_uppercase_cleaned_filtered.fasta",
    "All_trnl_CD_uppercase_cleaned_filtered.fasta",
    "All_trnl_CD_uppercase_cleaned_filtered.fasta",
]
min_lengths = [234, 81, 8]
max_lengths = [1566, 484, 220]

# Process each FASTA file

for fasta_file, min_len, max_len in zip(fasta_files, min_lengths, max_lengths):
    output_file = f"{fasta_file.rsplit('.', 1)[0]}_filtered.fasta"  # Add "_filtered" to the output file name

    # Read and filter sequences
    filtered_sequences = []
    for record in SeqIO.parse(fasta_file, "fasta"):
        seq_length = len(record.seq)
        if min_len <= seq_length <= max_len:  # Check if sequence length is within the range
            filtered_sequences.append(record)

    # Write the filtered sequences to the output FASTA file
    with open(output_file, "w") as output_fasta:
        SeqIO.write(filtered_sequences, output_fasta, "fasta")

    print(f"Filtered sequences saved to: {output_file}")

```
\
**Split by Species**

```{python}
import os
import pandas as pd
from Bio import SeqIO
from collections import defaultdict

# File paths
fasta_file = "All_trnl_CD_uppercase_cleaned_filtered.fasta"
taxonomy_file = "All_trnl_CD_uppercase_cleaned_taxonomy_clean.csv"
output_dir = "All_trnl_CD_cleaned_filtered_Species"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Load taxonomy data
taxonomy_df = pd.read_csv(taxonomy_file)
taxonomy_df['Acc'] = taxonomy_df['Acc'].str.strip()  # Ensure no leading/trailing whitespace

# Create a dictionary to map accession to species
acc_to_species = dict(zip(taxonomy_df['Acc'], taxonomy_df['Species']))

# Initialize a container to store sequences by species
species_sequences = defaultdict(list)

# Process FASTA file and split by species
with open(fasta_file) as fasta:
    for record in SeqIO.parse(fasta, "fasta"):
        acc = record.id.split()[0].strip()  # Extract accession number from the header
        
        # Get species name from the accession
        species = acc_to_species.get(acc)
        if species:  # If species is found
            species_name = species.replace(' ', '_')  # Format species name
            species_sequences[species_name].append(f">{record.id}\n{str(record.seq)}\n")

# Write species-specific FASTA files
for species_name, sequences in species_sequences.items():
    output_path = os.path.join(output_dir, f"{species_name}.fasta")
    with open(output_path, "w") as species_file:
        species_file.writelines(sequences)

print(f"Species-specific FASTA files saved to: {output_dir}")
```
\
**CD-HIT to cluster exact sequences within the same species fasta files:**
```{bash}

#!/bin/bash

#SBATCH --job-name="cdhit"
#SBATCH --output="cdhit_%j.out"
#SBATCH --error="cdhit_%j.err"
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --mem=16G

# Define input and output directories
input_directory="All_trnl_CD_cleaned_filtered_Species"
output_directory="All_trnl_CD_cleaned_filtered_Species_CDHIT"

# Create output directory if it doesn't exist
mkdir -p "$output_directory"

# Load CD-HIT module (if needed)
module load cd-hit  # Ensure cd-hit is available in your environment

# Process each FASTA file in the input directory
for input_file in "$input_directory"/*.fasta; do
    if [ -f "$input_file" ]; then
        filename=$(basename "$input_file")  # Extract the filename
        output_file="$output_directory/$filename"  # Define the output file path
        cd-hit-est -i "$input_file" -o "$output_file" -c 1.0 -n 10 -T 0 -d 0  # Run CD-HIT-EST
    fi
done

echo "CD-HIT filtering complete. Results saved in $output_directory"

```
\
**Combine CD_HIT output fasta files**

```{bash}
sbatch --mem=10G --wrap "for file in All_trnl_CD_cleaned_filtered_Species_CDHIT/*.fasta; do cat \"\$file\" >> All_trnl_CD_cleaned_filtered_Species_CDHIT.fasta; done"
```

\
**Create a taxonomy file for the final fasta file**

```{python}
import os
from Bio import SeqIO
import pandas as pd

# Input file paths
fasta_file = "All_trnl_CD_cleaned_filtered_Species_CDHIT.fasta"  # Single FASTA file
taxonomy_file = "All_trnl_CD_uppercase_cleaned_taxonomy_clean.csv"
output_csv = "All_trnl_CD_Final_Taxonomy.csv"  # Output CSV file

# Load taxonomy data
taxonomy_df = pd.read_csv(taxonomy_file)
taxonomy_df['Acc'] = taxonomy_df['Acc'].str.strip()  # Ensure no leading/trailing whitespace
valid_accessions = set(taxonomy_df['Acc'])  # Set of valid accessions from the taxonomy file

# Prepare a set to store matching accessions
matching_accessions = set()

# Process the single FASTA file
with open(fasta_file) as fasta:
    for record in SeqIO.parse(fasta, "fasta"):
        header = record.id.split()[0]  # Extract accession number from the header
        if header in valid_accessions:  # Check if the header is in the taxonomy file
            matching_accessions.add(header)  # Add to the set of matching accessions

# Filter the taxonomy DataFrame for matching accessions
filtered_taxonomy = taxonomy_df[taxonomy_df['Acc'].isin(matching_accessions)]

# Save the filtered taxonomy to a new CSV file
filtered_taxonomy.to_csv(output_csv, index=False)

print(f"Filtered taxonomy written to: {output_csv}")

```
