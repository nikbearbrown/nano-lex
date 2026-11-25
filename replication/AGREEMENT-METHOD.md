# Measuring semantic agreement between independent model editions of NanoLex

**Status:** proposal, draft (agree-v1-draft), adapted 2026-11-24 by Claude (Claude Code) for Nik Bear Brown from the agreement method of the Drugs and Recreational Drug Use Lexicon (`nikbearbrown/drugs-and-recreational-drug-use-lexicon`, branch `grok-agreement-method`; itself ported through the clinical lexicon from the Irreducibly Human Work Lexicon kit, 78f889a2). The schema (gen-v2) and the method are unchanged; the domain rule, frame, strata, prompts, examples and draft trap list are this repository's, and one adapter was added so that the initial NanoLex can join as an edition. Nothing here has been run on real editions yet, and no run folder (`replication/agreement/...`) exists. The instructions for judges are in [judging/](judging/README.md): [AI-JUDGE-INSTRUCTIONS.md](judging/AI-JUDGE-INSTRUCTIONS.md) for model judges, [START-HERE-AI-JUDGE.md](judging/START-HERE-AI-JUDGE.md) for the one generic paste-in prompt, [HUMAN-JUDGE-INSTRUCTIONS.md](judging/HUMAN-JUDGE-INSTRUCTIONS.md) for people, and [INTERVIEWER-PROTOCOL.md](judging/INTERVIEWER-PROTOCOL.md) for the agent that runs a person's session. All share one schema ([judgment.schema.json](judging/judgment.schema.json)) and one validator (`agreement.py validate`). `scripts/agreement.py` is a draft skeleton that does the deterministic parts (normalising the editions, coverage and scope, ID and string alignment, the statistics) and writes blinded judge requests; it never calls a model.

**Question.** The initial NanoLex was written by one language model in 2024–2025 and never checked. When several other models draft the same terms independently, without seeing it or each other, how far do they agree with one another, and how far does the initial lexicon agree with them? Field by field (sense, definition, links, variants, every relation type, basis, scope decision), for each pair of editions and across all of them, measured in meaning rather than wording. A panel of language models judges, human judges validate the panel, and deterministic matching gives a lower bound.

**Domain rule (binds every drafter, judge and operator).** From [instructions.md](instructions.md): say what the term names in nanomedicine at a high level; say when a name is a brand, an abbreviation or a spelling variant of another term; give no preparation or synthesis protocols, doses, clinical advice or patient-specific guidance; make no efficacy or safety claim that a cited source does not state. Judges compare meanings without adding any such guidance and without judging whether a material, product or treatment works or is safe. No request, packet, result, note or rationale may contain details of an identifiable person's health; an item that appears to is labelled `UNSURE` with the note "possible personal information" and reported to the operator.

**Builds on:** [instructions.md](instructions.md) (the gen-v2 draft shape and flag rules), `scripts/verify_drafts.py` and `scripts/check.py` (whether a run is complete and its pointers valid), and [../lexicon/README.md](../lexicon/README.md) (reconciliation). Agreement is not evidence: a reviewer still checks the cited source for each retained claim (section 11).

---

## 1. Editions and the concept frame

**Concept frame.** The 977 seeds of [../data/seeds.tsv](../data/seeds.tsv) (sha256 `def0820e9baf4934cfbf9484c3061c5548785dc2f2821942c6b38fbc45386a38`, see [../data/source-manifest.json](../data/source-manifest.json)): every term that heads an entry in the initial NanoLex files, after the cleaning recorded in the manifest. Only the term names were taken; no definition, classification or relation text is in the seed list, and drafters and judges never see the initial lexicon (it is kept in a separate private archive, `nikbearbrown/nano-lex-initial-2025`, and is not in this repository or its history). Forms that differ only in case, quotes, trade-mark signs or spacing were merged; hyphen and spelling variants such as *Nano-Ceria* and *Nanoceria* are separate seeds on purpose, so that each edition has to decide whether they are one concept. Every edition has exactly one record per `concept_id` (`nanolex:<NNNN>`), either an entry or a flagged abstention. There is **no reference lexicon** yet ([../lexicon/README.md](../lexicon/README.md)); when a reviewed `lexicon/entries.jsonl` exists, `run --lexicon` uses its variants for name resolution and `--with-reference` adds it as an edition (reported separately, section 6.6).

**Editions.** Each edition is a private run folder handed in under [README.md](README.md) (bundles, drafts, report, RUN.md). Drafts are **never committed** here; `agreement.py run` reads them from private paths. Known so far:

| Edition name | Drafter | Shape | Grounding | Notes |
|---|---|---|---|---|
| `legacy` | the initial NanoLex (one language model, 2024–2025; the model and version were not recorded) | `nanolex-legacy`, made by `scripts/legacy_to_edition.py` | none: no sources or pointers | joins only after the independent editions are frozen; links, basis and fine relation types are NOT_ELICITED; antonyms, verb relations and pertainyms are not carried over |

No independent edition exists yet. Each one is added to this table and to [judging/drafters.tsv](judging/drafters.tsv) before any judge joins.

### 1.1 Schema crosswalk (step 0: normalise before comparing)

Every edition is converted into one **canonical entry** (`agreement.py`, `canon_genv2`). Fields an edition never asked for become `NOT_ELICITED`; `ABSTAIN` means asked and chose null; `EMPTY` means asked and gave an empty list.

| Canonical field | gen-v2 draft ([instructions.md](instructions.md)) |
|---|---|
| `scope` | `entry`; or, when `definition.text` is "Out of scope", `duplicate` if a flag starts with `duplicate:`, else `out-of-scope` |
| `flags` | `flags` (strings; `ambiguous:`, `duplicate:`, `out-of-scope:` and free notes) |
| `sense` | `work_sense` (kept under its original name; here it states the sense in nanomedicine usage) |
| `definition` | `definition.text`, with `definition.basis` and `definition.pointers` |
| `links.{wikipedia,wikidata,wordnet}` | `choice`, or ABSTAIN when null |
| `variants[].text`, `.conditional`, `.condition` | `text`; `condition` is not null; `condition` |
| `relations[].type_fine` | the nine gen-v2 types (synonym, hypernym, hyponym, meronym, holonym, uses, requires, certifies, contrast) |
| `relations[].axis` | coarse axis (map below) |
| `relations[].target_id` / `target_label` / `proposed_new` | as drafted; a seed `concept_id` when the target is another seed |
| `basis` | per claim: `source` (with pointers) or `model_knowledge` |

A `nanolex-legacy` adapter converts the initial lexicon: its definition also serves as the sense, its synonyms become unconditional variants, and its hypernyms, hyponyms, meronyms and holonyms become label-only relations resolved by name. A `sonnet-edition` adapter is kept from the source kit for editions in a different shape; such editions get `scope = entry` and NOT_ELICITED links and fine types.

