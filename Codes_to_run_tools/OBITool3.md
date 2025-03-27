* Install: pip install OBITools3 (https://pypi.org/project/OBITools3/)
* Users can follow wolf tutorial: https://git.metabarcoding.org/obitools/obitools3/-/wikis/Wolf-tutorial-with-the-OBITools3
---
**Import files into obidms, run ecoPCR module, export to FASTA file**
---

```conda activate obi3``` \
```source ~/obi3-env/bin/activate``` 

Import a fasta file: \
```obi import --fasta /directory/fasta_file.fasta /directory/fasta_file_trnL/my_refs``` \
Import the taxonomy file: \
```obi import --taxdump /directory/taxdump.tar.gz /directory/fasta_file_trnL/taxonomy/my_tax ``` \
\
_trnL_Primers:\
Name	Code	Sequence 5′–3′\
C (A49325)	CGAAATCGGTAGACGCTACG\
D (B49863)	GGGGATAGAGGGACTTGAAC\
G (A49425)	GGGCAATCCTGAGCCAA\
H (B49466)	CCATTGAGTCTCTGCACCTATC\
\
EcoPCR for trnL_CD:\
```obi ecopcr -e 3 -l 1 -L 5000 -F CGAAATCGGTAGACGCTACG -R GGGGATAGAGGGACTTGAAC --taxonomy /directory/fasta_file_trnL/taxonomy/my_tax /directory/fasta_file_trnL/my_refs /directory/fasta_file_trnL/trnL_CD```\
\
EcoPCR for trnL_CH:\
```obi ecopcr -e 3 -l 1 -L 5000 -F CGAAATCGGTAGACGCTACG -R CCATTGAGTCTCTGCACCTATC --taxonomy /directory/fasta_file_trnL/taxonomy/my_tax /directory/fasta_file_trnL/my_refs /directory/fasta_file_trnL/trnL_CH```\
\
EcoPCR for trnL_GH:\
```obi ecopcr -e 3 -l 1 -L 5000 -F GGGCAATCCTGAGCCAA -R CCATTGAGTCTCTGCACCTATC --taxonomy /directory/fasta_file_trnL/taxonomy/my_tax /directory/fasta_file_trnL/my_refs /directory/fasta_file_trnL/trnL_GH```\
\
Export:\
```obi export --fasta-output /directory/fasta_file_trnL/trnL_CD > /directory/trnL_CD.fasta```\
```obi export --fasta-output /directory/fasta_file_trnL/trnL_CH > /directory/trnL_CH.fasta```\
```obi export --fasta-output /directory/fasta_file_trnL/trnL_GH > /directory/trnL_GH.fasta```\
\
.



