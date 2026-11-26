# NanoLex: a lexicon of nanomedicine terms

*Rough draft, not reviewed.* A paper series modelled on *Five Papers on WordNet*. Nik Bear Brown and Humanitarians AI [TODO: confirm authorship]. Drafted 2026-11-26 with Grok Bot.

**Where it stands:** the 977-term seed list, drafting kit, validators and judging setup are public; one independent Grok Bot edition is drafted and checked (977/977 pass: 805 entries, 13 out of scope, 114 duplicates, 45 unattested, 57 ambiguous). The initial, unchecked NanoLex (2024–2025) is kept in a private archive and has not yet been compared. No second edition, no cross-model judging and no human review have been run. NanoLex describes terms; it is not medical advice and makes no claim that a product works or is safe.

## Part I. Introduction to NanoLex

### I.1 What the lexicon is for

Nanomedicine borrows from chemistry, materials science, pharmacology and imaging, and coins names fast: product brands, abbreviations for polymers, nano-prefixed words for older ideas. A reader meets *PAMAM*, *PEG-PAMAM*, *Doxil*, *Caelyx* and *pegylated liposomal doxorubicin* and needs to know which name what, which are brands, and which are only spellings of each other. NanoLex covers nanomaterials and carriers, formulations and named products, techniques, and the biological targets they act on.

NanoLex also has an unusual history, which shapes everything below. Its first version was written by one language model in 2024–2025 and nobody checked it. The current project rebuilds it from independent editions, using the initial lexicon's headings as seeds but never its definitions, and compares the initial lexicon only at the end, as one more edition.

### I.2 Why a WordNet-style relational lexicon

A glossary of nanomedicine terms would list *Liposome* and *Pegylated Liposome* separately. A relational lexicon says the second is a kind of the first, that a brand uses both a drug and a carrier, and that two particle names that sound alike are different things. WordNet showed that a small set of tested relations can carry this structure (Miller et al. 1990/1993); for a field that coins words this fast, the structure is what makes new names placeable.

### I.3 The lexical matrix, adapted

Rows are concepts and columns are names, as in the other lexicons, but the seed list here is a list of **names**, not concepts. 977 seeds came from 2,117 headings of the initial lexicon; only forms differing in case, quotes, trade-mark signs or spacing were merged (9 forms). Hyphen and spelling variants (*Nano-Ceria*, *Nanoceria*) and names with and without an abbreviation stayed separate seeds. Deciding which names share a row is therefore part of the drafting, recorded with the `duplicate:` flag. The Grok Bot edition found 114 such duplicates, for example *EPR Effect* as the abbreviated name of *Enhanced Permeability and Retention (EPR) Effect*.

The seed file records each name's form: multiword (500), nano-prefixed (307), single-word (110) and abbreviated (60).

### I.4 The relations

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

**Certifies** is not used. In the Grok Bot edition the hypernym leads (498 edges), then hyponym (232), contrast (136), uses (130), synonym (82), meronym (21), holonym (7) and requires (1) [counted from `drafts.jsonl` on 2026-11-26]. Two features stand out against the other lexicons: hyponyms are common, because carriers and materials have many named subtypes, and `uses` is common, because named products are defined by the drug and carrier they combine.

### I.5 Built with AI: what changes and what does not

The common pipeline applies. Three things are specific. Seeds come with no page, so the drafter must find evidence for each name and may conclude the name is not in use (`unattested:`). The domain rule forbids any efficacy or safety claim a cited source does not state. And a fourth check, `leak_check.py`, compares each edition's wording with the initial lexicon, so an edition that copied it is caught before it counts.

## Part II. The vocabulary by category

The seed file has no category column; the four categories below are those named in the repository's README. Kind is not yet a field in the schema [open decision].

### II.1 Nanomaterials and carriers

Particles, vesicles, dendrimers, polymers and their subtypes. The hypernym and hyponym organise this part like WordNet's nouns. *Liposome* is a kind of vesicle with hyponyms *Echogenic Liposome*, *Pegylated Liposome* and *Folic Acid-Targeted Liposome*; *PAMAM* is a kind of dendrimer with the hyponym *PEG-PAMAM*. Contrast keeps similar names apart: *Quantum Dot* has the synonym *Semiconductor Nanocrystal* and a contrast with *Carbon Quantum Dot*, an edge a human reviewer should examine, since the draft also lists *Graphene Quantum Dot* as a hyponym.

### II.2 Formulations and named products