**Relation type map.** Agreement is measured on a coarse axis and, between gen-v2 editions, on the fine type: `EQUIV` synonym; `TAX_UP` hypernym; `TAX_DOWN` hyponym; `PART_UP` holonym; `PART_DOWN` meronym; `ASSOC` uses, requires, certifies; `CONTRAST` contrast. A hyponym in one entry and the matching hypernym in the target's entry count as the same edge in the graph-level analysis (section 6.3); opposite directions on the same pair are a **reversal**.

### 1.2 What changed from the source method (adaptation to this lexicon)

1. **IDs and frame.** Concepts are the seed ids `nanolex:<NNNN>`; the frame is `data/seeds.tsv`, not a lexicon roster. Ids outside the seed list are reported and ignored.
2. **Scope decisions are a compared field (L0b).** Out-of-scope and duplicate abstentions are compared deterministically (same label, both entries, both abstain, one abstains, Gwet's AC1) and are **never** sent to definition judges. Definitions, variants and relations are compared only where both editions wrote an entry, so "said something different" is separated from "declined to say anything".
3. **Strata.** The seeds carry no category, and the initial lexicon's own classifications are withheld, so `broad_class` is the seed's `term_form`, computed from the name alone (abbreviated, nano-prefixed, multiword, single-word). It fills the `{kind}` slot of the prompts, shown as "term form: ...".
4. **Prompts.** The system prompt and P1, P2, P3, P4 and P6 are reworded for nanomedicine, and the system prompt carries the domain rule (section 4.2). Judges, human and AI, get the same rules and labels.
5. **Trap concepts** (look-alike pairs, umbrella terms, short or multi-sense names): the list in `agreement.py` (`TRAP_IDS`) is a **DRAFT for Bear's review**. Claude chose it from the seed names while setting up this kit, in a session that had the initial lexicon open, so the maintainer should confirm or replace it before the first run.
6. **Name normalisation** drops trade-mark signs instead of disambiguators such as "(programming language)".
7. **No reference lexicon and no copy-through anchor**: bundles in this repository show no existing lexicon record, so section 6.6's copy-through correction applies only once a reviewed edition exists.
8. **The initial lexicon is an edition, not a reference.** It is compared like any other edition and reported separately, so that "the independent editions agree with each other" and "the initial lexicon agrees with them" are two results. `scripts/leak_check.py` tests each independent edition for wording shared with the initial lexicon before it is admitted.

Where sections 2–12 below still use examples from the work-concept lexicon (editions named Grok, Sonnet and the reference at `91312fec`), read them as the general method; the lexicon-specific details are those in this section and in [judging/](judging/README.md).

---

## 2. What gets compared: units and levels

| Level | Unit | Value each edition gives | Comparison |
|---|---|---|---|
| L0 coverage | concept | drafted or not, with a pass or fail status | deterministic |
| L1 sense | concept | sense statement (work_sense, or the definition as proxy) | LLM: sense clustering |
| L2 definition | concept × model pair | definition text | LLM: pairwise label |
| L3 links | concept × source | ID, ABSTAIN, NOT_OFFERED or NOT_ELICITED | deterministic, with LLM only to tell "different but compatible" from "conflicting" |
| L4 variants | concept | set of strings, each conditional or not, with a condition | align (strings, then LLM), set F1, then condition label |
| L5 relations | concept × axis (and × fine type) | set of targets | align (ID, string, LLM), set F1, type label on matched targets |
| L6 basis and pointers | aligned claim | source or model_knowledge; pointer list | deterministic |
| L7 target status | aligned relation target | in the lexicon (ID) or proposed_new | deterministic |
| L8 entry | concept × model pair | all of the above | composite score |

---

## 3. Alignment: match items across models before judging

Alignment comes first. If items are not matched, a judge asked whether "two relation lists agree" will reward lists that look similar, not lists that say the same thing.

**3.1 Sense gate (L1).** For each concept, the judge sees the concept's name and kind plus every edition's sense statement, anonymised and shuffled. It groups them into **sense clusters**: same referent, or different referent (prompt P1). A model whose sense falls outside the majority cluster is marked `cross_sense` for that concept. Its other fields are still compared but reported **separately**, because disagreement about relations is then a consequence of having picked a different sense (*SLN* as a solid lipid nanoparticle versus a sentinel lymph node, for example). This is also the main result for the trap concepts.

**3.2 Relation targets (L5).** These are aligned in three passes, each logged with the pass that produced the match:

1. **By ID.** `target_id` or `target` equal. Exact, no judge needed.
2. **By name.** A proposed_new label is normalised (NFKC, case-folded, punctuation and spacing removed, trade-mark signs dropped) and matched to a seed `preferred_name` (or a reviewed-lexicon variant label, once one exists). If exactly one concept matches, the label resolves to that ID (`resolved_by=name`). If several match, it stays unresolved.
3. **By meaning.** Within one concept, take every target still unresolved, plus the other editions' targets on the same coarse axis family. The judge clusters them into "same concept" groups (prompt P3). A group containing a lexicon ID takes that ID. Otherwise it gets a synthetic key `new:<concept_id>:<k>`. Grouping across axes is allowed, so that "uses polyethylene glycol" and "requires polyethylene glycol" align on target and then disagree on type.

**3.3 Variants (L4).** First an exact match after normalisation. The rest go to the judge clustering prompt (P3), with the rule that a variant matches only if it names the same concept (so "LNP" and "lipid nanoparticle" match, but "PEGylated liposome" and "liposome" do not).

**3.4 Links (L3).** Links are matched on canonical identity, not on raw strings. A Wikipedia revision ID is resolved to its page ID and title after redirects, using the model's own bundle, because models that built their own bundles (way A) have different revisions of the same page. Wikidata uses the QID. WordNet uses the synset name of the WordNet version the edition records (Grok's edition: WordNet 3.0 via nltk); editions on different WordNet versions are mapped through the sense key before comparison.

All alignments are saved (`alignment/*.jsonl`, section 10) **before** any agreement label is assigned. 10% of the meaning-based alignments go into the human validation sample (section 9).

---

## 4. The LLM judge

### 4.1 Labels for each field

**Definitions and sense statements (pairwise, P2).** One label, with sub-fields:

| Label | Meaning | Score |
|---|---|---:|
| `EQUIVALENT` | Same sense, same genus, same essential differentia. A nanomedicine researcher or encyclopaedia reader would take either to name the same thing. | 1.00 |
| `NARROWER` or `BROADER` | Same sense, but one scope strictly contains the other (A is narrower than B, or broader). | 0.75 |
| `OVERLAPPING` | Same sense, different emphasis. Neither contains the other and nothing contradicts. | 0.50 |
| `CONFLICTING` | Same sense, but at least one factual claim contradicts (genus, what it acts on, what condition it is used for, scope). | 0.00 |
| `DIFFERENT_SENSE` | Different referents. | 0.00 |
| `ONE_SIDE_ONLY` | Computed, never judged: one edition has no value. | not scored, counted |
| `UNSURE` | Any stage, model or human: the judge cannot tell. | missing (the rate is reported for each judge) |

