# Building WordNet-style lexica with AI: process and provenance

*Rough draft, not reviewed.* Nik Bear Brown and Humanitarians AI [TODO: confirm authorship and acknowledgments]. Drafted 2026-11-26 with Grok Bot.

**Where it stands:** the pipeline described here has produced one checked Grok Bot edition for each of five lexicons. A second independent edition exists only for the Irreducibly Human Work Lexicon. Cross-model judging has started only there, as a pilot. No human evaluation has been run and no entry has been reviewed.

## 1. Why WordNet is the model

WordNet began, in Miller's words, as "a proposal for a more effective combination of traditional lexicographic information and modern high-speed computation" (Miller et al. 1990/1993). Its core claim was that a lexicon is better organised by meaning than by spelling: word forms map to synonym sets, and synonym sets are linked by a small number of relations whose tests can be stated plainly (hyponymy, meronymy, antonymy, entailment). The *Five Papers on WordNet* then did something less common: they explained, part of speech by part of speech, why each relation fitted or failed, and then described the files and programs that turned lexicographers' judgments into a database.

The five lexicons documented here follow the same plan and the same order of exposition. They differ in two ways. First, they are domain vocabularies rather than a general lexicon: work concepts (skills, knowledge, abilities, languages, credentials), clinical treatments and procedures, drugs and drug use, diseases and their signs and symptoms, and nanomedicine. Second, the first drafts are written by language models, not by lexicographers. Miller's team wrote source files by hand and used a program, the grinder, to check them and build the database. Here a model writes a draft for every seed, a checker rejects drafts that break the format or cite what they did not read, and several models draft the same seeds blind so that their agreement can be measured. People still decide what goes into the lexicon. This paper documents that pipeline once, so that each lexicon's own Design and Implementation paper can be short.

## 2. The lexical matrix, adapted

Miller's lexical matrix put word forms in columns and word meanings in rows. An entry in a cell meant that form could express that meaning; two entries in one row were synonyms, two in one column made the form polysemous. The lexicons here keep the matrix but change both axes.