Brands and named formulations. The `uses` relation and brand variants carry this part. *Doxil* is drafted as a brand of pegylated liposomal doxorubicin, with *Caelyx* as a variant under the condition "brand outside the United States", a synonym *Pegylated Doxorubicin*, and `uses` edges to *Doxorubicin* and *Liposome*. Brand policy is not yet consistent: *Nanostim*, a pacemaker brand, was placed out of scope, while *NanoDrop* and *NanoLuc* were kept.

### II.3 Techniques

Imaging, characterisation and measurement methods. Many seeds keep the inverted heading order of indexing vocabularies (*Microscopy, Scanning Tunneling*), so canonical form is a recurring decision. The run's rule picked the closed, natural-order form, with two recorded exceptions where the other form had already been drafted.

### II.4 Biological targets and mechanisms

Receptors, tissues and proposed mechanisms that nanomedicine terms refer to. The domain rule is most important here. The *Enhanced Permeability and Retention (EPR) Effect* is drafted as "the proposed tendency" of nanoparticles and large molecules to collect in tumour tissue, wording that does not claim the effect is established beyond what the sources say.

### II.5 Names that are not terms

Forty-five seeds are unattested: no public source used the name. Some may be invented by the initial lexicon, some truncated (*Nanoporou*, drafted as *nanoporous* with a note), and at least one (*Nanodosing*) was marked unattested despite eight full-text hits, which a person should revisit. Thirteen seeds are out of scope (brands outside nanomedicine, gene products, taxa). Non-nano biomedical terms (drugs, conditions) were kept as entries with a note.

## Part III. Design and implementation

### III.1 Seed list and manifest

977 seeds, `nanolex:0001` to `nanolex:0977`; SHA-256 `def0820e9baf4934cfbf9484c3061c5548785dc2f2821942c6b38fbc45386a38`; repository main at `bd0bd4cf`. Built by `data/build_seeds.py` from the entry headings of the initial lexicon (source commit `9bff63f` in the private archive): 2,117 headings read, 2 rejected, 9 forms merged away. `validate_seeds.py` checks the file against the manifest; a maintainer holding the initial lexicon can confirm it rebuilds byte for byte.

### III.2 Evidence bundles

For each name: Wikipedia title lookup and search (up to three candidates, revision pinned); Wikidata search, excluding publications and clinical-trial items; WordNet noun and adjective lemmas; and, where those were thin, the NCI Thesaurus, MeSH (descriptor lookup and scope note), PubChem for compounds, and Europe PMC searches for the quoted name, with an automatic follow-up adding up to two sentences from different articles. Every query and its hit count is logged in the bundle.

### III.3 Drafting prompt and kit

Prompt gen-v2 with the domain rule: "Say what the term names in nanomedicine at a high level. Say when a name is a brand, an abbreviation or a spelling variant of another term. Do not give preparation or synthesis protocols, doses, clinical advice or patient-specific guidance, and make no efficacy or safety claim that a cited source does not state."

### III.4 Flags

`out-of-scope:`, `duplicate: <seed id and name>`, `unattested: <where you searched>` and `ambiguous:`, all defined in `instructions.md`. The Grok Bot run also used `note:` (135 records).

### III.5 Checking

977/977 pass. Twenty records failed on the first attempt and passed after one retry. Two known issues passed the check and were left as written: 0181 reuses nine words from an example, and 0015 has a null hypernym target though the target seed exists. The run's own lint was extended twice during the run; it never gained the 20-word quote limit, which caused one failure.

### III.6 Provenance

Run folder `nanolex-run-grok`, with the four handoff files and `work/` (batch sources, retry files, first failures, notes, rendered prompts). Every draft records batched drafting in `_meta.run_mode`.

### III.7 The Grok Bot edition: what was done and how it deviated

Drafted on 2026-11-25 between about 1:28 and 4:07 AM EST, in 66 batches of 15 (the last of 2), in one session; no entry was drafted in a fresh context. Three interruptions: after batch 16; at batch 33, when the box was replaced and the working folder came back at an older state, restored from the store backup; and after batch 55. Each time the run resumed from its progress file with the same rules. Europe PMC returned errors for several minutes around batch 52, affecting evidence for a few seeds (0790 was marked unattested while searches were failing). Some examples were added by manual query or copied between related seeds' bundles, with URLs kept. Blindness: no copy of the initial lexicon, no other run and no judging material was opened. Residual risk: public pages may themselves reflect the initial NanoLex.

### III.8 Parallel editions and agreement

Paste-in prompt `05-nanolex.md`. The judging setup is on main (`replication/judging/`, `AGREEMENT-METHOD.md`, `agreement.py`), with no `drafters.tsv` rows yet. The initial lexicon enters as an edition only after the independent editions are frozen, through `legacy_to_edition.py`.