Sub-fields: `same_sense` (bool), `genus_a`, `genus_b` (a few words each), `conflicts` (a list of claim pairs), `confidence` (1–5), and `rationale` (40 words at most, quoting the short spans it relied on).

**Variants: conditions (P5).** For each aligned variant pair: `BOTH_UNCONDITIONAL`, `SAME_CONDITION`, `COMPATIBLE_CONDITION`, `CONFLICTING_CONDITION`, or `CONDITIONAL_VS_NOT`. The last is assigned deterministically whenever one side has a condition and the other does not.

**Relations: type of an aligned target (P4).** `SAME_TYPE`, `COMPATIBLE_TYPE` (for example uses and requires, meronym and uses, or Sonnet `related` with any ASSOC type), `REVERSED` (hypernym against hyponym, or holonym against meronym), and `CONFLICTING_TYPE` (for example hypernym against contrast, or synonym against contrast). The judge sees both relation statements spelled out as sentences, using the system prompt's own tests ("[concept] is a kind of [target]").

**Links (L3), deterministic:** `SAME`, `BOTH_ABSTAIN`, `ABSTAIN_VS_LINK`, `DIFFERENT`. Only `DIFFERENT` goes to the judge (P6), which labels it `COMPATIBLE` (for example a product versus its software family in Wikidata, or a page that redirects) or `CONFLICTING` (a different referent).

### 4.2 Prompts

Each prompt has a version (`agree-v1`) and its SHA-256 is saved in every judgment record. The texts are below. The renderer is `agreement.py prompts`.

**System (all judge calls):**

```
You compare entries from a descriptive dictionary of nanomedicine (nanomaterials and nanocarriers,
formulations and named products, techniques and instruments, biological targets and effects). Several anonymous drafters wrote entries for the same concept independently. You judge whether
they MEAN the same thing, not whether they use the same words. Wording, length, order and style do not matter.
A longer or more fluent text is not better. Do not decide which drafter is right; decide only how their
meanings relate. Use only the texts shown and general knowledge of the concept. The dictionary describes
what each term names; it never gives preparation protocols, doses or clinical advice, so do not add any, and
do not judge whether a material, product or treatment works or is safe. Never write about an identifiable
person's health. Return only the JSON object asked for.
```

**P1, sense clustering (one call per concept):**

```
Concept: "{preferred_name}" (term form: {kind})
Other seed terms the drafters named as neighbours, for orientation only: {up to 10 neighbour names}

Each drafter states the sense of this concept:
{for each item, in random order: [S1] text, [S2] text, ...}

Group the statements so that two statements share a group if and only if they refer to the same thing in
nanomedicine or encyclopaedic usage (same referent), even if one is broader or narrower. Different
referents (for example a material versus a product made from it, a carrier versus the drug it carries, or an
abbreviation that also stands for something else) go in different groups. A statement that the term is out of scope or a duplicate forms its own group.
Return: {"groups": [["S1","S3"],["S2"]], "majority_reading": "<10 words>", "ambiguous_name": true|false,
         "note": "<=30 words"}
```

**P2, definition pair (one call per concept per pair; A and B are assigned at random):**

```
Concept: "{preferred_name}" (term form: {kind})
Definition A: {text_a}
Definition B: {text_b}

Choose exactly one label:
EQUIVALENT: same sense, same kind of thing, same essential features; either could replace the other.
A_NARROWER: same sense, A's scope is strictly inside B's.   B_NARROWER: the reverse.
OVERLAPPING: same sense, different emphasis, neither contains the other, nothing contradicts.
CONFLICTING: same sense, but some factual claim in one contradicts the other (what it is a kind of,
             what it consists of or acts on, its size range, material class or main use, where or by whom a name is used).
DIFFERENT_SENSE: they describe different things.
UNSURE: you cannot tell (counted as missing; do not use it to avoid hard items).
Return: {"label": "...", "same_sense": true|false, "genus_a": "...", "genus_b": "...",
         "conflicts": [{"a": "<span>", "b": "<span>"}], "confidence": 1-5, "rationale": "<=40 words"}
```

**P3, set alignment (variants, or relation targets; one call per concept and field, only for items left unaligned after the deterministic passes):**

```
Concept: "{preferred_name}" (term form: {kind})
Below are {variant names | relation targets} proposed by anonymous drafters, in random order, each
with an item id. {for targets: each line shows the target name and, if given, its seed concept id}
{I1 ...} {I2 ...} ...

Group items that name the SAME concept. {Variants: a variant matches only if, in nanomedicine or
encyclopaedic usage, it would name this same concept.} {Targets: ignore the relation type; group by what the target is.}
Do not group a thing with a broader or narrower thing (a PEGylated liposome is not a liposome; a gold nanorod is not a
gold nanoparticle).
Return: {"groups": [["I1","I4"],["I2"],["I3"]], "notes": {"I3": "<=20 words if unsure"}}
```

**P4, relation type for an aligned target:** both statements are shown as sentences from the gen-v2 tests, for example "A says: a liposome is a kind of nanocarrier. B says: a liposome routinely includes a phospholipid bilayer as a component." The output is `{"label": SAME_TYPE|COMPATIBLE_TYPE|REVERSED|CONFLICTING_TYPE, "confidence", "rationale"}`.

**P4 to P6** (relation type, variant condition, link compatibility) follow the same pattern, with the labels in 4.1. Their exact texts are in `judging/prompts/P4.txt` to `P6.txt`. The draft script generates only P2 requests so far.

Output is validated against a JSON schema (`schemas/agreement-judgment.schema.json`, to be added in stage 1). An invalid reply gets **one** retry with the validation error, the same rule as the kit's drafting retry. If it fails again, the item is recorded as `JUDGE_FAILED` and kept in the denominators as missing.

### 4.3 Blinding and order

- Model names, `draft_set`, `_meta`, edition folder names and `flags` are removed. Model-identifying words in the text ("Grok", "Claude", "as an AI") are masked. Every item is shown in the same neutral format, for example `Definition A: ...`.
- A and B are assigned at random for each call. In the pilot, and for a 10% sample at full scale, each pair is judged **in both orders**. The **position-flip rate** is reported, and `A_NARROWER` turning into `B_NARROWER` under the swap counts as consistent.
- In P1 and P3, items are shuffled with a seed saved in the record.
- The key that maps anonymous item IDs to models is written to a separate `keys/` file that the judge never sees. A request file never contains an edition name.
- **Style normalisation before judging.** Every text is first put into the common canonical format of section 1.1. A deterministic normaliser then (a) unifies quotes, dashes, spacing and the final full stop, (b) maps British spellings to American with a fixed word list, (c) removes stock openings ("In job postings, ...", "Refers to ...") from a fixed list, and (d) shows variants and relation targets as bare names in a fixed order. The normaliser never changes content words. Its rules are versioned along with the prompts.
- **Leak check.** On 100 pilot pairs, each judge is asked which of the two texts a Claude model wrote. If any judge does better than chance (a binomial test, p < 0.05), the blinding leaks style. The normaliser is then tightened and the check repeated. The accuracy is reported either way.

