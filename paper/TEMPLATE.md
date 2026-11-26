# Template for the lexicon paper series

*Rough draft, not reviewed.* One template, five lexicons. Every series uses these headings in this order and changes only the lexicon-specific content. The model is the WordNet series (Miller, Beckwith, Fellbaum, Gross and Miller, *Five Papers on WordNet*, 1990, revised 1993): an introduction that motivates the design and names the relations; one paper per part of the vocabulary, each organised by that part's own relations; a design and implementation paper; and appendices on file formats. Two things are added. Part III documents an AI build rather than a lexicographers' build, and Part IV is an evaluation that has **not** been run, written as a to-do centred on what people must do after the AI comparison of the independent editions.

Common machinery (seed manifests, bundles, the drafting prompt, checking, provenance, parallel editions, the agreement method, the human-in-the-loop rule) is documented once in the shared methods paper, [Building WordNet-style lexica with AI: process and provenance](building-wordnet-style-lexica-with-ai.md). Each series cites it and keeps only what differs.

| Template heading | WordNet counterpart | What goes here |
|---|---|---|
| Title block | the series title page | exact title; the line *Rough draft, not reviewed*; a one-line **Where it stands** |
| **Part I. Introduction** | "Introduction to WordNet" | |
| I.1 What the lexicon is for | Psycholexicology | the problem the lexicon solves and who uses it |
| I.2 Why a WordNet-style relational lexicon | Psycholexicology; Lexical Matrix | why relations, not an alphabetical list or a flat glossary |
| I.3 The lexical matrix, adapted | The Lexical Matrix | word forms × meanings: here, seed names and variants × concepts (work senses); how polysemy and synonymy show up |
| I.4 The relations | Synonymy, Antonymy, Hyponymy, Meronymy, Morphological Relations | the nine relation types and their tests; which ones carry this lexicon; what replaces antonymy |
| I.5 Built with AI: what changes and what does not | (none) | models draft, people decide; what is the same as WordNet and what is not |
| **Part II. The vocabulary by category** | "Nouns", "Adjectives", "Verbs" | |
| II.1 … II.n, one per category | one paper per part of speech | for each category: what belongs, its organising relations, worked examples from the edition, hard cases and what falls outside |
| **Part III. Design and implementation** | "Design and Implementation of the WordNet Lexical Database" | |
| III.1 Seed list and manifest | lexicographers' source files | where the seeds came from, count, hash, commit |
| III.2 Evidence bundles | (none; WordNet lexicographers used their own knowledge) | which sources, how pinned |
| III.3 Drafting prompt and kit | the source-file syntax | prompt version and hash, domain rule |
| III.4 Flags | (none) | the flags this lexicon uses and what they mean |
| III.5 Checking | the grinder | `check.py`, one retry, no hand edits |
| III.6 Provenance | the archive system | RUN.md and `_meta` |
| III.7 The Grok Bot edition: what was done and how it deviated | (none) | dates, totals, deviations, interruptions |
| III.8 Parallel editions and agreement | (none) | other models' blind editions and the agreement method |
| III.9 Human in the loop | the lexicographers | what only people decide |
| **Part IV. Evaluation (to do): what humans do after the AI comparison** | (none; WordNet's papers did not evaluate) | |
| IV.1 Status | | what has and has not been run |
| IV.2 Prerequisites on the AI side | | what must exist before people start |
| IV.3 Human steps in order | | the shared ordered steps H1 to H14, with gates, owners and status |
| IV.4 What humans review in this lexicon | | the lexicon's own review queues, with counts from the Grok edition, and its domain-safety rule |
| IV.5 Held-out task and coverage evaluations | | the downstream task and the reference vocabularies to compare with |
| IV.6 Open decisions | | decisions already pending for this lexicon |
| IV.7 Resources, owners and status | | raters, item counts, hours, tools |
| **Part V. Limitations** | Future Work | what the draft cannot claim |
| Appendix A. File formats | Appendix A, Lexicographers' Files | seeds, bundle, draft, report |
| Appendix B. Flags | Appendix B, Verb Sentence Frames (the closed list) | the flag prefixes |
| Appendix C. Scripts | Appendix C, Library Functions | each script and who runs it |
| References | References | real references only; uncertain ones marked [verify] |

**Rules for every series.** Use only numbers that are in the repositories, the run folders (RUN.md, totals, counts from `report.jsonl`) or the method documents. Write `[TODO: …]` for anything unknown. Follow the lexicon's domain rule in the paper itself. Name the Grok runs only as "Grok Bot", as recorded.
