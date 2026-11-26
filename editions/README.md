# Parallel editions

Independent, machine-drafted editions of this lexicon, kept here as parallel evaluations so they can be compared side by side. Each subfolder is one model's edition.

- **Unreviewed.** Every record is a machine draft. None has been checked by a person, and none is part of the reviewed lexicon in [`lexicon/`](../lexicon/README.md).
- **Not for drafters.** If you are drafting an independent edition with the [replication kit](../replication/README.md), do not open this folder until your edition is frozen. The kit's blindness rule covers every edition here.
- **Unedited copies.** The files inside an edition folder are copied unchanged from that model's private run folder. Nothing was hand-edited after the edition's final `check.py` run. Paths inside `RUN.md` and the tools refer to the drafter's own machine.
- Wikipedia text in the bundles is CC BY-SA 4.0, with the exact revision id pinned per record; Wikidata is CC0; WordNet 3.0 is under the WordNet licence.
- Example sentences in the bundles are short excerpts from Europe PMC open-access articles and public PubChem, MeSH and NCIt records, each with its source URL. Licences of individual Europe PMC articles vary.

## Editions

| Folder | Model as recorded | Run mode | Date | Seed commit | `data/seeds.tsv` sha256 | Records | `check.py` |
|---|---|---|---|---|---|---|---|
| [`grok-bot/`](grok-bot/) | Grok Bot (exact version: unknown, not exposed to the drafter) | Batched: 66 batches of 15 seeds (the last holds 2) in one session, not a fresh context per seed. Disclosed in `RUN.md` and every `_meta.run_mode`. | 2026-11-25 (EST) | `bd0bd4cf740aa441a6c075948bd4b8953f422aef` | `def0820e9baf4934cfbf9484c3061c5548785dc2f2821942c6b38fbc45386a38` | 977 / 977 seeds | 977/977 pass, 0 fail (20 records passed on their single retry) |

## `grok-bot/`: files

| File | What it is |
|---|---|
| `RUN.md` | Model, seed commit and hash, sources, method, deviations, check result |
| `drafts.jsonl` | One draft per seed, each with `_meta` |
| `report.jsonl` | `check.py` output per seed |
| `bundles.jsonl` | Evidence bundle per seed: pinned Wikipedia revisions, Wikidata, WordNet 3.0, neighbors, and short example sentences with exact URLs (Europe PMC, PubChem, MeSH, NCIt) |

## Left out of `grok-bot/`, and why

- `work/` (per-batch drafting sources, retry files, `first_failures.jsonl`, notes, rendered prompt packets). This repository's `.gitignore` excludes `work/`; it stays in the private run folder.
- `leak_check.py` (the copy check against the initial lexicon) has not been run on this edition here; the initial lexicon is kept in a separate private archive.
- No rendered entries file exists for this edition.
- No keys, secrets or judging anonymisation files are included.

More editions from other models can be added as sibling folders, for example `editions/<model>/`, with a row in the table above.
