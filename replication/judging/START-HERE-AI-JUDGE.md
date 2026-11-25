# Start here: one prompt for any AI judge

Paste the prompt below, **unchanged**, into a fresh session of any model: in an agent harness opened in a clone of `nikbearbrown/nano-lex`, or in a plain chat. The model works out its own provider, model name and exact version. A script then decides which items it may judge (self-exclusion from [drafters.tsv](drafters.tsv)) and builds its packets. Paste the same prompt again in a new session for each later batch: the model resumes where it left off.

## The prompt (for every model)

```
You are an AI judge in a study of how far independent, model-written dictionary entries for nanomedicine
agree in meaning. Do not use the web. The dictionary is descriptive only: judge
meaning, never give preparation protocols, doses or clinical advice, never judge whether a product works or
is safe, and never write or ask for details of a person's health. Never open a copy of the initial NanoLex.

1. Identify yourself from your harness or system information, not from memory: your provider (the company),
   your model name (without provider or version), your exact version, and the model string exactly as shown.
   If you cannot see an exact version, say so plainly; you will use --version-unknown. Never guess a version.

2. If you cannot run shell commands in this repository, reply only with:
   NO SHELL
   provider: ...
   model name: ...
   version: ... (or: unknown)
   model string: ...
   and wait. The operator will paste your items.

3. Otherwise, in this repository, read replication/judging/AI-JUDGE-INSTRUCTIONS.md and follow it exactly with
   RUN_DIR=replication/agreement/pilot-test, starting from origin/main: compute your judge id,
   switch to the branch judging/<your judge id>, and run the join command (it decides which items you get and
   resumes if you already joined). Judge only the next batch it names, write your results, run the validator
   until it passes, commit only your own results/ and packets/ folders, and push your judging/<judge id> branch.
   Open only your own packets/ and results/ folders.

4. When done, report your judge id, provider, model name and version, any flags join printed, the batch
   number, your label counts, and anything in the instructions that was unclear.
```

## Chat-only models (no shell)

If the model replied `NO SHELL`, the operator runs the commands from a clone of the repository, on the branch `judging/<judge id>`:

1. **Join for it**, using what the model stated:
   `python3 replication/scripts/agreement.py join replication/agreement/pilot-test --provider P --model-name M --version V --model-reported "<its model string>" --harness chat`
   (`--version-unknown` instead of `--version V` if it couldn't see its version). Note the judge id it prints.
2. **Export one paste block:**
   `python3 replication/scripts/agreement.py export-packet replication/agreement/pilot-test --judge-id <judge id> --write packet.txt`
3. **Paste** all of `packet.txt` into the same chat. The model replies with one `jsonl` block, one line per item.
4. **Import:** save the whole reply as `reply.txt` and run
   `python3 replication/scripts/agreement.py import replication/agreement/pilot-test --judge-id <judge id> --reply reply.txt`.
   It validates the reply and stores it as `results/<judge id>/batch-NNNN.jsonl`. If anything is missing or invalid, it stores nothing and says what to fix.
5. **Commit and push** `results/<judge id>/` and `packets/<judge id>/` to `judging/<judge id>` (AI-JUDGE-INSTRUCTIONS.md, section 7). For the next batch, repeat steps 2 to 5.

## What each judge gets

No run folder is built yet. When Bear freezes the editions, the operator builds `replication/agreement/pilot-test` with `agreement.py run` (drafts are read from private paths; nothing that names an edition is committed). Each judge then gets the stage-P2 definition pairs for seeds where **both** editions wrote an entry, in batches of 50, minus self-exclusion:

| Judge | Items |
|---|---|
| any model that drafted no edition (it may still be flagged `same_family_as_drafter`) | every pair |
| a model that drafted an edition (a row in drafters.tsv) | only pairs that do not involve its own edition |
| a model whose version is unknown but whose provider and model match a drafter | the drafter's share, **flagged** |

Seeds that one or both editions flagged as out of scope or duplicate are not sent to judges; `run` reports scope agreement for them deterministically, alongside variant (alias/synonym) and relation agreement per `concept_id`.

## For the operator

- To add a new drafter, add a row to [drafters.tsv](drafters.tsv) **before** that model joins. The edition name in the row must match the name used in `agreement.py run --edition NAME=gen-v2:PATH`.
- Build the run with, for example, `python3 replication/scripts/agreement.py run replication/agreement/pilot-test --private-dir <private>/pilot-test --edition <name>=gen-v2:<private>/<name>/drafts.jsonl --edition <other>=gen-v2:<private>/<other>/drafts.jsonl --edition legacy=nanolex-legacy:<private>/legacy/legacy-edition.jsonl`. Only `requests/`, `packets/`, `results/` and `humans/` go in the repository; `canonical/`, `keys/`, `tables/` and `coverage.csv` stay in the private directory.
- Flags printed by `join` are kept in `results/<judge id>/judge.json`. `stats` reports `version_unknown` judges separately.
- The key that unblinds A and B is **not** in this repository. Scoring needs it: `agreement.py stats replication/agreement/pilot-test --keys <private>/pilot-test/keys/anon.jsonl`.
- `requests/exclusions.json` lists, for each edition under an obfuscated token, which requests involve it, so that `join` can exclude drafters without the key. It is obfuscation, not secrecy: a judge that read it together with `drafters.tsv` and the script could learn which items involve which edition. Judges are told not to open it.
- Each judge pushes its own `judging/<judge id>` branch and touches only its own folders, so branches never conflict.
