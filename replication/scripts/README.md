# Replication scripts

None of these calls a model. A passing report does not establish that an entry is scientifically correct.

| Script | Who runs it | What it checks or does |
|---|---|---|
| `validate_seeds.py` | anyone | the seed file matches the manifest: hash, count, ids in sequence, no repeated or malformed names |
| `render.py` | drafter | renders one isolated system and user message per bundle |
| `check.py` | drafter, then maintainer | every seed has a bundle and a draft, the entry shape is right, and every pointer resolves (it calls `verify_drafts.py`, the evidence checks from the upstream MIT-licensed kit) |
| `leak_check.py` | maintainer | no draft definition shares a run of eight or more words with the initial lexicon |
| `legacy_to_edition.py` | maintainer | converts the initial lexicon into an edition, written to a private path, after the independent editions are frozen |
| `agreement.py` | maintainer and judges | normalises editions, compares scope, variants and relations deterministically, writes blinded judge requests, validates judgments and computes the statistics |

`build_seeds.py`, which made the seed list, is in [../../data](../../data/README.md).
