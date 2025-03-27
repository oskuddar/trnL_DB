* Install: Follow the instruction --> https://github.com/nbokulich/RESCRIPt
* Users can follow wolf tutorial: https://forum.qiime2.org/t/using-rescripts-extract-seq-segments-to-extract-reference-sequences-without-pcr-primer-pairs/23618
---
**Import files as QIIME2 Artifacts, run extract-seq-segments command, export to FASTA file**
---

\
`conda activate qiime2_environment`

Import fasta file as QIIME2 Artifact:

```
qiime tools import
      --type 'FeatureData[Sequence]
      --input-path /directory/fasta_file.fasta
      --output-path /directory/fasta_file.qza
```
Import reference sequence file as QIIME2 Artifact:

```
qiime tools import
      --type 'FeatureData[Sequence]
      --input-path /directory/reference_seq_file.fasta
      --output-path /directory/reference_seq_file.qza
```

Import taxonomy file as QIIME2 Artifact:
```
qiime tools import
  --type 'FeatureData[Taxonomy]'
  --input-format TSVTaxonomyFormat
  --input-path /directory/taxonomy_file.tsv
  --output-path /directory/taxonomy_file.qza
```

Extract the segments:

```
qiime rescript extract-seq-segments
  --i-input-sequences /directory/fasta_file.qza
  --i-reference-segment-sequences /directory/reference_seq_file.qza
  --p-perc-identity 0.8
  --p-min-seq-len ${min_length}
  --p-threads 12 \
  --o-extracted-sequence-segments /directory/fasta_reference_seq_extracted.qza
  --o-unmatched-sequences /directory/fasta_reference_seq_unmatch.qza
  --verbose
```
Export the extracted sequences:
```
qiime tools export \
  --input-path /directory/fasta_reference_seq_extracted.qza
  --output-path /directory/fasta_reference_seq_extracted
```
.