### III.9 Human in the loop

People decide canonical forms, brand policy, attestation, and every claim about what a material or product does.

## Part IV. Evaluation (to do): what humans do after the AI comparison

### IV.1 Status

Not run. One independent edition exists; the initial lexicon has not been compared.

### IV.2 Prerequisites on the AI side

A second blind edition; `drafters.tsv` rows; `leak_check.py` on every edition; `agreement.py run`; model judges; then `legacy_to_edition.py` for the initial lexicon. See [HUMAN-EVALUATION-TODO.md](HUMAN-EVALUATION-TODO.md), Part 1.

### IV.3 Human steps in order

The steps below are the same for every lexicon and are written out once, with owners and checkboxes, in [HUMAN-EVALUATION-TODO.md](HUMAN-EVALUATION-TODO.md). They run **after** the AI side has produced its blinded, pairwise comparison of the independent editions. Every step is a human step. None has started.

| # | Human step | What it produces | Gate before the next step | Owner | Status |
|---|---|---|---|---|---|
| H1 | Settle the open decisions (IV.6): judge invitations, `drafters.tsv` rows, trap list, worked examples, weights, acceptance threshold | a committed decision record | Bear signs off | Bear | not started |
| H2 | Recruit and register human judges (`agreement.py register`) | registry rows, seeded samples | at least 2 judges for the pilot; about 10 for full scale | Bear | not started |
| H3 | Pilot: Bear and at least one other judge label the whole pilot pool; tune the rubric on the development half only; freeze the prompts (`agree-v1`) and tag the analysis plan | adjudicated pilot labels, frozen rubric | rubric frozen and tagged | Bear + 1 judge | not started |
| H4 | Human–human overlap pool: about 30% of each judge's items come from a shared pool of about 50, each item judged by at least 2 people | the **human ceiling** (Krippendorff's α, pairwise κ, before adjudication) | ceiling reported per field | human judges | not started |
| H5 | Calibrate the AI judges against people: judge–human κ per field, for the panel, for the outside-family judge alone and for each judge | acceptance per field | κ ≥ 0.6 **and** no more than 0.1 below human–human; otherwise revise the rubric on the development split only and redraw the validation sample | Bear | not started |
| H6 | Targeted review queues (IV.4): disagreements, `FAMILY_SPLIT`, low agreement, flagged records, redirects, Wikidata errors, consensus gaps | a human label for each queued item | every queued item labelled or marked `UNSURE` with a note | human judges | not started |
| H7 | Random audit of agreed items: a seeded sample of items every model agreed on | the false-agreement rate | reported with an interval | human judges | not started |
| H8 | Adjudicate: majority of human judges, ties to Bear, judges' own words kept in `notes` | one adjudicated label per reviewed item | no open ties | Bear | not started |
| H9 | Verify claims (correctness, not agreement): for every claim kept, a reviewer opens the cited source and marks `supports`, `contradicts` or `unsure`; claims with only `model_knowledge` basis are sourced or withheld | per-claim decisions | no kept claim without a named check | reviewers | not started |
| H10 | Domain-safety review against the lexicon's rule (IV.4) | a pass or a list of removals | zero open safety items | Bear or a named domain reviewer | not started |
| H11 | Scope, duplicate and redirect decisions, with a crosswalk to the original seed IDs | decision list and crosswalk | every flagged seed decided | Bear | not started |
| H12 | Accept or reject merged entries into the reviewed edition (`lexicon/entries.jsonl`), with per-claim decisions, contributing run IDs and a named reviewer | the first reviewed entries | each accepted entry has a named reviewer and no unresolved contradiction | Bear | not started |
| H13 | Held-out task and coverage evaluations (IV.5) | task scores with intervals | analysis plan fixed before annotation | Bear + raters | not started |
| H14 | Write up: human ceiling, judge–human agreement, false-agreement rate, safety outcome, accepted-entry counts | the evaluation section of this paper | Bear approves | Bear | not started |

Agreement between models is not evidence that an entry is right. Steps H9 to H12 exist because two models can agree on the same mistake.

### IV.4 What humans review in this lexicon

Editions available today: **one** independent edition, Grok Bot's (977 records, 805 entries), plus the **initial NanoLex**, written by one language model in 2024–2025, never checked, and kept in a private archive. The initial lexicon joins the comparison only as one more edition, after the independent editions are frozen (`legacy_to_edition.py`). A second blind edition is needed first (paste-in prompt `05-nanolex.md`).

