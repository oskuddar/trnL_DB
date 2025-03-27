* Install: Follow the instruction --> https://github.com/RTRichar/MetaCurator
* Users can follow the tutorial: https://forum.qiime2.org/t/using-rescripts-extract-seq-segments-to-extract-reference-sequences-without-pcr-primer-pairs/23618](https://github.com/RTRichar/MetabarcodeDBsV2/blob/master/Workflow.md)
---
**Run MetaCurator.py script**
---

\
`conda activate metacurator_environment`
\
\
Run MetaCurator script for each trnL region, here is an example for running trnL CD region:
```
MetaCurator.py -i /director/input_fasta_file.fasta
               -r /director/reference_trnL_CD_seq.fasta
               -it /directory/input_taxonomy_file.csv
               -is 6,6,3,3,3
               -cs 1.0,0.98,0.95,0.9,0.85
               -t 12
               -e 0.005
               -ct True
               -tf True
               -of /directory/output_fasta_file.fasta
               -ot /directory/taxonomy_output_file.tax
```

.
