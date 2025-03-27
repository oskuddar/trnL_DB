from ete3 import NCBITaxa
from Bio import Entrez, SeqIO
from Bio.Entrez.Parser import IntegerElement
import csv

ncbi = NCBITaxa()
#ncbi.update_taxonomy_database()

def get_taxid_from_accession(accession, retry_count=3):
    Entrez.email = "email@email.com" #Replace with your email
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
        return [accession_number] + [None] * 7
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
        return taxonomy_info
    except Exception as e:
        print(f"Error fetching taxonomy for {accession_number}: {e}")
        return [accession_number] + [None] * 7

def main():
    ncbi = NCBITaxa()
    input_fasta = "$$$" # Replace with the input fasta file directory
    output_csv = "$$$" # Replace with the output csv file directory
    
    accession_numbers = []
    with open(input_fasta, "r") as fasta_file:
        for record in SeqIO.parse(fasta_file, "fasta"):
            accession_numbers.append(record.id)
    
    seen = set()
    with open(output_csv, "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Accession', 'Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species'])
        for accession in accession_numbers:
            if accession not in seen:
                tax_info = get_taxonomy_info(accession, ncbi)
                writer.writerow(tax_info)
                file.flush()  # Ensure data is written to the file
                seen.add(accession)


if __name__ == "__main__":
    main()
