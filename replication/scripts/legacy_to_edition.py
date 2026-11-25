#!/usr/bin/env python3
"""Turn the initial NanoLex markdown files into one edition for the agreement study. Maintainers only.

Usage: python3 replication/scripts/legacy_to_edition.py INITIAL_LEXICON_DIR OUT.jsonl

INITIAL_LEXICON_DIR is the Data/ folder of the private archive nikbearbrown/nano-lex-initial-2025. OUT.jsonl must be outside this
repository: it holds the initial lexicon's text, which drafters and judges of the independent editions must not
see. Run it only after the independent editions are frozen. Pass the output to agreement.py as
  --edition legacy=nanolex-legacy:OUT.jsonl

One record per seed that has an entry: concept_id, preferred_name, definition, variants (the entry's synonyms),
relations (hypernym, hyponym, meronym, holonym, by label) and source_file. Antonyms, verb relations and
pertainyms are not carried over, because the entry contract of this lexicon does not record them. Where a term
has several entries, the one with the longest definition is used.
"""
import csv, glob, json, os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "data"))
from build_seeds import HEAD, clean, key  # the same heading rule and cleaning that made the seed list

SECTIONS = [(r"synonym", "variant"), (r"hypernym", "hypernym"), (r"hyponym", "hyponym"),
            (r"part holonym|holonym", "holonym"), (r"meronym", "meronym")]
ITEM = re.compile(r"^\s*[-*]\s+(.*)$")

def label(item):
    m = re.match(r"\*\*(.+?)\*\*", item)
    s = m.group(1) if m else re.split(r":| - | \(", item)[0]
    return re.sub(r"\s+", " ", s).strip(" :*`'\"").strip()

def definition(lines, term):
    for l in lines:
        s = l.strip()
        if s.startswith("#") and re.search(r"classif|synonym|hypernym", s, re.I): break
        if not s or s.startswith(("#", "|")): continue
        s = re.sub(r"^[-*\s]*\*\*.+?\*\*\s*(\([^)]{0,12}\))?\s*\**\s*[:\-]?\s*", "", s)
        s = re.sub(r"^(n\.|noun)[:.]?\s+", "", s, flags=re.I).strip()
        if re.match(r"(a |an )?(compound )?noun\b|.{0,60}\bis (used|classified) as\b", s, re.I): continue
        if len(s.split()) >= 6: return s
    return ""

def parse(block):
    out = {"variants": [], "relations": []}
    kind = None
    for l in block:
        h = re.match(r"^#+\s*(.*)", l)
        if h:
            kind = next((k for pat, k in SECTIONS if re.search(pat, h.group(1), re.I)), None)
            continue
        m = ITEM.match(l)
        if kind and m:
            lab = label(m.group(1))
            if not lab or len(lab) > 80: continue
            if kind == "variant": out["variants"].append(lab)
            else: out["relations"].append({"type": kind, "target_label": lab})
    return out

def main():
    src, dest = sys.argv[1:3]
    if ROOT in Path(dest).resolve().parents:
        sys.exit("refusing to write the initial lexicon's text inside the repository; choose a private path")
    seeds = {}
    with open(ROOT / "data" / "seeds.tsv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"): seeds[key(r["preferred_name"])] = r
    best = {}
    for path in sorted(glob.glob(os.path.join(src, "*.md"))):
        raw = open(path, encoding="utf-8").read().split("\n")
        # headings are matched on the raw lines (as build_seeds does); bodies use the unescaped text
        blocks = []; cur = None
        for l in raw:
            m = HEAD.match(l)
            t = clean(m.group(1)) if m else ""
            if t:
                cur = [t, [l.replace("\\n", "\n").split("\n", 1)[1] if "\\n" in l else ""]]; blocks.append(cur)
            elif cur: cur[1].extend(l.replace("\\n", "\n").split("\n"))
        for term, body in blocks:
            seed = seeds.get(key(term))
            if not seed: continue
            body = "\n".join(body).split("\n")
            d = definition(body, term)
            if not d: continue
            rec = {"concept_id": seed["concept_id"], "preferred_name": seed["preferred_name"], "definition": d,
                   **parse(body), "source_file": os.path.basename(path)}
            if seed["concept_id"] not in best or len(d) > len(best[seed["concept_id"]]["definition"]):
                best[seed["concept_id"]] = rec
    with open(dest, "w", encoding="utf-8") as f:
        for cid in sorted(best): f.write(json.dumps(best[cid], ensure_ascii=False) + "\n")
    missing = sorted(set(r["concept_id"] for r in seeds.values()) - set(best))
    print(f"{len(best)}/{len(seeds)} seeds have a legacy entry; {len(missing)} without a usable definition: {missing[:15]}")

if __name__ == "__main__":
    main()
