# Allen gene identifier audit

Generated: 2026-09-14T15:02:50.868392+00:00. Assembly: GRCm39.

Audited 4,083 volume names against 4,752 Allen experiments.
The one-to-one subset corrects 58 existing IDs and recovers 14 previously missing IDs.

| Status | Volume names |
| --- | ---: |
| ambiguous_ensembl | 7 |
| one_to_one | 3989 |
| shared_target | 18 |
| unresolved | 69 |

## Method and limits

Select P56, coronal, ISH, sleep_state=Nothing experiments from the source CSV for the 4,083 volume names in gene_data_counts.json.gz. Follow each experiment's Allen Gene record to its Entrez ID, follow NCBI replacement history, then join stable MGI identifiers and Ensembl cross-references. No symbol or synonym search is used.

Each accepted candidate must be a live mouse Gene on GRCm39 in the Ensembl lookup snapshot, with an MGI accession matching the Allen-derived identity. Old IDs are candidates only and must pass the same check. Literal null values in source reports are never treated as identifiers.

one_to_one.json includes only names with exactly one accepted candidate that is not shared by any other input name. ensembl_to_allen_names.json retains all accepted candidates, including ambiguous and shared targets. audit.csv records experiment IDs, identifier history, candidates and rejections; ensembl_evidence.json preserves the lookup responses. Source URLs, snapshot hashes and times are in provenance.json.

This validates database gene identity, not probe specificity. Unresolved means these sources do not establish a mapping, not that the gene has no possible Ensembl annotation. Retired records without replacements, missing Entrez IDs, source disagreements and absent MGI links require further curation. Multiple matching models require probe/accession or sequence-level evidence. Distinct probes for a shared gene must retain their identities; do not invent new Ensembl IDs or automatically average volumes.

The volume loader requires every input to appear in the one-to-one subset and raises before loading if any do not. Consequently, the complete collection cannot yet be loaded as one volume per Ensembl gene. No volumes have been removed or merged.

## Shared identifiers

| Ensembl ID | Allen names |
| --- | --- |
| ENSMUSG00000015002 | D030063F01Rik, Efr3a |
| ENSMUSG00000021879 | 4921531P07Rik, Dnah12 |
| ENSMUSG00000022514 | 6430709H04Rik, Il1rap |
| ENSMUSG00000029673 | Auts2, LOC545810 |
| ENSMUSG00000038729 | Akap2, Palm2 |
| ENSMUSG00000039087 | LOC432748, Rreb1 |
| ENSMUSG00000047507 | Baiap3, LOC381076 |
| ENSMUSG00000049176 | Frmpd4, Gm196 |
| ENSMUSG00000055026 | B230362M20Rik, Gabrg3 |
| ENSMUSG00000058975 | C230009H10Rik, Kcnc1 |
| ENSMUSG00000089945 | Akap2, Palm2 |
| ENSMUSG00000090053 | Akap2, Palm2 |

## Multiple matching Ensembl models

| Allen name | Ensembl candidates |
| --- | --- |
| 1700086L19Rik | ENSMUSG00000071265, ENSMUSG00000121877 |
| Akap2 | ENSMUSG00000038729, ENSMUSG00000089945, ENSMUSG00000090053 |
| Erdr1 | ENSMUSG00000095562, ENSMUSG00000096768 |
| Kctd16 | ENSMUSG00000051401, ENSMUSG00000118202 |
| Nrg1 | ENSMUSG00000062991, ENSMUSG00000118541 |
| Palm2 | ENSMUSG00000038729, ENSMUSG00000089945, ENSMUSG00000090053 |
| Ptp4a1 | ENSMUSG00000026064, ENSMUSG00000117310 |

## Rebuild

```bash
python -m packaging_scripts.resolve_allen_gene_ids --cache-dir /path/to/cache
```

Use a new cache directory for a fresh snapshot. The first run downloads the global NCBI gene history (approximately 160 MB compressed), other identifier tables and API responses. No image volumes are downloaded.
