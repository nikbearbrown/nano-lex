# NanoLex

**A lexicon of nanomedicine terms, being rebuilt from independent, checked editions.**

[Working abstract](#abstract) · [How to contribute](CONTRIBUTING.md) · [Seed terms](data/README.md) · [Draft an edition](replication/README.md) · [Judge agreement](replication/judging/README.md) · [Reviewed lexicon](lexicon/README.md)

NanoLex covers the vocabulary of nanomedicine: nanomaterials and carriers, formulations and named products, techniques, and the biological targets they act on. A Humanitarians AI terminology project.

**We're inviting collaborators.** Review the method, judge agreement, review entries in your field, or take on one of the tasks listed below. You don't need to review the whole project to help. To join, follow [Getting started](CONTRIBUTING.md#getting-started) in the contributor guide.

> **Drafting or judging?** Follow [AGENTS.md](AGENTS.md) and the kit it points to, and nothing else in this README. Never open the initial lexicon, another model's run or the reviewed edition while you draft.

Led by Nik Bear Brown. NanoLex is one of [Humanitarians AI's papers in progress](https://github.com/nikbearbrown/hai-research).

## Abstract

*Working abstract. No manuscript exists yet, so this describes what the paper sets out to do. It reports no results.*

The first NanoLex, about a thousand nanomedicine entries, was written by one language model in 2024 and 2025, and no claim in it was ever checked: no author, model, prompt or source was recorded for any of them. This project rebuilds it so that each claim can be audited. The 977 terms the first lexicon defined become a seed list of names only. Several language models each draft an independent edition of every term from public sources they cite, without seeing the first lexicon or one another. Automated checks reject an edition that misses a term, breaks the entry shape, cites evidence it did not link or copies the first lexicon's wording. The editions, and then the first lexicon as one more edition, are compared term by term for meaning, by model judges that drafted none of the compared entries, with human judges checking the model judges. A reviewer checks the cited source for every claim that enters the reviewed lexicon. The paper will report how far independent editions agree with one another and with the unchecked original, and what review finds. NanoLex describes terms; it is not medical advice.

## Where the draft is

Rough draft, not reviewed: the [paper series](paper/README.md), modelled on the WordNet papers, with the [human evaluation to-do](paper/HUMAN-EVALUATION-TODO.md). One independent Grok Bot edition is checked (977/977 pass: 805 entries, 114 duplicates, 45 unattested); a second edition, the comparison with the initial lexicon, cross-model judging and human evaluation have not been run.

## What needs to be done

- **Draft independent editions** with several model families, following the [replication kit](replication/README.md). None exists yet.
- **Run the checks** on each edition: `check.py` for evidence and `leak_check.py` for copying.
- **Run the agreement study**, with model judges and human judges, once the editions are frozen.
- **Review entries** against their cited sources, with people who know nanomedicine, to build the reviewed edition.
- **Place the work** against existing nanomedicine vocabularies and ontologies, such as eNanoMapper and the NanoParticle Ontology.
- **Write the paper:** the method, the agreement results, how the unchecked original compares, and what review found.
- **Recommend a journal** Northeastern covers in full (see the [contributor guide](CONTRIBUTING.md#recommend-a-journal-northeastern-covers-in-full)).

## How to contribute

Read [CONTRIBUTING.md](CONTRIBUTING.md). In short: read this README, pick one task, and email Nik at bear@bearbrown.co with the subject "NanoLex: contributor" to be added to the repository. Anyone can [open an issue](https://github.com/nikbearbrown/nano-lex/issues/new) without emailing first.

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
