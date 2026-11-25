#!/usr/bin/env python3
"""Check data/seeds.tsv against data/source-manifest.json. Exit 1 on any error.

Usage: python3 replication/scripts/validate_seeds.py [--rebuild-from INITIAL_LEXICON_DIR]

With --rebuild-from (maintainers only; the directory is the Data/ folder of the private archive nikbearbrown/nano-lex-initial-2025)
it also rebuilds the seed list in memory and checks that the committed file is byte-identical.
"""
import csv, hashlib, json, re, subprocess, sys, tempfile, shutil
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "data"
FORMS = {"abbreviated", "nano-prefixed", "multiword", "single-word"}

def main():
    errors = []
    raw = (DATA / "seeds.tsv").read_bytes()
    manifest = json.loads((DATA / "source-manifest.json").read_text(encoding="utf-8"))
    if hashlib.sha256(raw).hexdigest() != manifest["sha256"]:
        errors.append("seeds.tsv sha256 differs from the manifest")
    rows = list(csv.DictReader(raw.decode("utf-8").splitlines(), delimiter="\t"))
    if rows and list(rows[0]) != ["concept_id", "preferred_name", "term_form", "merged_forms"]:
        errors.append("unexpected columns: " + ",".join(rows[0]))
    if len(rows) != manifest["seed_count"]:
        errors.append(f"{len(rows)} rows but the manifest says {manifest['seed_count']}")
    seen_id, seen_name = set(), set()
    for n, r in enumerate(rows, 1):
        cid, name = r["concept_id"], r["preferred_name"]
        if cid != f"nanolex:{n:04d}": errors.append(f"row {n}: id {cid} is out of sequence")
        if cid in seen_id: errors.append(f"duplicate id {cid}")
        if not name or name != name.strip() or "\\" in name or "#" in name or len(name) > 90:
            errors.append(f"{cid}: malformed name {name!r}")
        k = re.sub(r"\s+", " ", re.sub(r"[®™]", "", name)).casefold()
        if k in seen_name: errors.append(f"{cid}: name repeats an earlier seed ({name})")
        if r["term_form"] not in FORMS: errors.append(f"{cid}: unknown term_form {r['term_form']!r}")
        seen_id.add(cid); seen_name.add(k)
    if "--rebuild-from" in sys.argv:
        src = sys.argv[sys.argv.index("--rebuild-from") + 1]
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copy(DATA / "build_seeds.py", tmp)
            subprocess.run([sys.executable, str(Path(tmp) / "build_seeds.py"), src, "--commit", manifest["source_commit"]],
                           check=True, capture_output=True)
            if (Path(tmp) / "seeds.tsv").read_bytes() != raw:
                errors.append("rebuilding from the initial lexicon gives a different seeds.tsv")
    for e in errors: print("ERROR", e)
    print(f"{len(rows)} seeds; {len(errors)} errors")
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
