#!/usr/bin/env python3
"""Blindness check: does an independent edition share wording with the initial NanoLex? Maintainers only.

Usage: python3 replication/scripts/leak_check.py LEGACY_EDITION.jsonl DRAFTS.jsonl [--n 8]

LEGACY_EDITION.jsonl is the private output of legacy_to_edition.py. A draft definition that shares a run of N or
more consecutive words (default 8) with ANY initial-lexicon definition is listed. Shared wording does not prove
that a drafter saw the initial lexicon (two texts can both echo a common source), so every hit is read by a person
before an edition is admitted to, or kept out of, the agreement study. Exit 1 if there is any hit.
"""
import json, re, sys

def grams(text, n):
    w = re.findall(r"\w+", (text or "").lower())
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}

def main():
    legacy_path, draft_path = sys.argv[1:3]
    n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 8
    index = {}
    for line in open(legacy_path, encoding="utf-8"):
        if line.strip():
            e = json.loads(line)
            for g in grams(e["definition"], n): index.setdefault(g, e["concept_id"])
    hits = total = 0
    for line in open(draft_path, encoding="utf-8"):
        if not line.strip(): continue
        d = json.loads(line); total += 1
        shared = sorted(g for g in grams(d.get("definition", {}).get("text"), n) if g in index)
        if shared:
            hits += 1
            same = index[shared[0]] == d["concept_id"]
            print(f"{d['concept_id']}\t{'same seed' if same else 'seed ' + index[shared[0]]}\t{shared[0]}")
    print(f"{hits}/{total} draft definitions share {n}+ consecutive words with the initial lexicon")
    return 1 if hits else 0

if __name__ == "__main__":
    sys.exit(main())
