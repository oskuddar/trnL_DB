

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

Create the NCBI taxID and taxonomy database on your local computer, and use accession numbers to search for the taxID and seven-level taxonomy information.

```{python}
from ete3 import NCBITaxa
import csv
import gzip

#ncbi = NCBITaxa(dbfile="/path/taxa_2024_08.sqlite", taxdump_file="/path/taxdump_aug2024.tar.gz")


ncbi = NCBITaxa(dbfile="/path/taxa_2024_08.sqlite")

ACCESSION2TAXID_FILE = "/path/nucl_gb.accession2taxid_August_2024.gz"
ACCESSION_INPUT = "/path/accessions.txt"
OUTPUT_CSV = "/path/accessions_local_taxid_DB_August_2024.csv"

def load_needed_taxids(filepath, needed_accession_bases):
    acc2taxid = {}
    with gzip.open(filepath, "rt") as f:
        for line in f:
            if line.startswith("accession"):
                continue
            parts = line.strip().split("\t")
            if len(parts) >= 3:
                acc = parts[0].strip()
                taxid = parts[2].strip()
                acc_base = acc.split(".")[0]

                if acc_base in needed_accession_bases and acc_base not in acc2taxid:
                    acc2taxid[acc_base] = taxid

                if len(acc2taxid) == len(needed_accession_bases):
                    break
    return acc2taxid

def get_taxonomy_info(accession_number_with_version, acc2taxid, ncbi):
    acc_base = accession_number_with_version.split(".")[0]
    taxid = acc2taxid.get(acc_base)
    if not taxid:
        return [accession_number_with_version] + [None] * 7 + [None]
    try:
        lineage = ncbi.get_lineage(int(taxid))
        names = ncbi.get_taxid_translator(lineage)
        ranks = ncbi.get_rank(lineage)
        desired_ranks = ['kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species']
        taxonomy_info = [accession_number_with_version]
        for rank in desired_ranks:
            matched_taxids = [tid for tid in lineage if ranks.get(tid) == rank]
            taxonomy_info.append(names.get(matched_taxids[0]) if matched_taxids else None)
        taxonomy_info.append(taxid)
        return taxonomy_info
    except Exception as e:
        print(f"Error fetching taxonomy for {accession_number_with_version}: {e}")
        return [accession_number_with_version] + [None] * 7 + [taxid]

def main():
    with open(ACCESSION_INPUT, 'r') as f:
        accession_numbers = [line.strip() for line in f if line.strip()]
    accession_bases = set(acc.split(".")[0] for acc in accession_numbers)

    acc2taxid = load_needed_taxids(ACCESSION2TAXID_FILE, accession_bases)

    print(f"Found {len(acc2taxid)} / {len(accession_bases)} accessions with taxids.")

    taxonomy_data = []
    for acc in accession_numbers:
        tax_info = get_taxonomy_info(acc, acc2taxid, ncbi)
        taxonomy_data.append(tax_info)

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