| Queue | Source | Size in the Grok edition | What the human decides |
|---|---|---:|---|
| Duplicates | `duplicate:` | 114 | which form is canonical; the run deviated from its own closed-form rule twice (0772 and 0781 to 0720 PAMAM; 0788 to 0261) |
| Unattested | `unattested:` | 45 | search again; a name found in the literature becomes a seed to draft, a name not found stays out. 0790 was marked during a Europe PMC outage; 0527 Nanodosing had 8 full-text hits |
| Ambiguous | `ambiguous:` | 57 | sense, scope |
| Out of scope | `out-of-scope:` | 13 | confirm (brands, gene products, taxa) |
| Notes | `note:` | 135 | read; many record non-nano biomedical terms kept as entries |
| Least-sure ten | RUN.md | 10 | each in turn |
| Retried drafts | `_meta.attempt_count = 2` | 20 | spot-check |
| Known issues that passed the check | RUN.md | 2 (0181 reuses 9 words from an example; 0015 has a null hypernym target although seed 0748 exists) | fix in the reviewed edition |
| Blindness | `leak_check.py` | every edition | maintainer runs it against the initial lexicon; any edition sharing eight or more words with it is investigated before it counts |

**Claims about effects.** NanoLex has a stricter claim rule than the other lexicons: no efficacy or safety claim that a cited source does not state. In practice, phrases such as "valued for their redox activity, used as … antioxidants" (in the Grok *Nanoceria* work sense) must be checked against the cited source in H9, and withheld if the source does not say it.

**Domain-safety review (H10).** The rule: say what the term names; say when a name is a brand, abbreviation or spelling variant; no preparation or synthesis protocols, doses, clinical advice or patient-specific guidance; no efficacy or safety claim that a cited source does not state. The reviewer reads every definition and every `uses` relation, and every entry for a named product. Pass criterion: no protocol or dose, and no effect claim without a source pointer that states it.

### IV.5 Held-out task and coverage evaluations

- **Attestation.** For the 45 unattested and a sample of attested seeds, a person searches the literature and records whether the term is in use and in what sense. Measures how much of the initial lexicon named real terms. Status: not designed.
- **Coverage.** Map a sample to MeSH (Nanostructures, Nanotechnology), the NCI Thesaurus, and the ISO/TS 80004 nanotechnology vocabulary series. Status: not designed [TODO: access to ISO texts].
- **The initial lexicon as an edition.** After freezing, the initial NanoLex is judged like any edition. A claim that only it makes, with no source, is withheld (lexicon/README.md).

### IV.6 Open decisions

- The eight "Decisions for Bear" in `AGREEMENT-METHOD.md` §12 on main: invitations (`drafters.tsv` has no rows yet; the model that wrote the initial lexicon is not recorded); human judges and settings; weights and threshold; scope agreement as an outcome; the draft `TRAP_IDS`; whether a reviewed edition counts in α; scheduling; the placeholder human worked examples.
- Canonical form for duplicates (the closed-form rule and its two exceptions).
- Brand policy: 0660 Nanostim was put out of scope as a brand, while NanoDrop and NanoLuc were kept.
- Policy for non-nano biomedical terms (kept with a note, following 0074) and for gene products and taxa (out of scope).
- Who drafts the second edition.

### IV.7 Resources, owners and status

About 10 human judges at about 100 items each; a reviewer with literature access for attestation; a domain-safety reviewer for effect claims. Tools: `agreement.py register`, `validate`, `stats`; `leak_check.py` (maintainer). Owner: Bear unless delegated. Status: not started.

## Part V. Limitations

The seeds are what one model chose to define, not a survey of the field. Evidence for rare names is thin and depended on one literature service that was intermittently down. The edition was batched and interrupted three times.

## Appendix A. File formats

**Seeds** (`data/seeds.tsv`): `concept_id` (`nanolex:<NNNN>`), `preferred_name`, `term_form` (abbreviated, nano-prefixed, multiword, single-word), `merged_forms`.

**Evidence bundle** (`bundles.jsonl`, one JSON object per seed, exactly seven top-level fields):

| Field | Content |
|---|---|
| `concept_id` | the seed ID, unchanged |
| `concept` | `id`, `preferred_name`, `kind` and `broad_class` (`unclassified` until supported), `variants` and `relations` (start empty) |
| `neighbors` | candidate relation targets, taken only from the seed list, each `{id, name}` |
| `examples` | optional public terminology excerpts `{id, source URL, text}` |
| `wikipedia` | up to three `{title, revision_id, text}`; the revision is pinned |
| `wikidata` | candidate items `{qid, label, aliases, claims, revision_id}` and ancestors marked `ancestor_of` |
| `wordnet` | matching senses `{synset, lemmas, gloss, relations}` |

