* Replace the email@email.com with your own email address
<h3>Download EMBL Sequences {EMBL(4,792,161)}</h3>

`nohup crabs db_download --source ncbi --database nucleotide --query '("Viridiplantae"[Organism] OR Viridiplantae[All Fields]) AND (biomol_genomic[PROP] AND embl[filter] AND is_nuccore[filter])' --output embl-viridiplantae_June2024.fasta --keep_original yes --email email@email.com --batchsize 5000 &`

<h3>Download DDBJ Sequences {DDBJ(1,077,244)}</h3>

`nohup crabs db_download --source ncbi --database nucleotide --query '("Viridiplantae"[Organism] OR Viridiplantae[All Fields]) AND (biomol_genomic[PROP] AND ddbj[filter] AND is_nuccore[filter])' --output ddbj-viridiplantae_June2024.fasta --keep_original yes --email email@email.com --batchsize 5000 &`

<h3>Download RefSeq Sequences {RefSeq(2,110,972)}-Split by 3</h3>

`nohup crabs db_download --source ncbi --database nucleotide --query '("Viridiplantae"[Organism] OR ("Viridiplantae"[Organism] OR Viridiplantae[All Fields])) AND (biomol_genomic[PROP] AND refseq[filter] AND is_nuccore[filter]) AND ("0001/01/01"[MDAT] : "2018/12/31"[MDAT])' --output refseq-1-viridiplantae_June2024.fasta --keep_original yes --email email@email.com --batchsize 5000 &`
\
\
`nohup crabs db_download --source ncbi --database nucleotide --query '("Viridiplantae"[Organism] OR Viridiplantae[All Fields]) AND (biomol_genomic[PROP] AND refseq[filter] AND ("2018/12/30"[MDAT] : "2021/12/30"[MDAT]))' --output refseq-2-viridiplantae_June2024.fasta --keep_original yes --email email@email.com --batchsize 5000 &`
\
\
`nohup crabs db_download --source ncbi --database nucleotide --query '("Viridiplantae"[Organism] OR Viridiplantae[All Fields]) AND (biomol_genomic[PROP] AND refseq[filter] AND ("2021/12/29"[MDAT] : "2024/12/30"[MDAT]))' --output refseq-3-viridiplantae_June2024.fasta --keep_original yes --email email@email.com --batchsize 5000 &`


<h3>Download GenBank Sequences {GenBank(6,914,516)}-Split by 16</h3>

