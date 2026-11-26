# NanoLex — Grok Bot independent edition: run record

## Deviation 1 (stated first): batching
Seeds were drafted in batches of 15 (66 batches; the last batch holds 2 seeds), in order 0001–0977, all within one continuing agent session. **No entry was drafted in a fresh context**: earlier batches stayed in the session's working context. Every draft records this in `_meta.run_mode`.

## Identity and dates
- Model: "Grok Bot". Version: "unknown". The drafting agent could not see a version, so none was guessed.
- Settings: sampling settings such as temperature were not exposed to the agent and are not recorded. One agent drafted everything, with tools on and batch size 15. Each failed record got at most one retry with its check errors, per instructions.md.
- Date: 2026-11-25. Gathering started about 06:28 UTC (01:28 ET); the last batch was committed at 09:07 UTC (04:07 ET). ET means America/New_York (UTC−5).
- Repository: the clone at `bd0bd4cf740aa441a6c075948bd4b8953f422aef`, read-only. Nothing was committed, pushed or branched.
- Seed file: `data/seeds.tsv`, 977 seeds, sha256 `def0820e9baf4934cfbf9484c3061c5548785dc2f2821942c6b38fbc45386a38`.
- Repository files read: AGENTS.md, replication/README.md, replication/instructions.md (it wins on conflicts), replication/prompts/system.txt, replication/prompts/user-template.txt, data/README.md and data/seeds.tsv. The agent also ran replication/scripts/check.py and render.py without opening them for content beyond use.

## Files
- `bundles.jsonl`: one evidence bundle per seed. It holds pinned Wikipedia revisions, Wikidata items, WordNet synsets, examples with exact URLs, neighbors and query logs.
- `drafts.jsonl`: one draft per seed, each with `_meta`.
- `report.jsonl`: check.py output.
- `RUN.md`: this file.
- Working material is in `work/`: per-batch DSL sources, retry files, `first_failures.jsonl`, notes and the rendered `work/prompts.jsonl`. It is kept for audit and is not part of the four-file handoff.

## Tools and queries
- English Wikipedia API:
  - title lookup of the seed name and a cleaned form (without brackets);
  - then `list=search` (srlimit 5);
  - up to 3 candidates kept, with the exact revision id pinned;
  - the intro extract is stored.
- Wikidata `wbsearchentities` (en, limit 8): publications and clinical-trial items were excluded, and item revision, label, description, aliases, P31 and P279 were recorded.
- WordNet (NLTK) noun and adjective lemma lookup.
- When the evidence above was thin:
  - NCIt (EVS API, match search);
  - MeSH (descriptor exact lookup plus SPARQL scope note);
  - PubChem (compound name, for drug and compound seeds);
  - Europe PMC REST `search` for the quoted name (pageSize 10).
- Europe PMC follow-ups:
  - `autofollow.py`: an automatic follow-up over all records for the quoted name, adding up to 2 sentences that contain the phrase, from different articles.
  - `epq.py`: manual searches during bundle prep.
  - Every query and its hit count is logged in each bundle's `log`.
- Local validation:
  - a lint script (allowed relation types, quotes found in the linked revision, 9-word reuse, pointer form);
  - then `replication/scripts/check.py` after every batch, on the cumulative files.

## Interruptions (all three)
1. **Interruption 1, after batch 16 (seed 0240).** The session was cut off after batch 16 was committed, at about 07:09 UTC (02:09 ET). It resumed from seed 0241 using `work/progress.json`, the source of truth, with batch 17 at about 07:14 UTC (02:14 ET).
2. **Interruption 2, at batch 33 (495/977 drafted, all passing).**
   - The box was replaced in the middle of the run, with uptime reset at about 07:54 UTC (02:54 ET), and `/workspace` came back at an older state (batch 30).
   - At 08:00 UTC (03:00 ET) the run folder was restored from the store backup, which held batch 33 with 495/495 passing.
   - The stale copy is kept at `/workspace/nanolex-run-grok.stale-restore`, and background evidence prep for batches 34–45 was restarted.
   - Drafting resumed from seed 0496.
3. **Interruption 3, after batch 55 (825/977 drafted, all passing).** Recorded at 08:53 UTC (03:53 ET). It resumed from seed 0826 using `progress.json`.

Each time, the run resumed with the same batch size and rules, and with strict blindness.

## Other deviations and incidents
- **Lint extended twice.**
  - After batch 32, lint gained the quote-in-linked-revision and alias checks.
  - After batch 34's first attempt (08:05 UTC / 03:05 ET), it gained the allowed relation types.
  - check.py's 20-word quote limit was never added to lint; that gap caused failure 0913.
