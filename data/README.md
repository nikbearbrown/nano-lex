# Seed data

[seeds.tsv](seeds.tsv) holds one row per term: a stable `nanolex:<NNNN>` identifier, the term, its `term_form` (abbreviated, nano-prefixed, multiword or single-word, worked out from the name alone) and any trivially different spellings that were merged into it. [source-manifest.json](source-manifest.json) records the source files and their hashes, the cleaning rules, the counts and the seed file's hash.

**Where the terms come from.** They are the entry headings of the initial NanoLex, a lexicon one language model wrote in 2024–2025. [build_seeds.py](build_seeds.py) reads the headings and nothing else, so the list carries no definition, classification or relation. It is a list of what that lexicon chose to define, not a survey of the field: some terms may be rare, misspelt or invented. Drafters do not drop those; they flag them.

**What was merged.** Only forms that differ in case, quotes, trade-mark signs or spacing (*Doxil®* into *Doxil*). Hyphen and spelling variants (*Nano-Ceria*, *Nanoceria*) and names with and without an abbreviation (*Quantum Dot*, *Quantum Dot (QDs)*) are separate seeds. Whether they are one concept is for each edition to decide and flag.

**Checking it.** `python3 replication/scripts/validate_seeds.py` checks the file against the manifest. A maintainer with the initial lexicon can add `--rebuild-from <its Data folder>` to confirm that the file rebuilds byte for byte.
