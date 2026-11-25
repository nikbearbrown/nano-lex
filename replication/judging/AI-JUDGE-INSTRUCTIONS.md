# Instructions for AI judges

**For:** any language model asked to judge: Codex, Claude Code, Grok, a chat window, or anything later. **Not for:** an agent running a human judge's session. That agent follows [INTERVIEWER-PROTOCOL.md](INTERVIEWER-PROTOCOL.md).

You are one judge on a panel. Each item shows you two anonymous entries for the same concept of the NanoLex nanomedicine lexicon (one seed of [data/seeds.tsv](../../data/seeds.tsv), identified by its `concept_id`, `nanolex:<NNNN>`), written independently by different language models. You decide how far they **mean** the same thing. You do not decide which one is right. The study is described in [../AGREEMENT-METHOD.md](../AGREEMENT-METHOD.md).

All judging runs through the subscription plan in your harness. Never call a paid API. `RUN_DIR` is the run folder you were given, for example `replication/agreement/pilot-test` (not built yet; Bear names it when the editions are frozen).

## Domain content rules (descriptive only; no protocols or advice)

These rules apply to every judge, model or human, on top of everything else here. They restate the repository's domain rule ([../instructions.md](../instructions.md)): say what the term names in nanomedicine at a high level; say when a name is a brand, an abbreviation or a spelling variant of another term; give no preparation or synthesis protocols, doses, clinical advice or patient-specific guidance; make no efficacy or safety claim that a cited source does not state.

- **Descriptive only.** Judge only whether two entries mean the same thing. Never add, suggest or correct how a material is made, loaded, dosed or given, and do not judge whether a material, product or treatment works or is safe. An entry that reports a source's regulatory or evidence status ("approved for ovarian cancer") is compared as a claim like any other.
- **Brands, abbreviations and spelling variants.** Entries state when a name is a brand, an abbreviation with more than one expansion, or a hyphen or spelling variant of another seed. Treat that condition as part of the variant's meaning when you compare variants (P5).
- **No personal details.** Never paste, request or write details of an identifiable person's health, including your own, a judge's or someone you know, in a result, note or rationale. If an item seems to contain such details, label it `UNSURE`, write `"notes": "possible personal information"`, and tell the operator. Do not repeat it.
- **No advice.** If a person in a session asks for medical or dosing advice, do not give it inside the study; say that the study only compares dictionary meanings.
- **Abstentions are not judged here.** An edition may flag a seed as out of scope or as a duplicate (a spelling variant of another seed) instead of writing an entry. `agreement.py run` compares those scope decisions deterministically and never sends them to definition judges. Treat every definition you do see as an entry.


## 1. Who you are: provider, model name, exact version

Work out three things **from your harness or system information** (for example `/model`, `/status`, the model line in your session information, or the model picker), never from memory or by guessing:

- **provider:** the company, for example `openai`, `anthropic`, `xai` or `google`;
- **model name:** the model without the provider and without the version, for example `claude-fable` or `gpt-sol`;
- **version:** exactly as stated, for example `5.2`. If you cannot see an exact version, you **must say so** and use `--version-unknown`. Your run is then **flagged**: reported separately and kept out of the primary panel until the operator confirms the version.

Also note the model string exactly as the harness shows it (`--model-reported`).

Your **judge id** is `<provider>-<model name>-<version>`, for example `anthropic-claude-fable-5-2`. The script builds it, and you never type it by hand. Results, branch and commit messages all use it.

## 2. Join (or resume): one command

```bash
git fetch origin
JID=$(python3 replication/scripts/agreement.py judge-id RUN_DIR --provider P --model-name M --version V)   # or --version-unknown
git switch "judging/$JID" 2>/dev/null || git switch -c "judging/$JID" origin/main
python3 replication/scripts/agreement.py join RUN_DIR --provider P --model-name M --version V \
  --model-reported "<as shown>" --harness "<codex | claude-code | ...>" --harness-version "<its --version>"
```

`join` does everything that decides **what you see**, so you never choose it yourself:

- It builds your judge id.
- **Self-exclusion:** it looks you up in [drafters.tsv](drafters.tsv), the table of which models drafted which editions, and removes every item involving an edition you drafted. No edition is registered yet; a row is added for each drafter before it joins. A model of the same provider but a different model or version is not excluded. It is flagged `same_family_as_drafter`, so the analysis can check it for self-preference. If your version is unknown but your provider and model match a drafter, you are excluded **and** flagged.
- It writes your packets, `RUN_DIR/packets/<judge id>/batch-NNNN.jsonl` (50 items each, in a random order of your own), and records you in `RUN_DIR/results/<judge id>/judge.json`.
- If you already joined, it **resumes**: it changes nothing and prints how many batches are done and which comes next.