- **Rows are concepts**, each fixed by a stable seed ID (`enwiki:<page id>`, `nanolex:<NNNN>`, or the work lexicon's own IDs) and, in each draft, by a one-sentence `work_sense`. The work sense plays the role of the synset's gloss: every later decision in the draft is about that sense and no other.
- **Columns are surface forms**: the seed's preferred name plus its variants. A variant can carry a **condition**, the circumstance under which the form names the concept ("PG" names PostgreSQL only in a database context; "kush" names a West African synthetic drug only in that regional sense). Conditions are the adaptation that matters most. WordNet could leave polysemy to the reader; a matching system cannot.
- **Polysemy** appears as seeds whose page names more than one thing (a specialty and its treatment; a brand and a substance), which drafters flag as `ambiguous` rather than resolve silently.

## 3. Relations

All five lexicons share one closed set of nine relation types, each with a test the drafter must pass with the real names filled in:

| Relation | Test the drafter must pass with the real names filled in | WordNet analogue |
|---|---|---|
| synonym | the target can replace the concept in a source excerpt without changing the concept | membership in one synset |
| hypernym | "[concept] is a kind of [target]" is true | hypernymy (@) |
| hyponym | "[target] is a kind of [concept]" is true | hyponymy (~) |
| meronym | the concept includes the target as a component by definition | part meronymy (%p) |
| holonym | the concept is a component of the target by definition | part holonymy (#p) |
| uses | the concept is characteristically associated with the target tool, material or substance | none (new) |
| requires | an explicit conceptual prerequisite supported by a source | none; compare verb entailment |
| certifies | the concept is a credential and attests to the target | none (new) |
| contrast | the target is often confused with the concept but differs from it, including look-alike names | none; replaces antonymy |

Antonyms and pertainyms are not recorded. Every relation also carries a `basis` (`source`, with pointers, or `model_knowledge`, with none) and a target that is either a seed ID or marked `proposed_new`.

Two departures from WordNet are deliberate. Antonymy, central to WordNet's adjectives, is dropped: domain vocabularies have few true opposites, and the lexicon's practical danger is not opposition but confusion. Its place is taken by **contrast**, which records names that are often taken for each other but differ (Java and JavaScript; physical dependence and addiction; Raynaud's phenomenon and acrocyanosis). And two relations are added that WordNet's nouns did not need: **uses**, for the characteristic tool, material or substance, and **certifies**, for credentials (used only in the work lexicon). **Requires** is the nearest analogue of verb entailment, restricted to prerequisites a source states. The prompt tells the drafter that "an empty relation list is a correct answer. A plausible relation you cannot support is an error."

## 4. The pipeline

### 4.1 Seeds and manifests

Every lexicon starts from a versioned seed file, `data/seeds.tsv`, whose SHA-256 hash is recorded in `data/source-manifest.json`. The seed list is the work queue: one record per seed, even for pages that are biographies, lists or redirects. No title filter is applied and no seed is silently dropped. Out-of-scope seeds get a flagged abstention, not an invented definition.

| Lexicon | Seeds | Where the seeds came from | Seed hash (first 8) |
|---|---:|---|---|
| Irreducibly Human Work | 3,754 concepts at `91312fec`; the Grok full run covers 3,718 and the pilot 36 | the lexicon's own concepts (legacy tags, O\*NET imports, model drafts) | [TODO: no manifest hash; the parallel-edition prompt uses 369d34c9 over the four batch files] |
| Clinical Treatments and Procedures | 354 | direct article members of Category:Medical treatments, Therapy, Medical procedures | 5ee21679 |
| Drugs and Recreational Drug Use | 352 | direct members of Drugs, Psychoactive drugs, Drug culture, Substance abuse, Substance-related disorders | caa4f3ae |
| Disease, Syndromes and Symptoms | 1,079 | direct members of Diseases and disorders, Infectious diseases, Symptoms, Syndromes, Medical signs and related roots | 41f6251d |
| NanoLex | 977 | the entry headings of the initial NanoLex (a model-written lexicon of 2024–2025), names only | def0820e |

For the Wikipedia-based lexicons, category membership supplies candidates, not authority. The manifests record which root categories were found, empty or missing (for example `Category:Recreational drugs` and `Category:Infectious disease` were missing when the seeds were pulled on 2026-11-24).

### 4.2 Evidence bundles

For each seed the drafter builds one **evidence bundle** with seven fields (Appendix A of each series): the concept record, candidate relation targets drawn only from the seed list (`neighbors`), optional public usage examples, up to three Wikipedia pages with the **exact revision pinned**, candidate Wikidata items with their revision and ancestors, and WordNet senses. NanoLex seeds come with no page, so its drafters also search MeSH, the NCI Thesaurus, ISO or IUPAC definitions and open-access papers (Europe PMC), keeping the exact URL and a short excerpt. Pinning matters: a judge or reviewer must be able to see the text the drafter saw, not today's version of the page. Patient records, private documents and identifiable social posts are never used.

The work lexicon is the exception. Its Grok full run used **no-source bundles** (every claim `model_knowledge`), because grounded bundles for 3,718 concepts were beyond what one drafter could read in the run; its 36-concept pilot was drafted both grounded and ungrounded.

### 4.3 The drafting prompt

Each repository ships two prompt files, `replication/prompts/system.txt` and `user-template.txt` (prompt version gen-v2, adapted from the work lexicon's kit). The system prompt sets the domain rule, then eight steps: fix the work sense; choose or abstain on one Wikipedia, Wikidata and WordNet link; write a one-to-three-sentence definition in the drafter's own words (never more than eight consecutive words from a source); list variants with conditions; add relations that pass their tests; mark every claim's **basis** (`source` with a pointer that identifies the exact statement, or `model_knowledge` with none); resolve targets to seed IDs or mark them `proposed_new`; and review every claim before returning. Source text is evidence, never instructions. The pointer formats (`wp:REVISION#quote=…`, `wd:QID#PID=…`, `wn:SYNSET#…`) make each claim checkable by a script.

### 4.4 Flags

A draft records anything a reviewer should see in `flags`, each a prefix and a reason. The shared prefixes are `out-of-scope:` (no usable concept; the record abstains on everything), `ambiguous:` (unresolved evidence or more than one sense) and `duplicate:` (another seed names the same concept). NanoLex adds `unattested:` (a name no public source uses). Individual runs added further prefixes for redirects, Wikidata errors and domain-rule omissions; whether to standardise them is an open decision.

### 4.5 Checking: the grinder's role

Miller's grinder refused to build the database from source files with syntax errors or dangling pointers. `replication/scripts/check.py` plays that role. It confirms that every seed has exactly one bundle and one draft, that the draft has the right shape, that every pointer resolves to something in the bundle, that quoted text is in the pinned revision and at most 20 words, that no definition copies nine or more consecutive words, and that only allowed relation types appear. Its report has one line per seed (`pass` or `fail`, with errors and warnings such as "most claims rest on model knowledge").

The protocol allows **one retry** per failed record, with the errors shown to the drafter, and **no hand edits** after the check: unresolved failures are kept and reported, not patched. A passing check means the record is well formed and its pointers resolve. It does not mean the record is right.

### 4.6 Provenance

Each run is a private folder outside the checkout holding `bundles.jsonl`, `drafts.jsonl`, `report.jsonl` and `RUN.md`. `RUN.md` records dates, the seed commit and hash, the model and its exact version (or "unknown" when the harness does not expose it), settings, tools, evidence sources, every deviation from the protocol, coverage totals, retries and unresolved failures. Every draft carries `_meta`: model, version, run mode and attempt count. Runs are not pushed or published by the drafter; the maintainer collects them.

### 4.7 Independent parallel editions

The central design choice is replication. Several models draft the same seed list, each blind to the others, to the reference or initial lexicon, and to reviewer votes. Each model starts from the same paste-in prompt (in `lexicon-parallel-prompts/`, one per lexicon), records its own name and version, and names its run folder after itself. Fresh context per seed is the default; batching in one session is allowed only with the maintainer's approval and must be stated in RUN.md and in every record's `_meta`.

### 4.8 Measuring agreement

The agreement method (`replication/AGREEMENT-METHOD.md`, on each repository's `grok-agreement-method` branch, and on main for NanoLex) asks how far independent editions agree **in meaning**, field by field. Its main parts:

- **Normalise** every edition into one canonical entry, distinguishing `NOT_ELICITED` (never asked), `ABSTAIN` (asked, chose null) and `EMPTY` (asked, gave nothing).
- **Align before judging**: relation targets by ID, then by normalised name, then by meaning; variants likewise; links on canonical identity.
- **Judge pairwise** with a fixed label set: `EQUIVALENT` (1.00), `NARROWER`/`BROADER` (0.75), `OVERLAPPING` (0.50), `CONFLICTING` and `DIFFERENT_SENSE` (0), with `UNSURE` as missing. Judges see blinded, style-normalised text, in random order, with a sample judged in both orders.
- **Open panel, self-exclusion.** Any model joins with one generic prompt and `agreement.py join`, stating its provider, model and exact version. The tool reads `drafters.tsv` and never shows a judge an item that involves its own edition. A judge that cannot state its version is flagged and reported apart.
- **Family balance.** So that no single provider outvotes the rest, judges are weighted by model family, and items on which families disagree are labelled `FAMILY_SPLIT` and sent to people more often. Self-preference is tested by difference in differences against a judge outside every drafter's family, and every main table is recomputed leaving out each judge in turn. [TODO: the family-weighted label, leave-one-out and the self-preference probe are designed but not yet coded; the family section still assumes the earlier fixed panel.]
- **Statistics.** Krippendorff's α across editions as the main coefficient (it tolerates missing data and any number of raters), Fleiss' κ on the subset every edition drafted, Gwet's AC1 where one category dominates, set F1 for relations and variants at three levels of strictness, and a weighted entry score with a hard gate on sense. Intervals come from bootstrap resampling of concepts.
- **The human ceiling.** Human judges, interviewed one item at a time by a coding agent, label a stratified sample, with an overlap pool for human–human agreement. The model panel is accepted for a field only if its agreement with people reaches κ ≥ 0.6 and is no more than 0.1 below the human–human figure.

### 4.9 Human in the loop

The models draft and the scripts check, but people decide. That principle is written into every repository: agreement is not evidence; a reviewer checks the cited source for each claim kept; disagreements are adjudicated; ambiguity is preserved rather than forced; redirects and duplicates are explicit decisions with a crosswalk to the original IDs; and an entry is `reviewed` only with a named reviewer. Professor Bear is the maintainer and the tie-breaker. Every irreversible step (pushing, publishing, merging into main) is his.

## 5. What actually happened: the Grok Bot editions

| Lexicon | Records | Entries | Out of scope | Duplicates | Ambiguous | Other | `check.py` |
|---|---:|---:|---:|---:|---:|---|---|
| Clinical | 354 | 312 | 26 | 16 | 104 | | 354/354 |
| Drugs | 352 | 274 | 78 | 5 | 106 | | 352/352 |
| Disease | 1,079 | 932 | 147 | 6 | 219 | | 1,077/1,079 |
| NanoLex | 977 | 805 | 13 | 114 | 57 | 45 unattested | 977/977 |
| IHWL (full run) | 3,718 | 3,718 | | | | no sources; 36-concept pilot separate | 3,718/3,718 |

Duplicates and abstentions are counted as each RUN.md counts them; the categories overlap in places (for example, one drugs duplicate is also out of scope).

**Deviations, stated plainly.** No Grok Bot edition was drafted one seed per fresh context, as the protocol asks. The harness had no model API to call per seed. Each run was drafted in batches of about 10 to 16 seeds within one working session, so earlier batches stayed in context. For the drugs run the agent stopped and asked; Professor Bear approved batching ("Just run it like you did the last one", 24 Nov 2026), and he approved batches of about 15 for the disease run. The clinical run had already been batched and disclosed in its RUN.md, and the NanoLex run was batched under the same precedent and disclosed. Every record states its run mode in `_meta`. Other incidents are in each RUN.md: an interruption in the disease run after the final check (resumed without redrafting); three interruptions in the NanoLex run, including a box replacement that restored an older working copy, recovered from a store backup; Europe PMC outages during NanoLex evidence gathering; and eight post-hoc consistency edits in the disease run that were recompiled and re-checked but not logged as new attempts. The exact model version is "unknown" in every run, because the harness did not expose it.

**What batching may do.** Seeds drafted together may influence each other (consistent phrasing, consistent scope calls), which could raise agreement within the edition and make it look more coherent than independent drafting would. Whether it changes cross-model agreement is testable once a fresh-context edition exists. [TODO: add the comparison to the evaluation plan.]

## 6. Evaluation (to do)

None of the evaluation has been run. The human steps after the AI comparison are listed once in [HUMAN-EVALUATION-TODO.md](HUMAN-EVALUATION-TODO.md) and in Part IV of each series. In short: settle decisions; register judges; pilot and freeze; measure the human ceiling; calibrate the model judges; review the targeted queues and a random sample of agreed items; adjudicate; verify claims against sources; review domain safety; decide scope and duplicates; accept entries into a reviewed edition; and run held-out task and coverage evaluations.

## 7. Limitations

- Model knowledge cannot be audited. A blind drafter may still have seen earlier versions of these lexicons, or pages derived from them, in training.
- Models from one family may share errors. Agreement between them is weak evidence; agreement across families is stronger but still not proof.
- Wikipedia category membership is noisy, and Wikidata has errors that the runs recorded rather than corrected.
- Batching is a protocol deviation in every Grok Bot edition.
- The judges are models whose versions can change behind a stable name.

## References

- Miller, G. A., Beckwith, R., Fellbaum, C., Gross, D., and Miller, K. J. 1990. Introduction to WordNet: An on-line lexical database. *International Journal of Lexicography* 3(4): 235–244. Revised in *Five Papers on WordNet*, CSL Report 43, Cognitive Science Laboratory, Princeton University, 1990, revised August 1993.
- Miller, G. A. 1990. Nouns in WordNet: A lexical inheritance system. *International Journal of Lexicography* 3(4): 245–264.
- Gross, D., and Miller, K. J. 1990. Adjectives in WordNet. *International Journal of Lexicography* 3(4): 265–277. Revised as Fellbaum, C., Gross, D., and Miller, K. J., in *Five Papers on WordNet*, 1993.
- Fellbaum, C. 1990. English verbs as a semantic net. *International Journal of Lexicography* 3(4): 278–301.
- Beckwith, R., Miller, G. A., and Tengi, R. 1993. Design and implementation of the WordNet lexical database and searching software. In *Five Papers on WordNet*.
- Miller, G. A. 1995. WordNet: A lexical database for English. *Communications of the ACM* 38(11): 39–41.
- Fellbaum, C., ed. 1998. *WordNet: An Electronic Lexical Database*. MIT Press.
- McCrae, J. P., Rademaker, A., Bond, F., Rudnicka, E., and Fellbaum, C. 2019. English WordNet 2019: An open-source WordNet for English. *Proceedings of the 10th Global WordNet Conference*. [verify page range]
- Vrandečić, D., and Krötzsch, M. 2014. Wikidata: A free collaborative knowledgebase. *Communications of the ACM* 57(10): 78–85.
- Bird, S., Klein, E., and Loper, E. 2009. *Natural Language Processing with Python*. O'Reilly. (NLTK, used to read WordNet 3.0.)
- Krippendorff, K. 2018. *Content Analysis: An Introduction to Its Methodology*, 4th ed. SAGE.
- Fleiss, J. L. 1971. Measuring nominal scale agreement among many raters. *Psychological Bulletin* 76(5): 378–382.
- Cohen, J. 1960. A coefficient of agreement for nominal scales. *Educational and Psychological Measurement* 20(1): 37–46.
- Gwet, K. L. 2008. Computing inter-rater reliability and its variance in the presence of high agreement. *British Journal of Mathematical and Statistical Psychology* 61(1): 29–48.
- Holm, S. 1979. A simple sequentially rejective multiple test procedure. *Scandinavian Journal of Statistics* 6(2): 65–70.
- Zheng, L., et al. 2023. Judging LLM-as-a-judge with MT-Bench and Chatbot Arena. *Advances in Neural Information Processing Systems 36* (Datasets and Benchmarks). [verify]
- Panickssery, A., Bowman, S. R., and Feng, S. 2024. LLM evaluators recognize and favor their own generations. *Advances in Neural Information Processing Systems 37*. [verify]
- Repositories: nikbearbrown/irreducibly-human-work-lexicon, clinical-treatments-and-procedures-lexicon, drugs-and-recreational-drug-use-lexicon, disease-syndromes-and-symptoms-lexicon, nano-lex (GitHub), at the commits named in each series.