### 4.4 The judge panel, self-preference, and consistency

**Panel.** Four model judges, each run through a subscription plan Bear already has, in an agent harness. No paid API is used.

| Slot | Harness and plan | Family | Also a drafter? |
|---|---|---|---|
| `codex` | Codex (OpenAI), Bear's US$200-a-month plan | OpenAI | no |
| `claude-fable` | Claude Code, Claude Fable | Anthropic | no (same family as a drafter) |
| `claude-sonnet` | Claude Code, Claude Sonnet | Anthropic | **yes**, if it is Sonnet 5.5 (the `claude-sonnet-5-5` edition, and most of `reference`) |
| `claude-opus` | Claude Code, Claude Opus | Anthropic | no (same family as a drafter) |
| `grok-bot` (optional) | Grok | xAI | **yes** (the `grok` edition) |

**Joining, and versioned judge ids.** The table lists the intended panel, but there are no fixed seats. Any model joins with **one generic prompt** ([judging/START-HERE-AI-JUDGE.md](judging/START-HERE-AI-JUDGE.md)) and one command, `agreement.py join`. The model states its own provider, model name and exact version. `join` looks it up in [judging/drafters.tsv](judging/drafters.tsv) to decide self-exclusion (the judge never chooses it), generates its packets from the requests in a per-judge random order, and records it. Run again, `join` resumes. A model with no shell joins through the operator and judges a single paste block (`export-packet`, then `import`). Each judge is identified **with its exact model version**: judge id = `<provider>-<model name>-<version>`, for example `anthropic-claude-fable-5-2`. Provider, model name and version are **separate required fields** in `results/<judge id>/judge.json` and in every result line. The judge states the version from what its harness reports and never guesses it. A model that cannot state its version records `--version-unknown`. Its id then ends in `-version-unknown` and it is **flagged**: its results are reported separately and kept out of the primary panel until the operator confirms the version. Two versions of a model are two judges, and both are reported. A same-provider model that did not draft is flagged `same_family_as_drafter` for the self-preference check.

**Self-exclusion: drafters never judge their own edition.** The rule works item by item. A model that drafted an edition is never shown any item whose hidden key includes that edition, and `agreement.py join` enforces this when it writes the judge's packets, using the drafter table `judging/drafters.tsv` (provider, model pattern, version pattern, editions). Concretely:

- **Grok** drafted `grok`, so it never judges an item involving Grok's edition. Today that leaves it only Sonnet × reference items (2,895 of 9,544 definition requests), and in future, pairs of other editions. If Bear prefers the stricter reading ("a drafter never judges at all"), Grok simply isn't registered (decision 1 in section 12).
- **Claude Sonnet 5.5**, if the panel's Sonnet is that same model, is excluded from items involving `claude-sonnet-5-5` or `reference`. On items about other editions, it judges normally.
- **Fable and Opus** drafted nothing, so they judge everything. Because they share a family with a drafter, they are checked for self-preference below.
- **Any future edition:** add a row to `drafters.tsv` before its model joins, and the same rule applies. If the version is unknown but the provider and model match a drafter row, `join` excludes the model **and** flags it.
- **Self-judgment probe:** to measure self-preference directly, a drafter can additionally be run on its own edition's items under a separate judge id. This is an operator-only option and is not built into `join` yet. Probe labels are compared with the panel's and **never** enter the panel label.

**Aggregating the panel.** Three of the four judges are Anthropic models, so a simple majority would let one family decide. The **primary label is balanced by family**: the Claude label is the majority of the three Claude judges (or their median for the ordinal definition score); the Codex label stands alone; and the panel score is the mean of the two family scores. For nominal labels, the panel label is the one the two families agree on, and items where they disagree go to `FAMILY_SPLIT` (counted, and oversampled for humans). The **full four-judge majority** is reported next to the primary label.

**Self-preference controls:**

1. **Blinding and style normalisation** (section 4.3), with the leak check.
2. **Codex-only results** next to every panel result. Codex is the only judge outside the family of any drafter, so it is the cleanest reading.
3. **Self-preference check (difference in differences).** Each Claude judge j (Fable and Opus on every item; Sonnet through its self-judgment probe) gets a score for leniency toward the Sonnet edition, relative to Codex:
   Δ_j = [mean score_j − mean score_codex] on pairs **involving** the Sonnet edition − [the same difference] on pairs **not involving** Sonnet or the reference (which Sonnet mostly wrote).
   Today the non-Sonnet pairs are Grok grounded × Grok ungrounded in the pilot, plus any later editions. Δ_j gets a bootstrap interval. If the interval excludes 0, judge j shows self-preference (or, from the Codex side, lack of it). For the same check on alignments (P3), the outcome is the rate at which a judge merges a Sonnet target with another edition's target. For relation types (P4), it is the rate of `SAME_TYPE` when one side is Sonnet. When the correctness review (section 11.1) is added, the same check uses "supports" on Sonnet claims, where self-preference matters most.
4. **Leave one judge out.** Every main table (T3, T5) is recomputed once without each judge in turn (and without Grok, if Grok judged). A conclusion is reported as robust only if it holds every time.
5. **Agreement between judges, by family** (section 7.4). If Claude judges agree with each other much more than with Codex, the gap is reported. That gap is a family effect, not evidence that the Claude judges are right.

**Self-consistency.** Agent harnesses do not expose temperature or seeds, so repeat runs vary through order and session instead. Each judge runs R = 3 times in the pilot, each time in a fresh session with a different shuffle seed and the other A/B order. At full scale, R = 1, plus R = 3 on a 10% stratified sample. Test-retest is reported as Krippendorff's α across runs.

**Pinning.** Each batch records the judge id, provider, model name, **model version**, the model as the harness reports it, the harness and its version, the reasoning-effort setting, the plan, and the start and end time with zone (section 9.4). A batch whose identity fields differ from the judge's `judge.json` is rejected and rerun.

---

## 5. A cheap baseline next to the judge

For every definition pair and sense pair:

1. **Embedding cosine**, from one pinned open sentence-embedding model chosen from a family outside the editions. It runs on CPU in minutes for about 6k texts.
2. **Lexical baselines:** token Jaccard and ROUGE-L.

