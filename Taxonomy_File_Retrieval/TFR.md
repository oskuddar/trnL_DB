

Download the specific version of the taxonomy file from:
https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump_archive/

-- In our case it is from August 2024 --

```{bash}
wget https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump_archive/taxdmp_2024-08-01.zip && unzip /path/taxdmp_2024-08-01.zip -d /path/taxdump_aug2024
```

```{bash}
cd /path/taxdump_aug2024
tar -czf /path/taxdump_aug2024.tar.gz *
```
Download both "wgs" and "gb" accession2taxid files from (accession2taxid) [https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/accession2taxid/]
----------------------*Unfortunately, older versions are not available on NCBI.*----------------------

Create the NCBI taxID and taxonomy database on your local computer, and use accession numbers to search for the taxID and seven-level taxonomy information.

```{python}
from ete3 import NCBITaxa
import csv
import gzip
from functools import lru_cache

ncbi = NCBITaxa(dbfile="/path/Taxonomy_Files/taxa_2025_04.sqlite")

ACCESSION2TAXID_FILE = ""

ACCESSION2TAXID_FILES = [
    "/path/Taxonomy_Files/nucl_gb.accession2taxid_April_2025.gz",
    "/path/Taxonomy_Files/nucl_wgs.accession2taxid_April_2025.gz"
]

ACCESSION_INPUT = "/path/accessions.txt"
OUTPUT_CSV = "/path/accessions_local_taxid_DB_April_2025.csv"

# --- Efficient TaxID loader ---
def load_needed_taxids(filepath, needed_accession_bases):
    acc2taxid = {}
    needed = set(needed_accession_bases)  # Make mutable
    with gzip.open(filepath, "rt") as f:
        for line in f:
            if line.startswith("accession"):
                continue
            parts = line.strip().split("\t")
            if len(parts) >= 3:
                acc_base = parts[0].split(".")[0]
                if acc_base in needed:
                    acc2taxid[acc_base] = parts[2].strip()
                    needed.remove(acc_base)
                    if not needed:
                        break
    return acc2taxid

def load_needed_taxids_from_multiple(files, needed_accession_bases):
    acc2taxid = {}
    needed = set(needed_accession_bases)
    for filepath in files:
        acc2taxid.update(load_needed_taxids(filepath, needed))
        needed -= set(acc2taxid.keys())
        if not needed:
            break
    return acc2taxid

# --- Cached lineage lookup ---
@lru_cache(maxsize=10000)
def get_cached_lineage(taxid):
    lineage = ncbi.get_lineage(taxid)
    names = ncbi.get_taxid_translator(lineage)
    ranks = ncbi.get_rank(lineage)
    return lineage, names, ranks

# --- Per-accession taxonomy row ---
def get_taxonomy_info(accession_number_with_version, acc2taxid):
    acc_base = accession_number_with_version.split(".")[0]
    taxid_str = acc2taxid.get(acc_base)
    if not taxid_str:
        return [accession_number_with_version] + [None] * 7 + [None]
    try:
        taxid = int(taxid_str)
        lineage, names, ranks = get_cached_lineage(taxid)
        desired_ranks = ['kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species']
        row = [accession_number_with_version]
        for rank in desired_ranks:
            matched = [tid for tid in lineage if ranks.get(tid) == rank]
            row.append(names.get(matched[0]) if matched else None)
        row.append(taxid)
        return row
    except Exception as e:
        print(f"Error with {accession_number_with_version}: {e}")
        return [accession_number_with_version] + [None] * 7 + [taxid_str]

# --- Main ---
def main():
    with open(ACCESSION_INPUT, 'r') as f:
        accession_numbers = [line.strip() for line in f if line.strip()]
    accession_bases = set(acc.split(".")[0] for acc in accession_numbers)

    acc2taxid = load_needed_taxids_from_multiple(ACCESSION2TAXID_FILES, accession_bases)
    print(f"Found {len(acc2taxid)} / {len(accession_bases)} accessions with taxids.")

    seen = set()
    taxonomy_data = []
    for acc in accession_numbers:
        row = get_taxonomy_info(acc, acc2taxid)
        t = tuple(row)
        if t not in seen:
            taxonomy_data.append(row)
            seen.add(t)

    with open(OUTPUT_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Acc', 'Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species', 'TaxID'])
        writer.writerows(taxonomy_data)

if __name__ == "__main__":
    main()

```


***Just in case some taxonomy information for accession numbers is not provided:***
* Check the final CSV file for empty rows, collect the accession numbers, and manually retrieve the missing data from [genbank](https://www.ncbi.nlm.nih.gov/genbank/)\
\
Example of the input text file (accessions.txt):
```
MW174172.1
MT240944.1
OM022238.1
OM022237.1
```
Example of the output csv file (accessions_local_taxid_DB_August_2024.csv):
```
Acc	Kingdom	Phylum	Class	Order	Family	Genus	Species	TaxID
MW174172.1	Viridiplantae	Streptophyta	Magnoliopsida	Lamiales	Acanthaceae	Acanthus	Acanthus ilicifolius	328098
MT240944.1	Viridiplantae	Streptophyta	Magnoliopsida	Lamiales	Acanthaceae	Acanthus	Acanthus ebracteatus	241842
OM022238.1	Viridiplantae	Streptophyta	Magnoliopsida	Lamiales	Acanthaceae	Acanthus	Acanthus mollis	76277
OM022237.1	Viridiplantae	Streptophyta	Magnoliopsida	Lamiales	Acanthaceae	Acanthus	Acanthus leucostachyus	1605257
```

**Clean the taxonomy file by removing symbols and binary species names (excluding hybrids) using the Python code in Clean_tax.md.**
.
