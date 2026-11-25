# NanoLex

**A lexicon of nanomedicine terms, being rebuilt from independent, checked editions.**

[Seed terms](data/README.md) · [Draft an edition](replication/README.md) · [Judge agreement](replication/judging/README.md) · [Reviewed lexicon](lexicon/README.md)

NanoLex covers the vocabulary of nanomedicine: nanomaterials and carriers, formulations and named products, techniques, and the biological targets they act on. A Humanitarians AI terminology project.

## State

- **The initial lexicon is not in this repository.** One language model wrote it in 2024–2025, and nobody checked it. It is kept in a separate private archive, and this repository's history does not contain it.
- **The seed list is ready.** [data/seeds.tsv](data/seeds.tsv) holds the 977 terms the initial lexicon defined, as names only. No definition, classification or relation was copied.
- **No independent edition exists yet**, and no reviewed entry.

## How the lexicon gets checked

Four checks, each independent of the others:

1. **Independent editions.** Several language models each draft all 977 terms from the seed list, alone, from public sources they can cite. None sees the initial lexicon or another edition. See [replication/README.md](replication/README.md).
2. **Evidence check.** `check.py` rejects an edition that misses a seed, breaks the entry shape, cites a source it did not link, or quotes text that is not in its evidence bundle.
3. **Blindness check.** `leak_check.py` compares each edition's wording with the initial lexicon, so that an edition that copied it is caught before it counts.
4. **Agreement study.** The editions, and then the initial lexicon as one more edition, are compared term by term for meaning. Model judges that drafted none of the compared entries do the judging, and human judges check the model judges. See [replication/AGREEMENT-METHOD.md](replication/AGREEMENT-METHOD.md).

Agreement is not proof. A reviewer still checks the cited source for every claim that goes into the reviewed lexicon ([lexicon/README.md](lexicon/README.md)).

## Where to go

| You want to | Go to |
|---|---|
| See the terms and where they came from | [data/README.md](data/README.md) |
| Draft an independent edition (a coding agent) | [AGENTS.md](AGENTS.md), then [replication/instructions.md](replication/instructions.md) |
| Judge agreement, as a person or a model | [replication/judging/README.md](replication/judging/README.md) |
| Run the validators | [replication/scripts/README.md](replication/scripts/README.md) |

## Rules

- Drafters and judges are never given the initial lexicon, and do not open a copy if they find one.
- Drafts, evidence bundles, judging keys and the initial lexicon's text are never committed to `main`.
- NanoLex describes terms. It is not medical advice, and it makes no claim that a product works or is safe.

## Licence

MIT, see [LICENSE](LICENSE). Copyright Nik Bear Brown.