They are reported in three ways: (a) Spearman correlation with the judge's ordinal score; (b) ROC-AUC for predicting the human label "same meaning" (EQUIVALENT, NARROWER or BROADER) on the validation sample; (c) a deliberately adversarial comparison on the look-alike pairs (Java against JavaScript, Angular against AngularJS, C against C++ and C#), where high cosine with the judge saying `DIFFERENT_SENSE` shows why a judge is needed. If the baseline matches the judge as well as two humans match each other, the paper can say so and recommend the cheap method.

---

## 6. Statistics

Every interval below is a **95% bootstrap interval from 2,000 resamples of concepts** (10,000 in the pilot), because fields within one concept are correlated. Where judge runs repeat, a second level of the bootstrap draws one judge run per item, so judge noise is included. Intervals are percentile intervals, or BCa when the statistic is skewed.

### 6.1 Agreement for each field and each pair of models (works with N = 2)

For each field f and pair (m, n) over the concepts both drafted:

- **Mean agreement score** (scores from 4.1). In addition, `P(same meaning)` = the share of pairs labelled EQUIVALENT, NARROWER or BROADER, and the full label distribution.
- **Both present, one only, neither**, given as counts and shares before any agreement is computed, so that coverage and verbosity are kept separate from meaning.
- **Links:** exact agreement, plus Cohen's κ on the three-way {link, abstain, not offered} value. Where both editions link, the same-target rate is also given. (Not available for Grok against Sonnet: Sonnet did not elicit links.)
- **Basis:** for aligned claims, agreement and κ. When an edition's basis has no variance (Grok full run: all `model_knowledge`), κ is undefined. The prevalence is reported instead, with no κ.
- **Target status:** for aligned targets, the agreement on in-lexicon versus proposed_new.

### 6.2 Agreement across many models (for N ≥ 3; computed for N = 2 as well)

- **Krippendorff's α** is the main coefficient because it handles missing data (Sonnet has no credentials) and any number of raters. Here the models are the raters.
  - *Nominal α* on: link choice; the sense-cluster ID from P1 (the arbitrary cluster label for each concept is a valid nominal value, since α uses only agreement within a unit); presence or absence of each candidate relation target, over a **fixed frame** for each concept: the kit's 30 bundle neighbours plus every aligned proposed_new cluster (one unit per concept × frame member; value = the coarse axis or NONE). The frame must not be built from the union of what the editions said. A union frame guarantees that at least one rater says something for every unit, which pushes α below zero (the draft script shows this: α = −0.21 on a union frame); the coarse axis of each aligned target; and the conditional flag of each aligned variant.
  - *A semantic α* for definitions: α = 1 − D_o / D_e. Here D_o is the mean pairwise distance within a concept, with distance = 1 − score from 4.1. D_e is estimated by having the judge label a random sample of 500 **cross-concept** pairs (same kind, different concept). Without that estimate, α cannot be computed for free text.
- **Fleiss' κ**, only on the complete subset where every model drafted every unit, as a familiar comparison.
- **Gwet's AC1** next to κ and α whenever a category is very common (abstentions, "no relation"), because κ falls sharply when one category dominates even if raw agreement is high.

### 6.3 Relation and variant sets

For each concept and pair, after alignment:

- **Set F1** = 2|A∩B| / (|A| + |B|) and **Jaccard**, at three levels of strictness: (i) same target, any type; (ii) same target and same coarse axis, direction normalised; (iii) same target and same fine type (gen-v2 against gen-v2 only). For level (iii), `COMPATIBLE_TYPE` counts as a half match and is reported separately.
- **Directional coverage:** the share of m's edges that n also gives, and the reverse. With Sonnet's sparse relations, this asymmetry is the main finding, so it is reported alongside F1.
- **Empty sets:** F1(∅, ∅) is undefined. "Both empty" is reported as its own agreement rate, and F1 is averaged only over concepts where at least one edition gives relations. A sensitivity version with F1(∅, ∅) = 1 is reported too.
- Both a **macro** average (mean over concepts) and a **micro** average (pooled edges) are given, for each axis and for each fine type: synonym, hypernym, hyponym, meronym, holonym, uses, requires, certifies and contrast.
- **Reversal rate:** the share of aligned taxonomic or part-whole edges with opposite directions.
- **Graph level:** the edges are combined into one directed graph per edition. The analysis reports how often the editions share edges, the agreement on each concept's TAX_UP parent, and the cycles each edition creates.
- **Consensus gaps:** proposed_new targets that two or more editions independently propose and that align to the same cluster. These are candidates for new lexicon concepts, and the list is a useful result in its own right.

### 6.4 One score per entry

For each concept and pair: S = Σ_f w_f · a_f / Σ_f w_f, summed only over fields **both** editions elicited. Each a_f is in [0, 1].

| Field | a_f | Default weight |
|---|---|---:|
| sense | 1 if same cluster, else 0 | 0.20 |
| definition | score from 4.1 | 0.25 |
| relations | F1 at level (ii); "both empty" = 1 | 0.25 |
| variants | F1 after alignment; "both empty" = 1 | 0.10 |
| links | mean over the three sources of exact or compatible agreement | 0.15 |
| basis and target status | agreement on aligned claims | 0.05 |

A **hard gate** applies: if the sense clusters differ, S = 0 (the ungated version is reported too). S is also reported with **equal weights** and for each field left out in turn. The paper should show that no conclusion depends on the weights. For N > 2, the entry score is the mean of S over pairs, and the unanimity rate is the share of concepts where every pair has S ≥ 0.75.

### 6.5 Breakdowns

Every statistic in 6.1 to 6.4 is broken down by: **kind** (15), **broad class** (skill, ability, knowledge, language, credential), **grounded versus ungrounded** (pilot only), **trap set** versus the rest, **schema pair** (gen-v2 against gen-v2, or gen-v2 against another), and **how often the concept appears in postings** (tertiles of `observations.jsonl` counts, if available).

The trap set: Java and JavaScript; C, C++ and C#; Angular and AngularJS; Swift; R, Go and C (short names); Service orientation; the two nursing degrees; and the two Mathematics records. Differences between breakdown cells use a paired bootstrap, with Holm correction within each table. A mixed-effects logistic model, `agree ~ pair + broad_class + grounded + (1 | concept)`, is an optional robustness check.

### 6.6 The existing lexicon as a reference

The lexicon at `91312fec` is treated as an **additional edition**, not as the right answer. 95% of its entries were drafted by `claude-sonnet-5-5`, so Sonnet against the reference partly measures Sonnet agreeing with itself. The analysis reports (a) each edition's agreement with the reference, (b) agreement between editions **when both depart from the reference**, and (c) the **copy-through rate**: the share of each edition's variants and relations that already appear in the reference. The kit's bundles showed the drafter the lexicon's existing record, so (c) measures anchoring directly.

---

## 7. Is the judge right? Validation