**Draft** (`drafts.jsonl`, one JSON object per seed, prompt gen-v2):

| Field | Content |
|---|---|
| `concept_id` | the seed ID |
| `work_sense` | one sentence fixing the sense every later decision is about (the name is kept from the first lexicon for schema compatibility) |
| `links.{wikipedia,wikidata,wordnet}` | `{choice, reason}`; `choice` is a revision ID, QID or synset ID, or `null` to abstain |
| `definition` | `{text, basis, pointers}`; one to three sentences, never more than eight consecutive words from a source |
| `variants[]` | `{text, condition, basis, pointers}`; `condition` says when the form names the concept |
| `relations[]` | `{type, target_label, target_id, proposed_new, basis, pointers, note}` |
| `flags[]` | strings, each a prefix and a reason (Appendix B) |
| `_meta` | added after drafting: model and version (or `unknown`), run mode, attempt count, and for retries the errors that triggered them |

**Pointer forms:** `wd:QID#PID=VALUE_QID`, `wd:QID#alias=TEXT`, `wn:SYNSET#lemma=TEXT`, `wn:SYNSET#RELATION=TARGET`, `wp:REVISION_ID#quote=TEXT` (at most 20 words, copied exactly), `ex:EXAMPLE_ID`.

**Check report** (`report.jsonl`): one line per seed, `{concept_id, status: pass|fail, errors[], warnings[]}`.

**RUN.md:** dates, seed commit and hash, model and settings, tools, evidence sources, deviations, coverage totals, retries and unresolved failures.

## Appendix B. Flags

| Prefix | Meaning |
|---|---|
| `out-of-scope: <reason>` | no usable nanomedicine sense |
| `duplicate: <seed id and name>` | only another spelling, plural or abbreviation of another seed; written as out of scope |
| `unattested: <where searched>` | no public source uses the name; no definition from its parts |
| `ambiguous: <reason>` | unresolved evidence or more than one sense |
| `note:` | used by the Grok Bot run for reviewer notes (not defined in `instructions.md`) |

## Appendix C. Scripts

| Script | Who runs it | What it does |
|---|---|---|
| `validate_seeds.py` | anyone | seed file matches the manifest |
| `render.py` | drafter | one system and user message per bundle |
| `check.py` | drafter, then maintainer | completeness, shape, pointers (calls `verify_drafts.py`) |
| `leak_check.py` | maintainer | no draft definition shares eight or more consecutive words with the initial lexicon |
| `legacy_to_edition.py` | maintainer | converts the initial lexicon into an edition after the independent editions are frozen |
| `agreement.py` | maintainer and judges | normalise, compare, blinded requests, validate, stats |

## References

- Miller, G. A., Beckwith, R., Fellbaum, C., Gross, D., and Miller, K. J. 1990. Introduction to WordNet: An on-line lexical database. *International Journal of Lexicography* 3(4): 235–244. Revised in *Five Papers on WordNet*, CSL Report 43, Princeton University, 1990, revised 1993.
- Miller, G. A. 1990. Nouns in WordNet: A lexical inheritance system. *International Journal of Lexicography* 3(4): 245–264.
- Gross, D., and Miller, K. J. 1990. Adjectives in WordNet. *International Journal of Lexicography* 3(4): 265–277. Revised as Fellbaum, Gross and Miller in *Five Papers on WordNet*, 1993.
- Fellbaum, C. 1990. English verbs as a semantic net. *International Journal of Lexicography* 3(4): 278–301.
- Beckwith, R., Miller, G. A., and Tengi, R. 1993. Design and implementation of the WordNet lexical database and searching software. In *Five Papers on WordNet*.
- Miller, G. A. 1995. WordNet: A lexical database for English. *Communications of the ACM* 38(11): 39–41.
- Fellbaum, C., ed. 1998. *WordNet: An Electronic Lexical Database*. MIT Press.
- Vrandečić, D., and Krötzsch, M. 2014. Wikidata: A free collaborative knowledgebase. *Communications of the ACM* 57(10): 78–85.
- Krippendorff, K. 2018. *Content Analysis: An Introduction to Its Methodology*, 4th ed. SAGE.
- Fleiss, J. L. 1971. Measuring nominal scale agreement among many raters. *Psychological Bulletin* 76(5): 378–382.
- Shared methods paper: *Building WordNet-style lexica with AI: process and provenance* (`building-wordnet-style-lexica-with-ai.md` in this folder).
- MeSH, the NCI Thesaurus, PubChem, Europe PMC and the ISO/TS 80004 series are named as evidence sources or candidate reference vocabularies [TODO: add formal citations].
