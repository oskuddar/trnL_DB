from ete3 import NCBITaxa
from Bio import Entrez
from Bio.Entrez.Parser import IntegerElement
import csv

ncbi = NCBITaxa()
#ncbi.update_taxonomy_database()

def get_taxid_from_accession(accession, retry_count=3):
    Entrez.email ="email@email.com" #Replace with your email
    attempt = 0
    while attempt < retry_count:
        try:
            handle = Entrez.esummary(db="nucleotide", id=accession, retmode="xml")
            records = Entrez.read(handle)
            taxid = records[0]['TaxId']
            if isinstance(taxid, IntegerElement):
                taxid = int(taxid)
            return str(taxid)
        except Exception as e:
            print(f"Attempt {attempt+1}: Error processing accession {accession}: {e}")
            attempt += 1
    print(f"Failed to process accession {accession} after {retry_count} attempts")
    return None

def get_taxonomy_info(accession_number, ncbi):
    taxid = get_taxid_from_accession(accession_number)
    if not taxid:
        return [accession_number] + [None] * 7 + [None]  # Include None for TaxId at the end
    try:
        lineage = ncbi.get_lineage(taxid)
        names = ncbi.get_taxid_translator(lineage)
        ranks = ncbi.get_rank(lineage)
        name_rank_dict = {taxid: (names.get(taxid, None), ranks.get(taxid, None)) for taxid in lineage}
        desired_ranks = ['kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species']
        taxonomy_info = [accession_number]
        for rank in desired_ranks:
            matched_taxids = [taxid for taxid, (name, rank_val) in name_rank_dict.items() if rank_val == rank]
            if matched_taxids:
                taxonomy_info.append(names[matched_taxids[0]])
            else:
                taxonomy_info.append(None)
        taxonomy_info.append(taxid)  # Add TaxId at the end
        return taxonomy_info
    except Exception as e:
        print(f"Error fetching taxonomy for {accession_number}: {e}")
        return [accession_number] + [None] * 7 + [taxid]  # Include TaxId at the end

def main():
    ncbi = NCBITaxa()
    with open('/directory/unfound_accession_number_text_file.txt', 'r') as file: #change the directory and the file name
        accession_numbers = [line.strip() for line in file]
    taxonomy_data = []
    seen = {}
    for accession in accession_numbers:
        if accession not in seen:
            tax_info = get_taxonomy_info(accession, ncbi)
            taxonomy_data.append(tax_info)
            seen[accession] = True
    with open('/directory/unfound_accession_number_csv_file.csv', 'w', newline='') as file:  #change the directory and the file name
        writer = csv.writer(file)
        writer.writerow(['Acc', 'Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species', 'TaxID'])  # TaxId as the last column
        writer.writerows(taxonomy_data)


if __name__ == "__main__":
    main()