`nohup crabs db_download --source ncbi --database nucleotide --query '("Viridiplantae"[Organism] OR ("Viridiplantae"[Organism] OR Viridiplantae[All Fields])) AND (biomol_genomic[PROP] AND genbank[filter] AND is_nuccore[filter]) AND ("0001/01/01"[PDAT] : "2010/12/31"[PDAT])' --output genbank-1-viridiplantae_June2024.fasta --keep_original yes --email email@email.com --batchsize 5000 &`
\
\
`nohup crabs db_download --source ncbi --database nucleotide --query '("Viridiplantae"[Organism] OR ("Viridiplantae"[Organism] OR Viridiplantae[All Fields])) AND (biomol_genomic[PROP] AND genbank[filter] AND is_nuccore[filter]) AND ("2010/12/30"[PDAT] : "2013/12/31"[PDAT])' --output genbank-2-viridiplantae_June2024.fasta --keep_original yes --email email@email.com --batchsize 5000 &`
\
\
`nohup crabs db_download --source ncbi --database nucleotide --query '("Viridiplantae"[Organism] OR ("Viridiplantae"[Organism] OR Viridiplantae[All Fields])) AND (biomol_genomic[PROP] AND genbank[filter] AND is_nuccore[filter]) AND ("2013/12/30"[PDAT] : "2016/12/31"[PDAT])' --output genbank-3-viridiplantae_June2024.fasta --keep_original yes --email email@email.com --batchsize 5000 &`
\
\
`nohup crabs db_download --source ncbi --database nucleotide --query '("Viridiplantae"[Organism] OR ("Viridiplantae"[Organism] OR Viridiplantae[All Fields])) AND (biomol_genomic[PROP] AND genbank[filter] AND is_nuccore[filter]) AND ("2016/12/30"[PDAT] : "2019/12/31"[PDAT])' --output genbank-4-viridiplantae_June2024.fasta --keep_original yes --email email@email.com --batchsize 5000 &`
\
\
`nohup crabs db_download --source ncbi --database nucleotide --query '("Viridiplantae"[Organism] OR Viridiplantae[All Fields]) AND (biomol_genomic[PROP] AND genbank[filter] AND is_nuccore[filter] AND ("2019/12/30"[MDAT] : "2020/12/31"[MDAT]))' --output genbank-5-viridiplantae_June2024.fasta --keep_original yes --email email@email.com --batchsize 5000 &`
\
\
`nohup crabs db_download --source ncbi --database nucleotide --query '("Viridiplantae"[Organism] OR Viridiplantae[All Fields]) AND (biomol_genomic[PROP] AND genbank[filter] AND is_nuccore[filter] AND ("2020/12/30"[MDAT] : "2021/6/31"[MDAT]))' --output genbank-6_a-viridiplantae_June2024.fasta --keep_original yes --email email@email.com --batchsize 5000 &`
\
\
`nohup crabs db_download --source ncbi --database nucleotide --query '("Viridiplantae"[Organism] OR Viridiplantae[All Fields]) AND (biomol_genomic[PROP] AND genbank[filter] AND is_nuccore[filter] AND ("2021/6/30"[MDAT] : "2021/12/31"[MDAT]))' --output genbank-6_b-viridiplantae_June2024.fasta --keep_original yes --email email@email.com --batchsize 5000 &`
\
\
`nohup crabs db_download --source ncbi --database nucleotide --query '("Viridiplantae"[Organism] OR Viridiplantae[All Fields]) AND (biomol_genomic[PROP] AND genbank[filter] AND is_nuccore[filter] AND ("2021/12/30"[MDAT] : "2022/6/31"[MDAT]))' --output genbank-7-viridiplantae_June2024.fasta --keep_original yes --email email@email.com --batchsize 5000 &`
\
\
`nohup crabs db_download --source ncbi --database nucleotide --query '("Viridiplantae"[Organism] OR Viridiplantae[All Fields]) AND (biomol_genomic[PROP] AND genbank[filter] AND is_nuccore[filter] AND ("2022/6/30"[MDAT] : "2022/9/31"[MDAT]))' --output genbank-8-a-viridiplantae_June2024.fasta --keep_original yes --email email@email.com --batchsize 5000 &`
\
\
`nohup crabs db_download --source ncbi --database nucleotide --query '("Viridiplantae"[Organism] OR Viridiplantae[All Fields]) AND (biomol_genomic[PROP] AND genbank[filter] AND is_nuccore[filter] AND ("2022/9/30"[MDAT] : "2022/12/31"[MDAT]))' --output genbank-8-b-viridiplantae_June2024.fasta --keep_original yes --email email@email.com --batchsize 5000 &`
\
\
`nohup crabs db_download --source ncbi --database nucleotide --query '("Viridiplantae"[Organism] OR Viridiplantae[All Fields]) AND (biomol_genomic[PROP] AND genbank[filter] AND is_nuccore[filter] AND ("2022/12/30"[MDAT] : "2023/1/31"[MDAT]))' --output genbank-9-viridiplantae_June2024.fasta --keep_original yes --email email@email.com --batchsize 5000 &`
\
\
`nohup crabs db_download --source ncbi --database nucleotide --query '("Viridiplantae"[Organism] OR Viridiplantae[All Fields]) AND (biomol_genomic[PROP] AND genbank[filter] AND is_nuccore[filter] AND ("2023/1/30"[MDAT] : "2023/6/31"[MDAT]))' --output genbank-10-viridiplantae_June2024.fasta --keep_original yes --email email@email.com --batchsize 5000 &`
\
\
`nohup crabs db_download --source ncbi --database nucleotide --query '("Viridiplantae"[Organism] OR Viridiplantae[All Fields]) AND (biomol_genomic[PROP] AND genbank[filter] AND is_nuccore[filter] AND ("2023/6/30"[MDAT] : "2023/9/31"[MDAT]))' --output genbank-11-viridiplantae_June2024.fasta --keep_original yes --email email@email.com --batchsize 5000 &`
\
\
`nohup crabs db_download --source ncbi --database nucleotide --query '("Viridiplantae"[Organism] OR Viridiplantae[All Fields]) AND (biomol_genomic[PROP] AND genbank[filter] AND is_nuccore[filter] AND ("2023/9/30"[MDAT] : "2023/12/31"[MDAT]))' --output genbank-12-viridiplantae_June2024.fasta --keep_original yes --email email@email.com --batchsize 5000 &`
\
\
`nohup crabs db_download --source ncbi --database nucleotide --query '("Viridiplantae"[Organism] OR Viridiplantae[All Fields]) AND (biomol_genomic[PROP] AND genbank[filter] AND is_nuccore[filter] AND ("2023/12/30"[MDAT] : "2024/4/31"[MDAT]))' --output genbank-13-viridiplantae_June2024.fasta --keep_original yes --email email@email.com --batchsize 5000 &`
\
\
`nohup crabs db_download --source ncbi --database nucleotide --query '("Viridiplantae"[Organism] OR Viridiplantae[All Fields]) AND (biomol_genomic[PROP] AND genbank[filter] AND is_nuccore[filter] AND ("2024/4/30"[MDAT] : "2024/12/31"[MDAT]))' --output genbank-14-viridiplantae_June2024.fasta --keep_original yes --email email@email.com --batchsize 5000 &`

<h3>Download TPA Sequences {TPA(3,014)}</h3>

`nohup crabs db_download --source ncbi --database nucleotide --query '("Viridiplantae"[Organism] AND (biomol_genomic[PROP] AND tpa_srcdb[filter] AND is_nuccore[filter]))' --output tpa-viridiplantae_June2024.fasta --keep_original yes --email hadi@gmail.com --batchsize 5000 &`

<h3>Download BOLD Sequences</h3>

`nohup crabs db_download --source bold --database 'Bryophyta|Chlorophyta|Lycopodiophyta|Magnoliophyta|Pinophyta|Pteridophyta' --output bold_plant_June2024.fasta --keep_original yes --boldgap DISCARD &`

