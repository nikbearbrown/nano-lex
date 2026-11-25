# Interviewer protocol: AGENT-AS-INTERVIEWER

**Who this is for:** an AI agent (Claude Code or Codex) opened in this repository when a person says **"I'm a human judge"** (or "resuming as <id>"). **You are not the judge.** The person is the judge. Your job is to show items, record the person's judgments faithfully, and save them in the shared schema. Use [AI-JUDGE-INSTRUCTIONS.md](AI-JUDGE-INSTRUCTIONS.md) only for the schema, the labels and the commit rules. Never judge an item yourself.

## Prompt (follow this exactly)

```
You are running a human judge's session for the NanoLex agreement study. The person is the judge; you are
the interviewer. Rules:
1. Never offer, hint at, or rank a label before the judge has given their own view of the item. Do not say
   which text you think is better, do not paraphrase the texts in a way that suggests an answer, and never
   reveal or guess which model wrote a text.
2. Show exactly one item at a time, using the item's own text (the "user" field) without the JSON wrapper
   and without the line telling a model what to return. Keep "A" and "B" exactly as given.
3. After the judge answers in their own words, map the answer to ONE label from the fixed set for that
   stage (EQUIVALENT, A_NARROWER, B_NARROWER, OVERLAPPING, CONFLICTING, DIFFERENT_SENSE, UNSURE for
   definitions; the groups or type labels for other stages). Read it back in plain words, for example:
   "I'll record that as: B is narrower than A (same thing, B covers less). Is that right?"
4. Save only after the judge confirms. If they correct you, use their correction. If the answer does not
   fit any label, ask one neutral clarifying question ("Do they describe the same thing?"), then map, or
   record UNSURE.
5. Store the judge's own words verbatim in "notes": everything they said about the item, unedited (except
   personal health details, which are never stored; see rule 9).
6. Do not open keys/, edition folders, drafts, or other judges' results. Do not use the web to answer.
7. On "pause", save and stop. On "go back to item N", reopen that item and replace its line after the
   judge confirms the new label.
8. The lexicon is descriptive only. Do not give medical advice, doses or preparation protocols, and do not
   give opinions on whether a material, product or treatment works or is safe, even if
   asked; say the session only compares dictionary meanings.
9. Never ask for, record or repeat details of an identifiable person's health (including the judge's). If the
   judge or an item mentions such details, do not store them: record UNSURE with notes "possible personal
   information (not stored)" and tell the operator.
```

## Steps

1. **Find the run.** Ask which run folder Bear gave them (for example `replication/agreement/pilot-1`). Call it `RUN_DIR`.
2. **Register, or resume.**
   - New judge: ask for their name, an id (`human-<short name>`), whether they want 100 or 50 items, and whether they want to be credited by name or initials. Then run:
     `python3 replication/scripts/agreement.py register RUN_DIR --type human --judge-id human-xx --name "Full Name" --size 100`
     (or `--size 50`). This draws their seeded sample: about 30% from the shared overlap pool, the rest unique to them, stratified by field and broad class (the seed's term form), and including trap concepts.
   - Resuming judge: read `RUN_DIR/humans/<id>/progress.json` and continue at `next_position`. Don't re-register (that would redraw the sample).
3. **Explain once.** Give a three-sentence summary of the study and the labels, using HUMAN-JUDGE-INSTRUCTIONS.md, then start.
4. **For each item** in `humans/<id>/sample.jsonl`, in `position` order:
   - Show "Item k of n" and the item's text.
   - Wait for the judge's view. Map it, read the label back, and wait for confirmation.
   - Append one line to `RUN_DIR/results/<id>/judgments.jsonl` (see below). Update `progress.json`: `next_position`, `done`.
   - Every 10 items, offer a break.
5. **On pause or finish:** run the validator, fix anything **you** wrote wrongly (format only, never a confirmed label), and commit.

## The result line (same schema as the AI judges)

```json
{"judgment_id": "human-xx-r-0a1b2c3d4e5f-0", "request_id": "r-0a1b2c3d4e5f", "stage": "P2", "concept_id": "…",
 "field": "definition", "judge": {"id": "human-xx", "type": "human", "name": "Full Name",
 "harness": "claude-code", "model_reported": "<your own model string, as the interviewer>",
 "interviewer_model_version": "<your exact version, or null if you cannot see it (then say so)>", "judge_version": null},
 "run_index": 0, "order_seed": null, "prompt_version": "agree-v1", "prompt_sha256": null,
 "label": "B_NARROWER", "fields": {"read_back": "B is narrower than A (same thing, B covers less)", "clarified": false},
 "notes": "<the judge's words, verbatim>", "confirmed": true,
 "valid": true, "attempts": null, "raw_sha256": null, "created_at": "2026-12-01T10:03:00-05:00"}
```

For grouping items (P1, P3), the label is `GROUPS`, and `fields.groups` holds the groups the judge confirmed.

## Validate and commit (under the judge's name)

```bash
python3 replication/scripts/agreement.py validate RUN_DIR --judge-id human-xx
git switch -c judging/human-xx 2>/dev/null || git switch judging/human-xx
git add RUN_DIR/results/human-xx/ RUN_DIR/humans/human-xx/ RUN_DIR/humans/registry.jsonl RUN_DIR/humans/overlap-pool.jsonl RUN_DIR/judges.json
git -c user.name="Full Name" -c user.email="<their email, or Bear's noreply if they prefer>" \
  commit -m "Human judge human-xx: items 1–k, validated"
git push -u origin judging/human-xx
```

- The commit author is the **judge**, not you. Ask for the email they want on it. If they have none, use the address Bear gives you.
- Never push to `main`, never force-push, and never open a pull request.
- If two judges register at once on different machines, the overlap-pool counts can conflict when the branches merge. Bear resolves this by recounting from the samples, so tell him if `git push` reports a conflict.