It prints, for example:

```
judge id: anthropic-claude-fable-5-2  (joined)   ** FLAGGED: same_family_as_drafter **
items: 150 in 3 batches (packets/anthropic-claude-fable-5-2/); done: 0; next: batch-0001.jsonl
branch: judging/anthropic-claude-fable-5-2
```

If it says a different identity is already recorded, stop and tell the operator. Never edit `judge.json`, packets or `drafters.tsv` by hand: the validator regenerates your packets from your identity and rejects any difference.

## 3. Read a packet

Judge **only the `next` batch** that `join` printed, in a fresh session, and only that batch. Each line of the packet holds:

```json
{"request_id": "r-…", "stage": "P2", "concept_id": "…", "prompt_version": "agree-v1", "prompt_sha256": "…",
 "system": "<the judge system prompt>", "user": "<this item's question>"}
```

- Treat `system` as your instructions and `user` as the item. Answer the `user` text as `system` directs.
- Answer **each line on its own**. Don't look back at earlier lines or compare items with each other, and keep no running tallies.
- Open **only** `packets/<judge id>/` and `results/<judge id>/`. Do not open `requests/` (including `requests/exclusions.json`), other judges' packets or results, any edition's drafts or run folder, any branch or folder holding drafts, other `judging/*` branches, or `lexicon/entries.jsonl` once it exists. The key that unblinds A and B is not in this repository at all. Do not search the web.

**The script generates stage P2 (definition pairs) only, for now.** Requests are written only for seeds where both editions wrote an entry. Variants (aliases/synonyms) and relations are compared deterministically per `concept_id` by `agreement.py run` (exact-normalised variant F1, relation F1 by target and by axis, conditional-flag agreement), and so are scope decisions (entry, out-of-scope, duplicate). The P1 and P3–P6 prompts exist (`prompts/`), but the script doesn't generate those requests yet. A model that drafted an edition gets only pairs that don't involve it.

## 4. The judging prompt and rubric (exact)

The system prompt (also in `prompts/system.txt`, and already inside every request):

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

The labels for each stage:

| Stage | Question | Labels |
|---|---|---|
| P1 | Group sense statements by referent | `fields.groups` (for example `[["S1","S3"],["S2"]]`), plus `majority_reading`, `ambiguous_name`; label `GROUPS` |
| P2 | Two definitions | `EQUIVALENT`, `A_NARROWER`, `B_NARROWER`, `OVERLAPPING`, `CONFLICTING`, `DIFFERENT_SENSE` |
| P3 | Group variants or relation targets that name the same concept | `fields.groups`; label `GROUPS` |
| P4 | Relation types on one aligned target | `SAME_TYPE`, `COMPATIBLE_TYPE`, `REVERSED`, `CONFLICTING_TYPE` |
| P5 | Conditions on one aligned variant | `SAME_CONDITION`, `COMPATIBLE_CONDITION`, `CONFLICTING_CONDITION` |
| P6 | Two different links | `COMPATIBLE`, `CONFLICTING` |
| any | You cannot tell | `UNSURE` (counted as missing; use it honestly, not to avoid hard items) |

P2 definitions:

- **EQUIVALENT:** same sense, same kind of thing, same essential features; either could replace the other.
- **A_NARROWER** or **B_NARROWER:** same sense, but one's scope lies strictly inside the other's.
- **OVERLAPPING:** same sense, different emphasis; neither contains the other and nothing contradicts.
- **CONFLICTING:** same sense, but a factual claim in one contradicts the other (what it is a kind of, what it consists of or acts on, its size range, material class or main use, where or by whom a name is used).
- **DIFFERENT_SENSE:** they describe different things (for example *SLN* as solid lipid nanoparticle against *SLN* as sentinel lymph node; or a carrier against the drug it carries).

The P2 sub-fields go in `fields`: `same_sense`, `genus_a`, `genus_b`, `conflicts` (a list of `{a, b}` spans), `confidence` (1–5) and `rationale` (40 words at most).

Hard cases: two short texts that differ only in length or style are `EQUIVALENT`. A practice against a product used in it ("recreational use of nitrous oxide" against "a cartridge of nitrous oxide") is `DIFFERENT_SENSE`, never overlapping. A definition that also reports a historical or legal status the other omits ("now banned in many countries") is `NARROWER` or `OVERLAPPING`, not `CONFLICTING`, unless the two statuses contradict. If one definition adds a claim the other simply leaves out, that is `NARROWER` (or `OVERLAPPING`), not `CONFLICTING`. `CONFLICTING` needs a real contradiction.

## 5. Write your results

