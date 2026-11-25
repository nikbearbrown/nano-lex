#!/usr/bin/env python3
"""Verify Skills Lexicon draft entries against their source bundles.

Usage: python3 verify_drafts.py BUNDLES.jsonl DRAFTS.jsonl REPORT.jsonl [--ungrounded]
--ungrounded checks against the same bundles with wikipedia, wikidata and wordnet emptied,
which is what the ungrounded run was given.
"""
import json
import re
import sys

REL_TYPES = {"synonym", "hypernym", "hyponym", "meronym", "holonym",
             "uses", "requires", "certifies", "contrast"}
BASES = {"source", "model_knowledge"}
WN_RELS = {"hypernym", "hyponym", "part_meronym", "part_holonym",
           "member_meronym", "member_holonym"}
PUNCT = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"',
                       "–": "-", "—": "-", " ": " "})
SOURCE_FIELDS = ("wikipedia", "wikidata", "wordnet")


def norm(s):
    return re.sub(r"\s+", " ", (s or "").translate(PUNCT)).strip().lower()


def is_credential(concept):
    """The lexicon's kind is `credential`; its broad class for that kind is `certification`."""
    return concept.get("kind") == "credential" or concept.get("broad_class") in ("certification", "credential")


def ungrounded(b):
    """The bundle the ungrounded run sees: outside sources emptied, everything else kept."""
    return dict(b, **{f: [] for f in SOURCE_FIELDS})


def ancestor_of(item):
    a = item.get("ancestor_of")
    return set(a) if isinstance(a, list) else {a} if a else set()


def load_jsonl(path):
    out = {}
    with open(path) as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                out[rec["concept_id"]] = rec
    return out


def check_pointer(p, b, links):
    """Return an error string, or None if the pointer checks out."""
    kind, _, rest = p.partition(":")
    body, _, frag = rest.partition("#")
    key, _, val = frag.partition("=")
    if kind == "wd":
        choice = links["wikidata"]["choice"]
        records = b.get("wikidata", [])
        items = {}
        for i in records:  # first record per QID; an ancestor shared by two candidates may appear twice
            items.setdefault(i["qid"], i)
        ok = {choice} | {i["qid"] for i in records if choice in ancestor_of(i)}
        if not choice or body not in ok or body not in items:
            return f"{p}: item not linked or not in bundle"
        item = items[body]
        if key == "alias":
            names = [item.get("label", "")] + item.get("aliases", [])
            return None if norm(val) in map(norm, names) else f"{p}: alias not found"
        return None if val in item.get("claims", {}).get(key, []) else f"{p}: statement not found"
    if kind == "wn":
        if body != links["wordnet"]["choice"]:
            return f"{p}: synset not linked"
        syn = next((s for s in b.get("wordnet", []) if s["synset"] == body), None)
        if syn is None:
            return f"{p}: synset not in bundle"
        if key == "lemma":
            return None if norm(val) in map(norm, syn["lemmas"]) else f"{p}: lemma not in synset"
        if key in WN_RELS:
            return None if val in syn.get("relations", {}).get(key, []) else f"{p}: relation not found"
        return f"{p}: unknown WordNet field"
    if kind == "wp":
        # Revision ids are compared as text: bundles may store them as numbers, pointers always carry text.
        if body != str(links["wikipedia"]["choice"]):
            return f"{p}: article not linked"
        page = next((w for w in b.get("wikipedia", []) if str(w["revision_id"]) == body), None)
        if page is None:
            return f"{p}: article not in bundle"
        if key != "quote":
            return f"{p}: unknown Wikipedia field"
        if len(val.split()) > 20:
            return f"{p}: quote over 20 words"
        return None if norm(val) in norm(page["text"]) else f"{p}: quote not found verbatim"
    if kind == "ex":
        ids = {e["id"] for e in b.get("examples", [])}
        return None if body in ids else f"{p}: example not in bundle"
    return f"{p}: unknown pointer type"


def ngrams(text, n):
    w = re.findall(r"\w+", (text or "").lower())
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


def copies_wikipedia(text, b, n=9):
    src = set()
    for w in b.get("wikipedia", []):
        src |= ngrams(w["text"], n)
    return bool(ngrams(text, n) & src)


def verify(entry, b):
    errs, warns = [], []
    links = entry.get("links", {})
    for s in SOURCE_FIELDS:
        if "choice" not in links.get(s, {}):
            errs.append(f"links.{s} missing")
    if errs:
        return errs, warns
    # A link may only pick one of the bundle's candidates (or abstain with null).
    allowed = {
        "wikipedia": {str(w["revision_id"]) for w in b.get("wikipedia", [])},
        "wikidata": {i["qid"] for i in b.get("wikidata", []) if not ancestor_of(i)},
        "wordnet": {s["synset"] for s in b.get("wordnet", [])},
    }
    for s in SOURCE_FIELDS:
        choice = links[s]["choice"]
        if choice is not None and str(choice) not in allowed[s]:
            errs.append(f"links.{s}: choice {choice!r} is not one of the bundle's candidates")
    neighbor_ids = {n["id"] for n in b.get("neighbors", [])}
    claims = [("definition", entry.get("definition", {}))]
    claims += [(f"variant '{v.get('text')}'", v) for v in entry.get("variants", [])]
    claims += [(f"{r.get('type')} -> {r.get('target_label')}", r)
               for r in entry.get("relations", [])]
    for label, c in claims:
        basis, ptrs = c.get("basis"), c.get("pointers", [])
        if basis not in BASES:
            errs.append(f"{label}: bad basis {basis!r}")
        if basis == "source" and not ptrs:
            errs.append(f"{label}: basis is source but no pointers")
        for p in ptrs:
            e = check_pointer(p, b, links)
            if e:
                errs.append(f"{label}: {e}")
    for r in entry.get("relations", []):
        if r.get("type") not in REL_TYPES:
            errs.append(f"unknown relation type {r.get('type')!r}")
        tid = r.get("target_id")
        if tid is not None and tid not in neighbor_ids:
            errs.append(f"{r.get('target_label')}: target_id {tid} not in neighbors")
        if r.get("type") == "certifies" and not is_credential(b["concept"]):
            errs.append("certifies used on a non-credential concept")
    if copies_wikipedia(entry.get("definition", {}).get("text", ""), b):
        errs.append("definition copies 9+ consecutive words from Wikipedia")
    if sum(c.get("basis") == "model_knowledge" for _, c in claims) > len(claims) / 2:
        warns.append("most claims rest on model knowledge")
    return errs, warns


def main(bundle_path, draft_path, report_path, mode=None):
    bundles, drafts = load_jsonl(bundle_path), load_jsonl(draft_path)
    if mode == "--ungrounded":
        bundles = {cid: ungrounded(b) for cid, b in bundles.items()}
    passed = 0
    with open(report_path, "w") as rep:
        for cid, b in bundles.items():
            entry = drafts.get(cid)
            errs, warns = (["no draft"], []) if entry is None else verify(entry, b)
            passed += not errs
            rep.write(json.dumps({"concept_id": cid, "status": "fail" if errs else "pass",
                                  "errors": errs, "warnings": warns}) + "\n")
    print(f"{passed}/{len(bundles)} drafts passed")


if __name__ == "__main__":
    main(*sys.argv[1:5])