### 7.1 Human judges: who judges what

**No file upload.** A human judges by talking to Claude Code or Codex opened in this repository. The agent acts as an interviewer, following [judging/INTERVIEWER-PROTOCOL.md](judging/INTERVIEWER-PROTOCOL.md) (AGENT-AS-INTERVIEWER). The person reads [judging/HUMAN-JUDGE-INSTRUCTIONS.md](judging/HUMAN-JUDGE-INSTRUCTIONS.md). It registers the judge, draws their sample, and shows the blinded items one at a time. It maps the judge's free-form comments to the fixed label set, reads the label back for the judge to confirm, and keeps the judge's own words verbatim in `notes`. It writes `results/<judge_id>/` in the same schema as the model judges, runs the validator, and commits under the judge's name. A judge can pause and resume at any point. The interviewing agent records labels only; it never suggests one before the judge has spoken. Its mapping is checked because every label is read back and confirmed.

**Sampling (seeded, drawn fresh for each judge at registration):**

- **Size:** about **100 items** per judge by default, or **50** if the judge prefers.
- **Strata:** field (sense, definition, alignment, relation type, link) × broad class (skill, ability, knowledge, language, credential), allocated in proportion to the request pool with at least one item per non-empty cell. Kinds are spread within each cell. **Trap concepts** are always included, at a quota of at least 10% of each sample.
- **Overlap:** about **30%** of each judge's items come from a **shared overlap pool**, assigned least-judged-first, so every overlap item gets **at least 2** human judges once enough people have registered (with a pool of 50 and 30 overlap items each, from the fourth judge on). The other **70%** are **unique** to that judge and never given to another.
- **Scale:** with 10 judges at 100 items each, that is about 1,000 human judgments. With an overlap pool of 50 items, each pool item gets about 6 judges, and there are about 700 + 50 = **750 unique items**. Pool size, sample size, overlap share and the trap quota are all settings (`agreement.py register --size --overlap --pool-size --trap-share`).
- **Reproducibility:** the judge's seed is derived from the run salt and the judge id, and recorded in the registry, so anyone can redraw the same sample.
- **Optional rare-label boost:** if model judgments already exist when a judge registers, CONFLICTING, DIFFERENT_SENSE and FAMILY_SPLIT items can be oversampled. Sampling weights are recorded, and estimates are reweighted to the population with inverse weights.

**Why this design:**

- *Judge–human agreement* needs many distinct items more than repeated ones. The 70% unique share gives about 700 items, which estimates judge–human κ to about ±0.05 overall and to about ±0.08–0.10 per field.
- *Human–human agreement* is the ceiling the judge is held to (section 7.2). The overlap pool gives every pool item several human ratings. Krippendorff's α handles that incomplete, unbalanced design directly. A pool of 50 items × about 6 raters estimates human α to about ±0.1. A larger pool (for example 100 items at about 3 raters each) narrows that interval at the cost of fewer unique items, and the setting makes the trade explicit.
- A fresh seeded sample for each judge spreads human attention across the lexicon instead of concentrating it on one fixed set. It also keeps any single judge's tastes from defining the gold standard.
- Stratification guarantees that every field and every broad class is validated, including small ones (abilities, languages), and the trap quota guarantees that the hardest cases get human eyes.
- Humans see the same blinded, style-normalised rendering as the model judges, so differences come from the judging, not from what was shown.

**Effort:** 100 items at about 1.5 to 3 minutes each is roughly **3 to 5 hours per judge**, which can be split across sessions with pause and resume.

**Pilot:** the 32 shared pilot concepts form their own pool. Bear plus at least one other judge label all of it (96 definition pairs plus the other fields). That pilot work tunes the rubric before the seeded samples above are drawn for the full run.

### 7.2 What gets reported

- **Human–human** α (and pairwise κ) on the overlap pool, before adjudication. This is the **ceiling** for the judge. Adjudication of overlap items uses the majority of the human judges, and ties go to Bear.
- **Judge–human** on every human-judged item, measured against the adjudicated label where there is one and against the single human label otherwise. This is reported for the primary panel, for Codex alone, and for each judge: κ (weighted κ for the ordinal definition scale), a confusion matrix, and precision and recall for "same meaning" and for "conflicting".
- **Acceptance rule, fixed before the full run:** the judge panel is accepted for a field if judge–human κ ≥ 0.6 **and** is no more than 0.1 below human–human. Otherwise the rubric is revised, but **only on the pilot development split**, and the validation sample is drawn fresh after the rubric is frozen.

### 7.3 Consistency within one judge

Test-retest α across R runs, and the position-flip rate (section 4.3).

### 7.4 Agreement between judges

Pairwise κ for every pair of judges, and Fleiss' κ across the four; agreement within the Claude family against agreement between Codex and the Claude judges; the `FAMILY_SPLIT` rate; and the self-preference check of section 4.4.

---

## 8. Plan in stages (pilot first)

1. **Stage 0: freeze and normalise.** Record the commit SHA of each edition, run the adapters, and produce the coverage tables, the crosswalk audit and the deterministic alignments (ID and name). No model calls. *(The skeleton script does this now.)*
2. **Stage 1: pilot.** The 32 shared pilot concepts, plus the reference, plus Grok grounded against Grok ungrounded. Model judge panel (section 4.4) with R = 3, both orders, and the leak check. Full human annotation. Tune the rubric on half the concepts (development) and test it on the other half.
3. **Stage 2: freeze.** Prompt version `agree-v1` is locked. The analysis plan (this page, with its weights and acceptance rule) is committed with a tag **before** the full run.
4. **Stage 3: full scale.** The 2,895 shared concepts, plus 855 Grok-only credentials (coverage and reference comparison only). R = 1 plus a 10% sample at R = 3. Human judges register and are interviewed (section 7.1).
5. **Stage 4: as more editions arrive.** When another model hands in an edition, it gets an adapter; only the new pairs are judged; and α and Fleiss' κ are recomputed. Pairwise calls grow as N(N − 1)/2, while the clustering calls (P1, P3) stay at one per concept.
6. **Stage 5: paper.** Tables and figures (section 10.2).

### 8.4 Grounded against ungrounded

For the pilot, there are two contrasts: (a) **within a model**, Grok grounded against Grok ungrounded, which shows how much the sources change the entry; and (b) **across models**, whether cross-model agreement is higher when both are grounded. (b) needs a second gen-v2 grounded pilot edition. That is the main reason to have other models run the kit as it is.

---

## 9. Run plan (subscription agents, no API)

There is **no dollar budget**. All judging runs through the plans Bear already has: Codex (OpenAI, US$200 a month) and Claude Code (Fable, Sonnet, Opus). The plans are flat-rate, so the limits are the plans' usage windows and wall-clock time. Nothing is billed per token.

### 9.1 Requests and results are files, so any agent can do the work