- **Europe PMC outages.**
  - The service returned HTTP 503 and timeouts for several minutes around batch 52, from 08:44 UTC (03:44 ET), and was intermittent later.
  - Prep for the affected batches was re-run after it recovered.
  - Prep queries still failed for 0792, 0845 and 0905. 0792 got a manual example; 0845 and 0905 carry notes.
  - 0790 was made unattested while searches were flaky, so the term may exist. 0835, 0837 and 0839 carry outage-affected evidence or notes.
- **Manual examples.** Some examples were added with a manual Europe PMC query (logged in the bundle), for example:
  - 0773, 0776, 0777, 0778, 0779, 0792, 0820, 0877, 0878, 0879 and 0923;
  - 0967 (MED39648920).
- **Copied examples.** Some examples were copied from another seed's bundle into this seed's bundle, with source URLs kept:
  - 0687 (mesh:D045333, from 0689);
  - 0376, 0420 and 0479.
- **Canonical-form deviations for duplicates.**
  - 0772 and 0781 → 0720 PAMAM. The closed-form rule would pick 0781, but 0720 had already been committed as an entry in batch 48.
  - 0788 → 0261. The inverted form had already been drafted as the entry, so the natural-order form became the duplicate.
- **Batch 57 re-expanded before moving on.** This was not a check failure. It corrected 0855 relations that had a null target although the target was in fact a neighbor.
- **Known issues** (passed check.py and left as written):
  - 0181 reuses 9 words from an example.
  - 0015 has a null hypernym target, although seed 0748 exists, because 0748 was not among the bundle's neighbors.
- **Non-nano biomedical terms** (drugs, conditions and the like) were kept as entries with a note, following the 0074 precedent, for example 0757, 0819, 0829, 0840, 0847, 0848, 0885, 0918, 0926, 0934, 0950 and 0971. Gene products and taxa were marked out of scope.

## Checking
- **First attempts.** 20 records failed check.py on their first attempt. Each was retried once with its errors, from `dsl/batch_NN_retry.py`, and all 20 passed on retry (`_meta.attempt_count` = 2). They are listed in `work/first_failures.jsonl`:
  - 0013, 0027, 0038, 0055, 0123, 0129, 0130, 0134, 0170, 0206, 0233, 0470, 0497, 0498, 0500, 0503, 0504, 0505, 0509, 0913.
- **Final full run.** `python3 replication/scripts/check.py bundles.jsonl drafts.jsonl report.jsonl` printed `977/977 seeds passed` (exit 0).
- No records were hand-edited. Every draft was generated from the batch sources.

## Coverage totals
| | count |
|---|---|
| seeds | 977 |
| records written | 977 |
| entries (defined) | 805 |
| out-of-scope (excluding duplicates and unattested) | 13 |
| duplicate | 114 |
| unattested | 45 |
| ambiguous flag (among entries) | 57 |
| note flag | 135 |
| still failing | 0 |

805 + 13 + 114 + 45 = 977.

## Least-sure seeds (top 10)
1. 0790: unattested while Europe PMC was failing; the term may exist.
2. 0766 PLGA-TPG: unattested; it may be a truncation of PLGA-TPGS, which was not assumed.
3. 0962 USPIO → 0963: duplicate call for the hyphenated, abbreviated form.
4. 0772/0781 → 0720 PAMAM: the canonical choice deviates from the closed-form rule.
5. 0788 → 0261: the duplicate direction is reversed.
6. 0839: the definition rests on model knowledge only (thin evidence, outage).
7. 0527 Nanodosing: unattested despite 8 full-text hits.
8. 0660 Nanostim: out of scope as a brand, inconsistent with NanoDrop and NanoLuc, which were kept.
9. 0636 Nanoporou: the truncated seed was read as "nanoporous".
10. 0714 NVX-CoV2373 Adjuvated Lipid Nanoparticle: the seed's wording conflicts with the sources' protein-nanoparticle description.

## Blindness
- No earlier NanoLex, no file named NanoLex*.md and no nano-lex-initial-2025 repository was searched for, opened or met.
- agreement.py, AGREEMENT-METHOD.md, replication/judging/ and other runs, drafts, votes or branches were not opened.
- No other model or agent drafted, checked or judged entries.
- Source text was treated as data only.

Residual risks:
- Wikipedia, Wikidata and Europe PMC pages may themselves reflect earlier NanoLex-derived content.
- The agent's background knowledge cannot be audited.
- The stale-restore folder is an earlier copy of this same run, not another run.