For `packets/<judge id>/batch-0001.jsonl`, write `results/<judge id>/batch-0001.jsonl`. Copy `provider`, `model_name`, `model_version` and `model_reported` from `results/<judge id>/judge.json`. Start with **one header line**:

```json
{"_batch": "batch-0001", "judge_id": "anthropic-claude-fable-5-2", "provider": "anthropic", "model_name": "claude-fable",
 "model_version": "5.2", "model_reported": "<exactly as in judge.json>", "harness": "claude-code",
 "harness_version": "<claude --version>", "effort": "<reasoning effort or null>", "plan": "<plan name>",
 "started_at": "2026-12-01T10:00:00-05:00"}
```

Then write one line per request, in packet order, following [judgment.schema.json](judgment.schema.json):

```json
{"judgment_id": "anthropic-claude-fable-5-2-r-0a1b2c3d4e5f-0", "request_id": "r-0a1b2c3d4e5f", "stage": "P2",
 "concept_id": "nanolex:0298", "field": "definition",
 "judge": {"id": "anthropic-claude-fable-5-2", "type": "model", "provider": "anthropic", "model_name": "claude-fable",
           "model_version": "5.2", "model_reported": "…", "harness": "claude-code", "judge_version": 1},
 "run_index": 0, "order_seed": null, "prompt_version": "agree-v1", "prompt_sha256": "<copied from the request>",
 "label": "A_NARROWER", "fields": {"same_sense": true, "genus_a": "lipid vesicle",
 "genus_b": "drug carrier", "conflicts": [], "confidence": 4, "rationale": "…"},
 "notes": null, "confirmed": null, "valid": true, "attempts": 1, "raw_sha256": null,
 "created_at": "2026-12-01T10:03:00-05:00"}
```

- `judgment_id` is `<judge id>-<request_id>-<run_index>`. `model_version` is null only if you joined with `--version-unknown`.
- End the file with the header line again, adding `"finished_at"`. The validator rejects a batch without it, and it also rejects a batch that leaves any packet request unanswered.
- If a reply doesn't fit the schema, fix it once. If it still doesn't fit, write `"label": "UNSURE", "valid": false`.

## 6. Validate

```bash
python3 replication/scripts/agreement.py validate RUN_DIR --judge-id "$JID"
```

Fix every error it reports. The common errors: a label not allowed for that stage, a `request_id` that isn't in your packets, a duplicate, an identity field that differs from `judge.json`, or packets that differ from what `join` generates. A `WARNING FLAGGED` line is allowed, and it's reported as such. **A batch that fails validation is not handed in.**

## 7. Commit and push

```bash
git add RUN_DIR/results/$JID/ RUN_DIR/packets/$JID/
git -c user.name=nikbearbrown -c user.email=610338+nikbearbrown@users.noreply.github.com \
  commit -m "Judge $JID: batch NNNN, validated"
git push -u origin "judging/$JID"
```

- Stage only your own `results/<judge id>/` and `packets/<judge id>/`. Never push to `main`, never force-push, and never open or merge a pull request.

## 8. Rate limits and resuming

If your plan's usage limit stops you mid-batch, don't hand in a partial batch. In a new session, paste the same kickoff again. `join` resumes and names the next batch, and you redo that batch from its first line.

## 9. No shell? The chat-only route

A model in a plain chat window can still judge. The **operator** runs the commands, and the model only reads one paste block and replies.

1. **Identify:** paste the generic prompt from [START-HERE-AI-JUDGE.md](START-HERE-AI-JUDGE.md). A model without a shell replies `NO SHELL`, followed by its provider, model name, exact version (or "version unknown") and the model string it sees.
2. **Join for it:** `agreement.py join RUN_DIR --provider P --model-name M --version V --model-reported "..." --harness chat` (or `--version-unknown`). Self-exclusion is applied exactly as above.
3. **Export:** `agreement.py export-packet RUN_DIR --judge-id <judge id> --write packet.txt`. This writes one self-contained block, with the instructions, every item, and the exact reply format, for the next unfinished batch (`--batch N` picks another).
4. **Paste** `packet.txt` into the same chat. The model replies with one `jsonl` block: one line per item, `{"request_id", "label", "fields"}`.
5. **Import:** save the reply to `reply.txt`, then run `agreement.py import RUN_DIR --judge-id <judge id> --reply reply.txt`. It checks that every item is answered exactly once with an allowed label, fills in the identity and schema fields from `judge.json`, writes `results/<judge id>/batch-NNNN.jsonl` and runs the validator. If anything is missing or invalid, it stores nothing and lists the problems: ask the model again, or fix only formatting.
6. **Commit** as in section 7, on `judging/<judge id>`.