- `agreement.py run` writes `requests/<stage>/batch-NNNN.jsonl`. Each batch holds 50 requests, and each line has `request_id`, `system`, `user` and `prompt_sha256`, with no edition names. A batch is the unit of work.
- `agreement.py join` gives each model judge its own copy, `packets/<judge id>/batch-NNNN.jsonl`, with self-exclusion from `drafters.tsv` applied and its own seeded order (section 4.4). Self-exclusion works without the private key, using the obfuscated index `requests/exclusions.json`.
- A judge session gets one instruction ([judging/AI-JUDGE-INSTRUCTIONS.md](judging/AI-JUDGE-INSTRUCTIONS.md)): read its packet batch; answer each line independently, following its own system and user text; write one JSON line per request to `results/<judge_id>/<stage>/batch-NNNN.jsonl`; then run `agreement.py validate`.
- **One fresh session per batch.** No context carries between batches, which keeps judgments independent and stops the drift that builds up in long sessions. Within a batch, the session must not compare lines with each other.
- Headless invocation, for example `codex exec -m <model> "<the generic prompt>"` or `claude -p --model <model> "<...>"`, the same way `run_batch.sh` already drives `claude -p`. Interactive sessions work too: the prompt is the same either way.
- `manifest.json` lists every batch × judge × run with a status (`todo`, `done`, `invalid`, `rerun`). A runner picks the next `todo`, so a stopped run resumes where it left off. Invalid replies get one retry (section 4.2).

### 9.2 Request and session counts (rough)

About 3 + N(N − 1)/2 requests per concept, where N counts editions plus the reference, plus order swaps and repeats.

| Scope | Requests per judge | Batches (= sessions) per judge, at 50 per batch | Four judges |
|---|---:|---:|---:|
| Pilot, 32 concepts (Grok ungrounded, Grok grounded, Sonnet, reference; both orders; R = 3) | about 1,500 | about 30 | about 120 sessions |
| Full, 2,895 shared concepts today (Grok, Sonnet, reference; R = 1 plus 10% at R = 3) | about 21,000 | about 420 | about 1,700 sessions |
| Full, 3,754 concepts, 5 editions | about 55,000 | about 1,100 | about 4,400 sessions |

Batches of 100 halve the session counts if a harness handles them reliably. The pilot shows which size works.

### 9.3 Rate limits

- Subscription plans meter usage in rolling windows (for example over a few hours, plus a weekly cap). The current limits are whatever the plan shows at the time; this page does not assume a number. The runner runs a small number of parallel sessions per plan (for example 2 to 4). When a session hits a limit, it marks the batch `todo` again and waits for the window to reset.
- Codex and Claude Code have separate limits, so the four judges can run at the same time. The three Claude judges share one plan's limits, so the Claude side is the slower one. It is scheduled round-robin across Fable, Sonnet and Opus, so that no judge finishes far ahead of the others and model updates hit all three at about the same point.
- At a rough 5 to 10 minutes per 50-request batch, the full run today is about 35 to 70 hours of session time per judge. Spread across usage windows, that is one to three weeks of calendar time. The pilot fits in a day or two.
- Usage spent on judging competes with Bear's other work on the same plans. The runner has a quiet-hours setting, and full-scale stages are scheduled for when the plans are otherwise idle.

### 9.4 Pinning and recording the model

- Each judge's model is set explicitly at launch (`-m` / `--model`) and never left to a default. In its first session, the judge runs `agreement.py join` with its provider, model name, **exact version** (or `--version-unknown`, which flags it) and the model string the harness reports. That writes `results/<judge id>/judge.json` and fixes the versioned judge id. At the start of each batch, the session writes a header line: `{"_batch": "...", "judge_id": "anthropic-claude-fable-5-2", "provider": "anthropic", "model_name": "claude-fable", "model_version": "5.2", "model_reported": "...", "harness": "codex|claude-code", "harness_version": "...", "effort": "...", "plan": "...", "started_at": "...-05:00"}`. It writes `finished_at` at the end.
- `validate` rejects a batch whose provider, model name, version or `model_reported` differs from `judge.json`. A new version means a new judge id, never an edit to the old one. If a provider changes the model behind an unchanged name and version partway through, the batches before and after are given different `judge_version` values and tested for a shift (on the repeated 10% sample).
- Because the model behind a hosted name can change, exact reruns are not guaranteed. Every request, result line and raw reply hash is committed, so the analysis itself can always be recomputed.

The embedding baseline and all the statistics run on CPU in minutes. The human interviews in 7.1 take the most time.

---

## 10. Outputs

### 10.1 Files (under `agreement/<run>/`, committed on a branch)

- `canonical/<edition>.jsonl`: one canonical entry per concept (section 1.1), with `edition`, `edition_sha`, `schema`, `run`.
- `coverage.csv`: concept_id, kind, broad_class, and one column per edition (`drafted`, `missing`, `out_of_scope`).
- `alignment/{targets,variants}.jsonl`: `{concept_id, field, cluster_key, members: [{edition, item_index, text, target_id}], resolved_by: id|name|judge|human, judgment_id}`.
- `keys/anon.jsonl`: `{request_id, A, B}`, plus `keys/request-id-secret.txt` (request ids are keyed with a secret, so nobody can recompute them from concept and edition names). These go in `--private-dir` and are **never committed** to the public repo. `stats` and `register` take `--keys PATH`. `canonical/`, `tables/` and `coverage.csv` are private too, because they name editions.
- `requests/<stage>/batch-NNNN.jsonl`: `{request_id, stage: P1..P6, concept_id, field, kind, broad_class, trap, prompt_version, prompt_sha256, order_seed, system, user}`. Only `system` and `user` are shown to a judge.
- `judges.json`: human judges (seed, sample settings). `results/<judge id>/judge.json`: a model judge's identity, written by `join`, with its flags and a self-exclusion summary. `judging/drafters.tsv`: which models drafted which editions. `requests/exclusions.json`: the obfuscated self-exclusion index. `results/<judge id>/judge.json` holds (provider, model name, **model version** or the unknown flag, model string as reported, harness and its version).
- `humans/registry.jsonl`, `humans/overlap-pool.jsonl`, `humans/<judge_id>/sample.jsonl`, `humans/<judge_id>/progress.json`: registration, the seeded sample and the resume point.
- `results/<judge_id>/<stage>/batch-NNNN.jsonl` for model judges, or `results/<judge_id>/judgments.jsonl` for humans. **The same line schema for both**, one line per judgment:

```json
{"judgment_id": "j-000123", "request_id": "r-000123", "stage": "P2", "concept_id": "sh6x1wmacn",
 "field": "definition",
 "judge": {"id": "openai-codex-5-3", "type": "model", "provider": "openai", "model_name": "codex", "model_version": "5.3",
           "model_reported": "...", "harness": "codex", "judge_version": 1},
 "run_index": 0, "order_seed": 11, "prompt_version": "agree-v1", "prompt_sha256": "...",
 "label": "A_NARROWER",
 "fields": {"same_sense": true, "genus_a": "...", "genus_b": "...", "conflicts": [], "confidence": 4,
            "rationale": "..."},
 "notes": null, "confirmed": null,
 "valid": true, "attempts": 1, "raw_sha256": "...", "created_at": "2026-12-01T10:00:00-05:00"}
```

  A human line has `judge.type = "human"`, `judge.name`, the judge's words verbatim in `notes`, and `confirmed: true` once the judge has accepted the read-back label. The model-only fields (`raw_sha256`, `attempts`) are null for humans. The pairing of A and B with editions lives only in `keys/`, and the statistics step joins it in.
- `adjudicated.jsonl`: the resolved labels for overlap items.
- `tables/*.csv`: one file per table below, each with its bootstrap intervals.

### 10.2 Tables and figures for the paper

| # | Table |
|---|---|
| T1 | Coverage by edition × broad class × kind, with the intersection |
| T2 | Schema crosswalk: which fields each edition elicits |
| T3 | Agreement per field: pairwise score, P(same meaning), α, Fleiss' κ, AC1, with 95% intervals |
| T4 | Model × model matrix, one per field |
| T5 | Relation set F1 at three levels of strictness, per axis and per fine type; directional coverage; reversal rate |
| T6 | Breakdowns by broad class and kind |
| T7 | Pilot: grounded against ungrounded |
| T8 | Trap concepts, case by case |
| T9 | Judge validation: human–human, judge–human, confusion matrices |
| T10 | Judge test-retest, position flips, agreement between judges |
| T11 | Embedding and lexical baselines compared with the judge and with humans |
| T12 | Consensus gaps: proposed_new targets proposed by two or more editions |

| # | Figure |
|---|---|
| F1 | UpSet plot of coverage |
| F2 | Heatmaps of model × field agreement |
| F3 | Definition labels per pair (stacked bars) |
| F4 | Forest plot of agreement by kind |
| F5 | Embedding cosine by human label (box plots) |
| F6 | Distribution of the entry score, gated and ungated |
| F7 | Confusion of relation types on aligned targets (Sankey or matrix) |

---

## 11. Threats to validity

1. **Agreement is not correctness.** Two models can agree on the same wrong claim, especially from shared pretraining (Wikipedia, O\*NET). This analysis is therefore paired with the correctness verdicts in `reviews/BRIEF.md` on the same human sample, and the paper reports "agree and correct", "agree and wrong" and "disagree" separately.
2. **A shared anchor.** Both drafting routes could see the lexicon's existing record (the kit's bundles include it), and most of that record was written by Sonnet. This inflates agreement. Mitigation: the copy-through rate and agreement conditional on departing from the reference (section 6.6).
3. **Model is confounded with schema and prompt.** Grok used the kit (gen-v2) and Sonnet used its own schema and instructions. A difference between them is therefore model **plus** procedure. The coarse-axis comparison reduces this but does not remove it. The fix is for each model to also run the kit as it is (stage 4).
4. **Differences in procedure.** Grok drafted every concept in one session rather than a fresh chat per concept (recorded in its RUN.md). The Sonnet model label is still awaiting the user's confirmation (its RUN.md). Both are recorded as edition covariates.
5. **Judge bias:** self-preference, because three judges are Anthropic models and one of them may be the same model as a drafter (handled by blinding, style normalisation, the leak check, Codex-only results, family-balanced aggregation, the difference-in-differences check and leave-one-judge-out; section 4.4); family-level shared blind spots, which balancing by family reduces but cannot remove with only two families; favouring longer or more fluent text, position bias (both orders tested), and leniency (labelling things OVERLAPPING too readily). Measured in 7.2 to 7.4.
6. **Alignment errors propagate.** An over-eager merge in P3 inflates set F1. Mitigation: deterministic passes first, a conservative prompt ("not broader or narrower"), and human checks on 10% of the meaning-based alignments.
7. **Ambiguity in the labels and the rubric.** NARROWER against OVERLAPPING is a fuzzy line. The human–human ceiling measures how fuzzy, and a sensitivity analysis merges them.
8. **Prevalence and sparsity.** Mostly empty fields (Sonnet's relations) give paradoxical κ values. Presence, AC1 and conditional agreement are reported separately (section 6.1).
9. **Concepts are not independent.** Look-alike and near-duplicate concepts are related, and bootstrap resampling by concept understates the uncertainty for them. A sensitivity check resamples families of related concepts (clusters of trap concepts).
10. **Coverage is selected.** The overlap excludes credentials, so the result is not about the whole lexicon. Credential agreement must wait for a second edition that covers credentials.
11. **Blinding by instruction.** Packets and requests are public files in this repo. A judge that compared its packet with another judge's (for example `grok-bot`'s, which holds only Sonnet × reference items) could infer which editions are paired. Judges are told to open only their own folders, and the leak check (4.3) would catch systematic unblinding. A stricter setup would hand each judge its packet privately.
11. **Drift and reproducibility.** Hosted judge models change. Subscription harnesses report a model name but may change what sits behind it. Batches are pinned and stamped (section 9.4), shifts are tested on the repeated sample, and every request and reply is committed.
12. **Many comparisons.** There are many fields × breakdowns × pairs. A short list of primary outcomes is fixed in advance (T3 per field and T5 at level (ii)), and everything else is exploratory with Holm correction.

---

## 12. Decisions for Bear

1. **Which models to invite** as drafters and as judges. `drafters.tsv` has no rows yet; add one per edition before any judge joins. The model that wrote the initial lexicon is not recorded, so no judge can be excluded from `legacy` items on that ground; say which model it was if you know.
2. **Human judges:** who they are, and the settings (default: 100 items, 30% overlap, a pool of 50, a 10% trap quota). Background in nanomedicine or materials science is not required, since the task compares meanings, but the panel's background should be recorded.
3. **Weights and the hard gate** for the entry score, and the acceptance threshold (κ ≥ 0.6 and within 0.1 of human–human).
4. **Scope agreement as a primary outcome?** Default: scope (entry / out-of-scope / duplicate) is reported per pair with AC1 and listed per seed, but is not part of the entry score.
5. **Trap list:** confirm or replace the draft `TRAP_IDS` (see 1.2).
6. **Whether a reviewed `lexicon/entries.jsonl` counts as an edition** in α once it exists (default: reported separately, not counted).
7. **Scheduling and batch size** (50 or 100 requests per session), settled in the pilot.
8. **Human worked examples:** write the worked examples left as placeholders in [judging/HUMAN-JUDGE-INSTRUCTIONS.md](judging/HUMAN-JUDGE-INSTRUCTIONS.md).
