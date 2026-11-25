#!/usr/bin/env python3
"""Build data/seeds.tsv and data/source-manifest.json from the headings of the initial NanoLex files.

Usage: python3 data/build_seeds.py PATH_TO_INITIAL_LEXICON_DIR [--commit SHA]

Reads only the entry headings ("### Lexical Dictionary Entry: <term>" and its variants). No definition,
classification or relation text is read into the output, so the seed list can be shown to drafters and
judges who must not see the initial lexicon. Deterministic: same input files, same output bytes.
"""
import argparse, collections, glob, hashlib, json, os, re, unicodedata

HEAD = re.compile(r"^#+\s*Lexical\b[A-Za-z ]*?\b(?:Entry|Entries|Dictionary|Annotation|File|Expansion)\s*(?::| for )\s*(.+)$")
IPA = re.compile(r"[ɐ-˿]")
QUOTES = "'\"`„‚‘’“”\\ "

def clean(raw):
    s = unicodedata.normalize("NFC", raw)
    for bad in ("\u201a\u00c4\u00ec", "\u201a\u00c4\u00eb", "\u2013", "\u2011", "\u2010"):
        s = s.replace(bad, "-")                            # mis-encoded and typographic dashes
    s = s.split("\\n")[0].split("#")[0]                  # literal "\n" artefacts and run-on headings
    s = re.split(r"\(?\s*Lexical Dictionary\b", s)[0]      # "X Lexical Dictionary Entry: X" repeats
    s = re.sub(r"\s*\(n\.\)\s*:?\s*$", "", s)              # trailing part-of-speech marker
    s = re.sub(r"\s*\([^)]*$", lambda m: "" if IPA.search(m.group(0)) or m.group(0).strip() == "(" else m.group(0), s)
    s = re.sub(r"\s*\(([^)]*)\)", lambda m: "" if IPA.search(m.group(1)) else m.group(0), s)
    s = re.sub(r"\s+", " ", s).strip(QUOTES).rstrip(":.").strip(QUOTES)
    return s

def key(term):
    """Trivial-variant key: case, quotes, trade-mark signs and spacing only. Hyphen, slash and
    one-word/two-word variants are NOT merged; whether they are one concept is a drafter's call."""
    return re.sub(r"\s+", " ", re.sub(r"[®™]", "", term)).strip().casefold()

def term_form(t):
    if re.search(r"\([A-Za-z0-9\-]{2,12}\)\s*$", t) or re.fullmatch(r"[A-Z0-9\-]{2,8}", t.replace("®", "")):
        return "abbreviated"
    if t.casefold().startswith("nano"):
        return "nano-prefixed"
    return "multiword" if " " in t else "single-word"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source_dir")
    ap.add_argument("--commit", default="unknown")
    a = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    files = sorted(glob.glob(os.path.join(a.source_dir, "*.md")))
    headings = 0; rejected = []; forms = collections.defaultdict(collections.Counter)
    for f in files:
        for line in open(f, encoding="utf-8"):
            m = HEAD.match(line.rstrip("\n"))
            if not m: continue
            headings += 1
            t = clean(m.group(1))
            if not t or len(t) > 90 or not re.search(r"[A-Za-z0-9]", t):
                rejected.append(m.group(1)[:60]); continue
            forms[key(t)][t] += 1
    rows = []
    for k, c in forms.items():
        best = sorted(c.items(), key=lambda kv: (bool(re.search("[\u00ae\u2122]", kv[0])), -sum(ch.isupper() for ch in kv[0]), -kv[1], kv[0]))[0][0]
        rows.append((best, sorted(c)))
    rows.sort(key=lambda r: (r[0].casefold(), r[0]))
    out = os.path.join(here, "seeds.tsv")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("concept_id\tpreferred_name\tterm_form\tmerged_forms\n")
        for i, (name, variants) in enumerate(rows, 1):
            f.write(f"nanolex:{i:04d}\t{name}\t{term_form(name)}\t{'|'.join(v for v in variants if v != name)}\n")
    manifest = {
        "project": "nano-lex",
        "language": "en",
        "source": "entry headings of the initial NanoLex files (Data/*.md), a model-written lexicon from 2024-2025",
        "source_repo": "nikbearbrown/nano-lex-initial-2025 (private archive)",
        "source_commit": a.commit,
        "source_files": {os.path.basename(f): hashlib.sha256(open(f, "rb").read()).hexdigest() for f in files},
        "membership": "every entry heading; definitions, classifications and relations are not read",
        "cleaning": "cut at literal \\n and '#'; plain hyphen for mis-encoded and typographic dashes; drop repeated 'Lexical Dictionary' text, '(n.)' markers, IPA "
                    "parentheticals, wrapping quotes and trailing ':' or '.'; merge forms that differ only in "
                    "case, quotes, trade-mark signs or spacing. Hyphen, slash and spacing-of-words variants stay "
                    "separate seeds.",
        "headings_read": headings,
        "headings_rejected": len(rejected),
        "forms_merged_away": sum(len(c) - 1 for c in forms.values()),
        "seed_count": len(rows),
        "term_forms": dict(sorted(collections.Counter(term_form(r[0]) for r in rows).items())),
        "sha256": hashlib.sha256(open(out, "rb").read()).hexdigest(),
    }
    json.dump(manifest, open(os.path.join(here, "source-manifest.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(os.path.join(here, "source-manifest.json"), "a").write("\n")
    print(f"{headings} headings, {len(rejected)} rejected, {len(rows)} seeds")
    for r in rejected: print("  rejected:", r)

if __name__ == "__main__":
    main()
