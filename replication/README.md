# Replication

One coding agent, one independent edition. Use the pinned [seed manifest](../data/source-manifest.json), the [instructions](instructions.md), and the two [prompt files](prompts/README.md). The entry shape, three source links, evidence pointers and independent drafting protocol follow the [Irreducibly Human Work Lexicon replication kit](https://github.com/nikbearbrown/irreducibly-human-work-lexicon/tree/0ba8e0c2c6a2cf5e8d7a7f9d7abd301fe0185d76/replication). The field `work_sense` keeps its original name for compatibility; here it states the sense in nanomedicine.

1. Verify the seed file with `python3 replication/scripts/validate_seeds.py`. Prepare one independently sourced bundle per seed in a private run directory.
2. Render messages with `python3 replication/scripts/render.py BUNDLES.jsonl PROMPTS.jsonl`.
3. Send the system and user messages separately for each seed in a fresh context. Save one object per seed, including flagged abstentions.
4. Check completeness with `python3 replication/scripts/check.py BUNDLES.jsonl DRAFTS.jsonl REPORT.jsonl`.
5. Hand in the run privately. The maintainer runs the blindness check (`leak_check.py`) on it. After all runs are frozen, a separate reviewer follows the [reconciliation instructions](../lexicon/README.md).

A maintainer may designate a separate shared-bundle or ungrounded control. Do not mix those results with independently sourced grounded runs.

## Agreement study

Once several independent editions are frozen, their agreement in meaning is measured per `concept_id` with the kit in [AGREEMENT-METHOD.md](AGREEMENT-METHOD.md), [judging/](judging/README.md) (start at [judging/START-HERE-AI-JUDGE.md](judging/START-HERE-AI-JUDGE.md)) and `scripts/agreement.py`. The initial lexicon then joins as one more edition, converted by `scripts/legacy_to_edition.py`. Drafts and run folders stay private; the kit reads them from private paths.
