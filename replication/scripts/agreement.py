#!/usr/bin/env python3
"""DRAFT skeleton for AGREEMENT-METHOD.md (NanoLex): normalise editions, align by concept_id, write blinded judge
requests, compute stats.

Adapted from nikbearbrown/drugs-and-recreational-drug-use-lexicon (branch grok-agreement-method; itself ported through
the clinical lexicon from nikbearbrown/irreducibly-human-work-lexicon, 78f889a2) for this repository: concept ids are
the seed ids in data/seeds.tsv (nanolex:<NNNN>); the concept frame is the seed list (there is no reference lexicon
yet); broad classes are the seeds' term_form; the initial NanoLex joins as an edition through the nanolex-legacy
adapter; flagged abstentions (out-of-scope, duplicate) are compared deterministically for scope agreement and are
never sent to definition judges.

Status: draft (agree-v1-draft). Deterministic parts only; it never calls a model and uses no paid API. Judges
(Codex, Claude Code, or a human interviewed by one of them) read packet files and write result files; see
replication/judging/README.md. One line schema and one validator (`validate`) serve model and human judges alike.

Usage:
  agreement.py run OUT_DIR --edition NAME=SCHEMA:PATH[,PATH...] [--edition ...] [--seeds data/seeds.tsv]
                   [--lexicon lexicon/entries.jsonl [--with-reference]] [--private-dir PRIVATE] [--seed 7]
     SCHEMA is gen-v2 (the drafts.jsonl shape of replication/instructions.md) | nanolex-legacy (the output of
     legacy_to_edition.py) | sonnet-edition (adapter kept from the source kit).
     Later paths override earlier ones for the same concept_id. --lexicon is the reviewed canonical edition
     (lexicon/entries.jsonl, same shape as drafts) once it exists; it adds name variants for target resolution and,
     with --with-reference, joins the comparison as edition "reference".
  agreement.py join OUT_DIR --provider P --model-name M (--version X.Y | --version-unknown) --model-reported "<as shown>"
     Model judges (any model). Builds the versioned judge id (<provider>-<model>-<version>), looks the model up in
     judging/drafters.tsv to decide self-exclusion (the judge never chooses it), writes packets/<judge id>/ in a
     per-judge random order, and records results/<judge id>/judge.json. Run again to resume.
  agreement.py judge-id OUT_DIR --provider P --model-name M (--version X.Y | --version-unknown)   (prints the id only)
  agreement.py export-packet OUT_DIR --judge-id ID [--batch N] [--write FILE]   (chat-only: one paste block)
  agreement.py import OUT_DIR --judge-id ID [--batch N] --reply FILE            (chat-only: store and validate a reply)
  agreement.py register OUT_DIR --judge-id human-xx --name NAME [--size 100] [--overlap 0.3] [--pool-size 50]
     Human judges: draws the seeded, stratified sample (30% from the shared overlap pool) into humans/<id>/.
  agreement.py build-exclusions OUT_DIR --keys PRIVATE/keys/anon.jsonl   (operator; `run` does this itself)
  agreement.py validate OUT_DIR --judge-id VERSIONED_ID   (checks results/<id>/; exit 1 on any error)
  agreement.py stats OUT_DIR --keys PRIVATE/keys/anon.jsonl   (after results/ exist)

Example (two independent editions, each a private run folder with drafts.jsonl; nothing here is committed):
  agreement.py run replication/agreement/pilot-test --private-dir ../agreement-private \
    --edition modela=gen-v2:RUNS/modela/drafts.jsonl --edition modelb=gen-v2:RUNS/modelb/drafts.jsonl \\
    --edition legacy=nanolex-legacy:PRIVATE/legacy/legacy-edition.jsonl
"""
import argparse, glob, hashlib, itertools, json, os, random, re, sys, unicodedata
from collections import Counter, defaultdict

PROMPT_VERSION = "agree-v1-draft"
NOT_ELICITED, ABSTAIN, EMPTY = "NOT_ELICITED", "ABSTAIN", "EMPTY"
AXIS = {"synonym": "EQUIV", "hypernym": "TAX_UP", "broader": "TAX_UP", "hyponym": "TAX_DOWN",
        "holonym": "PART_UP", "part_of": "PART_UP", "meronym": "PART_DOWN", "uses": "ASSOC", "requires": "ASSOC",
        "certifies": "ASSOC", "related": "ASSOC", "contrast": "CONTRAST"}
INVERSE = {"TAX_UP": "TAX_DOWN", "TAX_DOWN": "TAX_UP", "PART_UP": "PART_DOWN", "PART_DOWN": "PART_UP"}
DEF_SCORE = {"EQUIVALENT": 1.0, "A_NARROWER": .75, "B_NARROWER": .75, "OVERLAPPING": .5, "CONFLICTING": 0.0,
             "DIFFERENT_SENSE": 0.0}

def norm(s):
    s = unicodedata.normalize("NFKC", s or "").casefold()
    s = re.sub(r"[\u00ae\u2122]", "", s)
    return re.sub(r"[^\w+#]", "", s)

# ---------- step 0: adapters to the canonical entry ----------
def canon_genv2(e):
    links = {k: (e["links"][k]["choice"] if e["links"][k]["choice"] is not None else ABSTAIN)
             for k in ("wikipedia", "wikidata", "wordnet")}
    fl = e.get("flags") or []
    abst = (e["definition"]["text"] or "").strip().lower() == "out of scope"
    scope = ("duplicate" if any(f.startswith("duplicate") for f in fl) else "out-of-scope") if abst else "entry"
    return {"concept_id": e["concept_id"], "scope": scope, "flags": fl,
            "sense": e.get("work_sense"), "sense_from_definition": False,
            "definition": e["definition"]["text"], "definition_basis": e["definition"]["basis"],
            "definition_pointers": e["definition"].get("pointers", []), "links": links,
            "variants": [{"text": v["text"], "conditional": v.get("condition") is not None,
                          "condition": v.get("condition"), "basis": v["basis"]} for v in e.get("variants", [])],
            "relations": [{"type_fine": r["type"], "axis": AXIS[r["type"]], "target_id": r.get("target_id"),
                           "target_label": r.get("target_label"), "proposed_new": bool(r.get("proposed_new")),
                           "basis": r["basis"]} for r in e.get("relations", [])],
            "run": (e.get("_meta") or {}).get("run")}

def canon_sonnet(e):
    return {"concept_id": e["concept_id"], "scope": "entry", "flags": [], "sense": e["definition"]["text"], "sense_from_definition": True,
            "definition": e["definition"]["text"], "definition_basis": e["definition"]["basis"],
            "definition_pointers": [s.get("identifier") for s in e["definition"].get("sources", [])],
            "links": {k: NOT_ELICITED for k in ("wikipedia", "wikidata", "wordnet")},
            "variants": [{"text": v["label"], "conditional": bool(v.get("ambiguous")), "condition": NOT_ELICITED,
                          "basis": v.get("basis")} for v in e.get("variants", [])],
            "relations": [{"type_fine": NOT_ELICITED, "axis": AXIS[r["type"]], "target_id": r["target"],
                           "target_label": r.get("target_label"), "proposed_new": False, "basis": r.get("basis")}
                          for r in e.get("relations", [])], "run": "edition"}

LEGACY_TYPES = {"hypernym", "hyponym", "meronym", "holonym"}

def canon_legacy(e):
    """The initial NanoLex, as written by scripts/legacy_to_edition.py. It has no sources, links or basis."""
    return {"concept_id": e["concept_id"], "scope": "entry", "flags": [], "sense": e["definition"],
            "sense_from_definition": True, "definition": e["definition"], "definition_basis": NOT_ELICITED,
            "definition_pointers": [], "links": {k: NOT_ELICITED for k in ("wikipedia", "wikidata", "wordnet")},
            "variants": [{"text": v, "conditional": False, "condition": NOT_ELICITED, "basis": NOT_ELICITED}
                         for v in e.get("variants", [])],
            "relations": [{"type_fine": r["type"], "axis": AXIS[r["type"]], "target_id": None,
                           "target_label": r["target_label"], "proposed_new": True, "basis": NOT_ELICITED}
                          for r in e.get("relations", []) if r["type"] in LEGACY_TYPES], "run": "legacy"}

ADAPTERS = {"gen-v2": canon_genv2, "nanolex-legacy": canon_legacy, "sonnet-edition": canon_sonnet}

def load_edition(spec):
    name, rest = spec.split("=", 1)
    schema, paths = rest.split(":", 1)
    out = {}
    for p in paths.split(","):
        for line in open(p):
            if line.strip():
                c = ADAPTERS[schema](json.loads(line)); out[c["concept_id"]] = c
    return name, out

SEEDS_DEFAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "seeds.tsv")
def load_frame(seeds_path):
    """The concept frame: every seed in data/seeds.tsv, keyed by its original concept_id."""
    frame = {}
    with open(seeds_path) as f:
        head = f.readline().rstrip("\n").split("\t")
        for line in f:
            if not line.strip(): continue
            r = dict(zip(head, line.rstrip("\n").split("\t")))
            frame[r["concept_id"]] = {"id": r["concept_id"], "preferred_name": r["preferred_name"],
                                      "broad_class": r.get("term_form") or "other", "variants": []}
    return frame

def load_lexicon(path, frame):
    """Reviewed canonical edition (lexicon/entries.jsonl, same shape as drafts). Adds its variants to the frame for
    name resolution and returns it as a canonical edition."""
    ref = {}
    for line in open(path):
        if line.strip():
            c = canon_genv2(json.loads(line)); c["run"] = "reference"; ref[c["concept_id"]] = c
            if c["concept_id"] in frame and c["scope"] == "entry":
                frame[c["concept_id"]]["variants"] = [{"label": v["text"]} for v in c["variants"] if not v["conditional"]]
    return ref

# ---------- step 1: deterministic alignment ----------
def name_index(lex):
    idx = defaultdict(set)
    for i, d in lex.items():
        idx[norm(d["preferred_name"])].add(i)
        for v in d.get("variants", []):
            idx[norm(v["label"])].add(i)
    return idx

def resolve_targets(ed, idx):
    """Pass 2: resolve label-only targets to a lexicon id when exactly one concept has that name."""
    n = 0
    for c in ed.values():
        for r in c["relations"]:
            if not r["target_id"]:
                hits = idx.get(norm(r["target_label"]), set())
                if len(hits) == 1:
                    r["target_id"], r["resolved_by"] = next(iter(hits)), "name"; n += 1
            else:
                r.setdefault("resolved_by", "id")
    return n

def edge_set(c, level):
    s = set()
    for r in c["relations"]:
        key = r["target_id"] or "unresolved:" + norm(r["target_label"])
        if level == "target": s.add(key)
        elif level == "axis": s.add((r["axis"], key))
        else: s.add((r["type_fine"], key))
    return s

# ---------- statistics ----------
def f1(a, b):
    if not a and not b: return None
    return 2 * len(a & b) / (len(a) + len(b))

def kripp_alpha_nominal(units):
    """units: list of lists of values (one per rater that rated the unit; missing omitted)."""
    o = Counter(); n = 0
    for vals in units:
        m = len(vals)
        if m < 2: continue
        for a, b in itertools.permutations(range(m), 2):
            o[(vals[a], vals[b])] += 1 / (m - 1)
        n += m
    if n == 0: return None
    nc = Counter()
    for (a, _), w in o.items(): nc[a] += w
    do = sum(w for (a, b), w in o.items() if a != b) / n
    de = sum(nc[a] * nc[b] for a in nc for b in nc if a != b) / (n * (n - 1))
    return None if de == 0 else 1 - do / de

def fleiss_kappa(units):
    units = [u for u in units if len(u) == len(units[0])] if units else []
    if not units or len(units[0]) < 2: return None
    m = len(units[0]); cats = sorted({v for u in units for v in u}, key=str)
    p_j = {c: sum(u.count(c) for u in units) / (len(units) * m) for c in cats}
    P_i = [(sum(u.count(c) ** 2 for c in cats) - m) / (m * (m - 1)) for u in units]
    Pbar, Pe = sum(P_i) / len(P_i), sum(v * v for v in p_j.values())
    return None if Pe == 1 else (Pbar - Pe) / (1 - Pe)

def gwet_ac1_two(pairs):
    if not pairs: return None
    cats = sorted({x for p in pairs for x in p}, key=str); q = len(cats)
    if q < 2: return None
    pa = sum(a == b for a, b in pairs) / len(pairs)
    pi = {c: sum((a == c) + (b == c) for a, b in pairs) / (2 * len(pairs)) for c in cats}
    pe = sum(p * (1 - p) for p in pi.values()) / (q - 1)
    return (pa - pe) / (1 - pe)

def bootstrap(concepts, stat, reps=2000, seed=7):
    """Resample concepts with replacement; stat(list_of_concepts) -> float or None."""
    rng = random.Random(seed); est = stat(concepts); vals = []
    for _ in range(reps):
        v = stat([rng.choice(concepts) for _ in concepts])
        if v is not None: vals.append(v)
    vals.sort()
    if est is None or not vals: return est, None, None
    return est, vals[int(.025 * len(vals))], vals[int(.975 * len(vals)) - 1]

# ---------- step 2: blinded judge requests (stubs; no model is called) ----------
PROMPTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "judging", "prompts")
SYSTEM = open(os.path.join(PROMPTS, "system.txt")).read().strip() if os.path.exists(os.path.join(PROMPTS, "system.txt")) else ""
LABELS = {"P1": None, "P2": set(DEF_SCORE), "P3": None,
          "P4": {"SAME_TYPE", "COMPATIBLE_TYPE", "REVERSED", "CONFLICTING_TYPE"},
          "P5": {"SAME_CONDITION", "COMPATIBLE_CONDITION", "CONFLICTING_CONDITION"},
          "P6": {"COMPATIBLE", "CONFLICTING"}}
# trap concepts (AGREEMENT-METHOD.md 4.3). DRAFT FOR BEAR'S REVIEW: chosen by Claude from the seed names while
# setting up this kit, in a session that had the initial lexicon open; confirm or replace before the first run.
# Look-alike pairs (Nano-Ceria / Nanoceria; Nanofiber / Nanofibre; SLN (Spheroidal Nucleosomes) / Solid Lipid
# Nanoparticle (SLN); Nanostructured Lipid Carrier (NLC) / NLC (Nano-Lipid Complex); Enhanced Permeability and
# Retention (EPR) / ... (EPR) Effect; PAMAM / Poly(amidoamine); Gold Colloid / Gold Nanoparticle; Abraxane /
# Albumin-Bound Paclitaxel), umbrella terms (Nanoparticle, Nanomaterial, Nanocarrier, Nanomedicine) and short or
# multi-sense names (Stimuli Responsive, Theranostic, Nano-Scale, Nanocrystal).
TRAP_IDS = {"nanolex:0401", "nanolex:0494", "nanolex:0545", "nanolex:0548", "nanolex:0875", "nanolex:0883",
            "nanolex:0667", "nanolex:0705", "nanolex:0169", "nanolex:0170", "nanolex:0720", "nanolex:0772",
            "nanolex:0210", "nanolex:0217", "nanolex:0005", "nanolex:0014", "nanolex:0596", "nanolex:0582",
            "nanolex:0489", "nanolex:0583", "nanolex:0894", "nanolex:0927", "nanolex:0460", "nanolex:0514"}
KIND_LABEL = {"abbreviated": "an abbreviation, or a name that carries one", "nano-prefixed": "a name starting with nano",
              "multiword": "a multi-word name", "single-word": "a single-word name"}

MASK = re.compile(r"\b(grok|xai|claude|anthropic|sonnet|opus|gpt|openai|codex|muse|gemini|as an ai)\b", re.I)

P2_TEMPLATE = open(os.path.join(PROMPTS, "P2.txt")).read().strip() if os.path.exists(os.path.join(PROMPTS, "P2.txt")) else ""

def p2_request(cid, lexe, ea, eb, a_text, b_text, rng):
    """Render prompts/P2.txt exactly; A/B order is random and recorded only in the private key."""
    order = [ea, eb]; rng.shuffle(order)
    texts = {ea: a_text, eb: b_text}
    user = (P2_TEMPLATE.replace("{preferred_name}", lexe["preferred_name"])
            .replace("{kind}", KIND_LABEL.get(lexe["broad_class"], "other"))
            .replace("{text_a}", MASK.sub("[model]", texts[order[0]])).replace("{text_b}", MASK.sub("[model]", texts[order[1]])))
    return order, user

def run(args):
    """Public files (requests/) go in OUT; everything that names an edition (keys, canonical drafts, coverage,
    deterministic tables) goes in --private-dir, which must NOT be committed to a public repo."""
    priv = args.private_dir or args.out
    for d in ("requests/P2", "results", "packets", "humans"):
        os.makedirs(os.path.join(args.out, d), exist_ok=True)
    for d in ("canonical", "keys", "tables"):
        os.makedirs(os.path.join(priv, d), exist_ok=True)
    secret = os.urandom(16).hex()  # request ids are keyed by this secret so they cannot be brute-forced to editions
    open(os.path.join(priv, "keys", "request-id-secret.txt"), "w").write(secret + "\n")
    only = set(l.split()[0] for l in open(args.concepts) if l.strip() and not l.startswith("#")) if args.concepts else None
    lex = load_frame(args.seeds)  # the concept frame: every seed, keyed by its original concept_id
    ref = load_lexicon(args.lexicon, lex) if args.lexicon else {}
    eds = dict(load_edition(s) for s in args.edition)
    if ref and args.with_reference:
        eds["reference"] = ref
    stray = {n: sorted(set(ed) - set(lex)) for n, ed in eds.items()}
    for n, xs in stray.items():
        if xs: print(f"WARNING {n}: {len(xs)} concept ids not in the seed list (ignored for judging), e.g. {xs[:3]}")
    idx = name_index(lex)
    names = list(eds)
    for n, ed in eds.items():
        k = resolve_targets(ed, idx)
        with open(os.path.join(priv, "canonical", f"{n}.jsonl"), "w") as f:
            for c in ed.values(): f.write(json.dumps(c) + "\n")
        print(f"{n}: {len(ed)} concepts; {k} label-only targets resolved by name")
    allc = sorted(lex)
    # coverage
    with open(os.path.join(priv, "coverage.csv"), "w") as f:
        f.write("concept_id,broad_class," + ",".join(names) + "\n")
        for c in allc:  # 1 = entry, O = out-of-scope, D = duplicate, 0 = missing
            f.write(f"{c},{lex[c]['broad_class']}," + ",".join(
                {"entry": "1", "out-of-scope": "O", "duplicate": "D"}[eds[n][c]["scope"]] if c in eds[n] else "0"
                for n in names) + "\n")
    rows = ["| pair | shared | both have relations | rel F1 target (macro) | rel F1 axis | both have variants | variant F1 (exact norm) | conditional-flag agreement |",
            "|---|---:|---:|---|---|---:|---|---|"]
    rng = random.Random(args.seed); req, keys = [], []
    scope_rows = ["", "| pair | seeds in both | same scope label | both entries | both abstain | one abstains | scope AC1 |",
                  "|---|---:|---:|---:|---:|---:|---|"]
    for a, b in itertools.combinations(names, 2):
        inboth = sorted((set(eds[a]) & set(eds[b])) & set(lex))
        if only is not None: inboth = [c for c in inboth if c in only]
        sp = [(eds[a][c]["scope"], eds[b][c]["scope"]) for c in inboth]
        scope_rows.append(f"| {a} × {b} | {len(sp)} | {sum(x == y for x, y in sp)} | {sum(x == y == 'entry' for x, y in sp)} | "
                          f"{sum(x != 'entry' and y != 'entry' for x, y in sp)} | {sum((x == 'entry') != (y == 'entry') for x, y in sp)} | "
                          f"{gwet_ac1_two(sp)} |")
        # definitions, variants and relations are compared only where BOTH editions wrote an entry
        shared = [c for c in inboth if eds[a][c]["scope"] == "entry" and eds[b][c]["scope"] == "entry"]
        def relf(level):
            def s(cs):
                v = [f1(edge_set(eds[a][c], level), edge_set(eds[b][c], level)) for c in cs]
                v = [x for x in v if x is not None]; return sum(v) / len(v) if v else None
            return s
        def varf(cs):
            v = [f1({norm(x["text"]) for x in eds[a][c]["variants"]}, {norm(x["text"]) for x in eds[b][c]["variants"]}) for c in cs]
            v = [x for x in v if x is not None]; return sum(v) / len(v) if v else None
        cond = []
        for c in shared:
            vb = {norm(x["text"]): x["conditional"] for x in eds[b][c]["variants"]}
            cond += [(x["conditional"], vb[norm(x["text"])]) for x in eds[a][c]["variants"] if norm(x["text"]) in vb]
        fmt = lambda t: "n/a" if t[0] is None else f"{t[0]:.3f} [{t[1]:.3f}, {t[2]:.3f}]"
        both_rel = sum(1 for c in shared if eds[a][c]["relations"] and eds[b][c]["relations"])
        both_var = sum(1 for c in shared if eds[a][c]["variants"] and eds[b][c]["variants"])
        ca = sum(x == y for x, y in cond) / len(cond) if cond else None
        rows.append(f"| {a} × {b} | {len(shared)} | {both_rel} | {fmt(bootstrap(shared, relf('target'), args.reps))} | "
                    f"{fmt(bootstrap(shared, relf('axis'), args.reps))} | {both_var} | {fmt(bootstrap(shared, varf, args.reps))} | "
                    f"{'n/a' if ca is None else f'{ca:.3f} (n={len(cond)}, AC1={gwet_ac1_two(cond)})'} |")
        for c in shared:
            order, user = p2_request(c, lex[c], a, b, eds[a][c]["definition"], eds[b][c]["definition"], rng)
            rid = "r-" + hashlib.sha256(f"{secret}|P2|{c}|{a}|{b}".encode()).hexdigest()[:12]
            req.append({"request_id": rid, "stage": "P2", "concept_id": c, "field": "definition",
                        "kind": KIND_LABEL.get(lex[c]["broad_class"]), "broad_class": lex[c]["broad_class"], "trap": c in TRAP_IDS,
                        "prompt_version": PROMPT_VERSION, "prompt_sha256": hashlib.sha256((SYSTEM + user).encode()).hexdigest(),
                        "system": SYSTEM, "user": user})
            keys.append({"request_id": rid, "A": order[0], "B": order[1]})
    # multi-rater: presence/absence of each target (axis-level), nominal alpha across all editions
    units = []
    for c in allc:
        have = [n for n in names if c in eds[n] and eds[n][c]["scope"] == "entry"]
        if len(have) < 2: continue
        tgts = set().union(*[edge_set(eds[n][c], "target") for n in have])
        for t in tgts:
            units.append([next((r["axis"] for r in eds[n][c]["relations"] if (r["target_id"] or "unresolved:" + norm(r["target_label"])) == t), "NONE") for n in have])
    rows += ["", f"UNION-FRAME (biased low, see AGREEMENT-METHOD.md 6.2; replace with the fixed neighbour frame) Krippendorff nominal alpha, {len(units)} units: "
             f"{kripp_alpha_nominal(units)}", f"Fleiss kappa on the same units (complete only): {fleiss_kappa(units)}"]
    rows += scope_rows
    open(os.path.join(priv, "tables", "deterministic.md"), "w").write("\n".join(rows) + "\n")
    rng.shuffle(req)  # so batch position reveals nothing about which editions are paired
    for b in range(0, len(req), args.batch_size):
        with open(os.path.join(args.out, "requests", "P2", f"batch-{b // args.batch_size + 1:04d}.jsonl"), "w") as f:
            for r in req[b:b + args.batch_size]: f.write(json.dumps(r) + "\n")
    with open(os.path.join(priv, "keys", "anon.jsonl"), "w") as f:
        for k in keys: f.write(json.dumps(k) + "\n")
    write_exclusions(args.out, {k["request_id"]: k for k in keys})
    print("\n".join(rows)); print(f"wrote {len(req)} P2 requests (blinded); PRIVATE key in {priv}/keys/anon.jsonl")

# ---------- judges: registration, sampling, validation (one schema for model and human judges) ----------
def jload(path):
    return [json.loads(l) for l in open(path) if l.strip()] if os.path.exists(path) else []

def all_requests(out):
    return [r for f in sorted(glob.glob(os.path.join(out, "requests", "*", "batch-*.jsonl"))) for r in jload(f)]

def judges_file(out):
    p = os.path.join(out, "judges.json")
    return p, (json.load(open(p)) if os.path.exists(p) else {})

def stratified(items, n, rng, trap_share):
    """Proportional allocation over field x broad_class (>=1 per non-empty cell), trap quota first."""
    if n <= 0 or not items: return []
    pick = []
    traps = [r for r in items if r.get("trap")]
    rng.shuffle(traps); pick += traps[:min(len(traps), max(1, round(n * trap_share)) if traps else 0)]
    rest = [r for r in items if r not in pick]
    cells = defaultdict(list)
    for r in rest: cells[(r["field"], r.get("broad_class"))].append(r)
    need = n - len(pick)
    for k in sorted(cells, key=str):
        rng.shuffle(cells[k])
        pick += cells[k][:max(1, round(need * len(cells[k]) / len(rest)))]
    rng.shuffle(pick)
    return pick[:n]

def register(args):
    """Human judges only. Model judges use `join` (they never choose their own exclusions)."""
    out = args.out; reqs = all_requests(out)
    if args.type != "human": sys.exit("model judges join with `agreement.py join` (see replication/judging/AI-JUDGE-INSTRUCTIONS.md)")
    jp, judges = judges_file(out)
    if args.judge_id in judges and not args.force: sys.exit(f"{args.judge_id} is already registered (use --force to redraw)")
    seed = int(hashlib.sha256(f"{args.salt}|{args.judge_id}".encode()).hexdigest()[:8], 16)
    judges[args.judge_id] = {"type": "human", "name": args.name, "seed": seed, "salt": args.salt, "size": args.size,
                             "overlap": args.overlap, "pool_size": args.pool_size, "trap_share": args.trap_share}
    if True:
        hd = os.path.join(out, "humans"); os.makedirs(hd, exist_ok=True)
        pool_path = os.path.join(hd, "overlap-pool.jsonl")
        pool = jload(pool_path)
        if not pool:
            prng = random.Random(f"{args.salt}|pool")
            pool = [{"request_id": r["request_id"], "times_assigned": 0} for r in stratified(reqs, args.pool_size, prng, args.trap_share)]
        rng = random.Random(seed)
        n_over = round(args.size * args.overlap)
        order = sorted(pool, key=lambda x: (x["times_assigned"], rng.random()))[:n_over]
        for x in order: x["times_assigned"] += 1
        with open(pool_path, "w") as f:
            for x in pool: f.write(json.dumps(x) + "\n")
        taken = {x["request_id"] for x in pool}
        for f in glob.glob(os.path.join(hd, "*", "sample.jsonl")):
            taken |= {x["request_id"] for x in jload(f)}
        uniq = stratified([r for r in reqs if r["request_id"] not in taken], args.size - len(order), rng, args.trap_share)
        byid = {r["request_id"]: r for r in reqs}
        sample = [dict(byid[x["request_id"]], overlap=True) for x in order] + [dict(r, overlap=False) for r in uniq]
        rng.shuffle(sample)
        d = os.path.join(hd, args.judge_id); os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "sample.jsonl"), "w") as f:
            for i, r in enumerate(sample): f.write(json.dumps({"position": i + 1, **{k: r[k] for k in ("request_id", "stage", "concept_id", "user", "overlap")}}) + "\n")
        json.dump({"next_position": 1, "done": 0, "total": len(sample)}, open(os.path.join(d, "progress.json"), "w"))
        with open(os.path.join(hd, "registry.jsonl"), "a") as f:
            f.write(json.dumps({"judge_id": args.judge_id, "name": args.name, "seed": seed, "size": len(sample),
                                "overlap_items": len(order), "unique_items": len(uniq)}) + "\n")
        print(f"{args.judge_id}: {len(sample)} items ({len(order)} overlap, {len(uniq)} unique) in humans/{args.judge_id}/sample.jsonl")
    json.dump(judges, open(jp, "w"), indent=1)

def slug(*parts):
    return re.sub(r"[^a-z0-9]+", "-", "-".join(p for p in parts if p).lower()).strip("-")

# ---------- model judges: join (self-service, generic), packets, chat-only export/import ----------
import fnmatch
DRAFTERS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "judging", "drafters.tsv")
EXCL_SALT = "agree-v1-exclusions"  # public: the exclusion index is obfuscated, NOT secret (AGREEMENT-METHOD.md 11)

def etoken(edition):
    return hashlib.sha256(f"{EXCL_SALT}|{edition}".encode()).hexdigest()[:12]

def write_exclusions(out, keys):
    """requests/exclusions.json: for each edition, the requests that involve it, keyed by an obfuscated token."""
    groups = defaultdict(list)
    for k in keys.values():
        for e in {k["A"], k["B"]}: groups[etoken(e)].append(k["request_id"])
    json.dump({"note": "Self-exclusion index for `agreement.py join`. Tokens are obfuscated edition names. Judges: do not open.",
               "groups": {t: sorted(v) for t, v in sorted(groups.items())}}, open(os.path.join(out, "requests", "exclusions.json"), "w"), indent=0)

def build_exclusions(args):
    keys = {k["request_id"]: k for k in jload(args.keys)}
    if not keys: sys.exit("needs the private keys/anon.jsonl")
    write_exclusions(args.out, keys); print(f"wrote {args.out}/requests/exclusions.json")

def norm_version(v):
    return re.sub(r"[^0-9a-z]+", ".", (v or "").lower()).strip(".")

def drafter_match(provider, model_name, version):
    """Look the model up in judging/drafters.tsv. Returns (editions to exclude, flags, matched rows).
    Exact drafter (provider, model and version match): exclude its editions.
    Version unknown but provider and model match a drafter row: exclude too (cannot rule it out) and flag.
    Same provider as a drafter but a different model or version: no exclusion, flag same_family_as_drafter."""
    rows = []
    for line in open(DRAFTERS):
        if not line.strip() or line.startswith("#") or line.startswith("provider\t"): continue
        c = line.rstrip("\n").split("\t")
        rows.append({"provider": c[0].strip().lower(), "model": c[1].strip(), "version": c[2].strip(),
                     "editions": [e for e in c[3].split(",") if e.strip()], "note": c[4] if len(c) > 4 else ""})
    m, v = slug(model_name), norm_version(version)
    prov = lambda x: re.sub(r"[^a-z0-9]", "", x.lower())  # xAI, x.ai, X-AI -> xai
    excl, flags, hits = set(), set(), []
    for r in rows:
        if prov(r["provider"]) != prov(provider): continue
        if fnmatch.fnmatch(m, r["model"]):
            if version is None:
                if r["version"] != "*": flags.add("possible_drafter_version_unknown")
                excl |= set(r["editions"]); hits.append(r)
            elif fnmatch.fnmatch(v, r["version"]):
                excl |= set(r["editions"]); hits.append(r)
            else:
                flags.add("same_family_as_drafter")
        else:
            flags.add("same_family_as_drafter")
    if excl: flags.discard("same_family_as_drafter")
    return excl, sorted(flags), hits

def eligible_packets(out, jid, excl):
    reqs = all_requests(out)
    ex = os.path.join(out, "requests", "exclusions.json")
    if excl and not os.path.exists(ex): sys.exit(f"{ex} is missing; the operator must run build-exclusions")
    groups = json.load(open(ex))["groups"] if os.path.exists(ex) else {}
    drop = set().union(*[set(groups.get(etoken(e), [])) for e in excl]) if excl else set()
    ok = [r for r in reqs if r["request_id"] not in drop]
    seed = int(hashlib.sha256(f"agree-v1|{jid}".encode()).hexdigest()[:8], 16)
    random.Random(seed).shuffle(ok)
    return ok, len(reqs), seed

PACKET_KEYS = ("request_id", "stage", "concept_id", "prompt_version", "prompt_sha256", "system", "user")

def judge_id_of(a):
    if bool(a.version) == bool(a.version_unknown):
        sys.exit("give exactly one of --version X.Y (as your harness or system information states it) or --version-unknown")
    return slug(a.provider, a.model_name, a.version.strip() if a.version else "version-unknown")

def judge_id_cmd(args):
    print(judge_id_of(args))

def batch_status(out, jid):
    pk = sorted(glob.glob(os.path.join(out, "packets", jid, "batch-*.jsonl")))
    done = []
    for f in pk:
        rf = os.path.join(out, "results", jid, os.path.basename(f))
        if os.path.exists(rf):
            want = {r["request_id"] for r in jload(f)}
            lines = jload(rf)
            got = {x["request_id"] for x in lines if "_batch" not in x}
            if want <= got and any("finished_at" in x for x in lines if "_batch" in x): done.append(os.path.basename(f))
    nxt = next((os.path.basename(f) for f in pk if os.path.basename(f) not in done), None)
    return pk, done, nxt

def join(args):
    out = args.out; jid = judge_id_of(args); version = args.version.strip() if args.version else None
    d = os.path.join(out, "results", jid); p = os.path.join(d, "judge.json")
    excl, flags, hits = drafter_match(args.provider, args.model_name, version)
    if not version: flags = sorted(set(flags) | {"version_unknown"})
    if os.path.exists(p):
        rec = json.load(open(p))
        if (rec["provider"], rec["model_name"], rec["model_version"]) != (args.provider.lower(), slug(args.model_name), version):
            sys.exit(f"{p} records a different identity; stop and tell the operator")
        status = "resumed"
    else:
        ok, total, seed = eligible_packets(out, jid, excl)
        pd = os.path.join(out, "packets", jid); os.makedirs(pd, exist_ok=True); os.makedirs(d, exist_ok=True)
        for b in range(0, len(ok), args.batch_size):
            with open(os.path.join(pd, f"batch-{b // args.batch_size + 1:04d}.jsonl"), "w") as f:
                for r in ok[b:b + args.batch_size]: f.write(json.dumps({k: r[k] for k in PACKET_KEYS}) + "\n")
        import datetime
        rec = {"judge_id": jid, "provider": args.provider.lower(), "model_name": slug(args.model_name),
               "model_version": version, "version_status": "stated" if version else "unknown",
               "model_reported": args.model_reported, "harness": args.harness, "harness_version": args.harness_version,
               "effort": args.effort, "plan": args.plan, "flags": flags,
               "self_exclusion": {"drafter_rows": [f"{h['provider']}\t{h['model']}\t{h['version']}" for h in hits],
                                  "editions_excluded": len(excl), "requests_total": total, "requests_assigned": len(ok)},
               "seed": seed, "batch_size": args.batch_size,
               "joined_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds")}
        json.dump(rec, open(p, "w"), indent=1); status = "joined"
    pk, done, nxt = batch_status(out, jid)
    n = sum(len(jload(f)) for f in pk)
    print(f"judge id: {jid}  ({status})" + ("   ** FLAGGED: " + ", ".join(rec["flags"]) + " **" if rec["flags"] else ""))
    print(f"items: {n} in {len(pk)} batches (packets/{jid}/); done: {len(done)}; next: {nxt or 'none - all batches done'}")
    print(f"branch: judging/{jid}")

def check(out, jid):
    _, judges = judges_file(out)
    rec = judge_record(out, jid)
    if jid in judges and judges[jid]["type"] == "human":
        kind, pkdir = "human", None
        allowed = {r["request_id"] for r in jload(os.path.join(out, "humans", jid, "sample.jsonl"))}
    elif rec:
        kind, pkdir = "model", os.path.join(out, "packets", jid)
        allowed = {r["request_id"] for f in glob.glob(os.path.join(pkdir, "*.jsonl")) for r in jload(f)}
    else:
        sys.exit(f"{jid} has not joined (no results/{jid}/judge.json) and is not a registered human judge")
    errs, warns, seen, n = [], [], set(), 0
    if kind == "model":
        for fl in rec.get("flags", []):
            if fl in ("version_unknown", "possible_drafter_version_unknown"):
                warns.append(f"FLAGGED {fl}: results are reported separately and kept out of the primary panel")
        if jid != slug(rec["provider"], rec["model_name"], rec["model_version"] or "version-unknown"):
            errs.append(f"judge id {jid} does not match provider/model/version in judge.json")
        excl, _, _ = drafter_match(rec["provider"], rec["model_name"], rec["model_version"])
        ok, _, _ = eligible_packets(out, jid, excl)
        if {r["request_id"] for r in ok} != allowed:
            errs.append("packets differ from what join generates for this identity (self-exclusion must come from join, not by hand)")
    for f in sorted(glob.glob(os.path.join(out, "results", jid, "**", "*.jsonl"), recursive=True)):
        for ln, line in enumerate(open(f), 1):
            if not line.strip(): continue
            try: j = json.loads(line)
            except ValueError: errs.append(f"{f}:{ln} not JSON"); continue
            if "_batch" in j:
                if kind == "model":
                    bad = [k for k in WHO if j.get(k) != rec.get(k)]
                    if j.get("judge_id") != jid: bad.append("judge_id")
                    if bad: errs.append(f"{f}:{ln} header {bad} differ from results/{jid}/judge.json")
                continue
            n += 1
            miss = [k for k in REQUIRED if k not in j]
            if miss: errs.append(f"{f}:{ln} missing {miss}"); continue
            if j["request_id"] not in allowed: errs.append(f"{f}:{ln} {j['request_id']} was not assigned to {jid}")
            key = (j["request_id"], j["run_index"])
            if key in seen: errs.append(f"{f}:{ln} duplicate {key}")
            seen.add(key)
            labels = LABELS.get(j["stage"])
            if labels and j["label"] not in labels | {"UNSURE"}: errs.append(f"{f}:{ln} label {j['label']!r} not allowed for {j['stage']}")
            if j["judge"].get("id") != jid: errs.append(f"{f}:{ln} judge.id {j['judge'].get('id')!r} != {jid}")
            if kind == "model":
                if "model_version" not in j["judge"]: errs.append(f"{f}:{ln} judge.model_version is required (null only if unknown)")
                bad = [k for k in WHO if j["judge"].get(k) != rec.get(k)]
                if bad: errs.append(f"{f}:{ln} judge {bad} differ from results/{jid}/judge.json")
            if kind == "human" and j["confirmed"] is not True: errs.append(f"{f}:{ln} human label not confirmed by the judge")
    if kind == "model":  # a handed-in batch must answer every request in the packet of the same name
        for f in sorted(glob.glob(os.path.join(out, "results", jid, "batch-*.jsonl"))):
            pk = os.path.join(pkdir, os.path.basename(f))
            want_ids = {r["request_id"] for r in jload(pk)}
            got = {j["request_id"] for j in jload(f) if "_batch" not in j and "request_id" in j}
            if not os.path.exists(pk): errs.append(f"{f}: no packet {pk}")
            elif want_ids - got: errs.append(f"{f}: incomplete, {len(want_ids - got)} of {len(want_ids)} requests unanswered")
            hdr = [j for j in jload(f) if "_batch" in j]
            if not any("finished_at" in h for h in hdr): errs.append(f"{f}: no closing header line with finished_at")
    return errs, warns, n

def validate(args):
    errs, warns, n = check(args.out, args.judge_id)
    for w in warns: print("WARNING", w)
    for e in errs[:50]: print("ERROR", e)
    print(f"{args.judge_id}: {n} judgments, {len(errs)} errors, {len(warns)} flags"); sys.exit(1 if errs else 0)

def pick_batch(out, jid, batch):
    pk, done, nxt = batch_status(out, jid)
    name = f"batch-{int(batch):04d}.jsonl" if batch else nxt
    if not name: sys.exit("all batches are done")
    path = os.path.join(out, "packets", jid, name)
    if not os.path.exists(path): sys.exit(f"no {path}")
    return name, jload(path)

def export_packet(args):
    """Chat-only fallback: one self-contained block to paste into a model with no shell."""
    rec = judge_record(args.out, args.judge_id)
    if not rec: sys.exit(f"{args.judge_id} has not joined; run join first (the operator can run it for a chat-only model)")
    name, items = pick_batch(args.out, args.judge_id, args.batch)
    system = items[0]["system"] if items else SYSTEM
    lines = [f"LEXICON AGREEMENT JUDGING - {name.replace('.jsonl', '')} - judge {args.judge_id} - {len(items)} items", "",
             "INSTRUCTIONS", system, "",
             "Answer every item below on its own. Do not compare items with each other, do not use the web, and do not",
             "guess who wrote a text. Each item ends with the labels to choose from and the fields to return.", "",
             "REPLY FORMAT: reply with ONLY one ```jsonl code block, with one line per item, in item order, exactly like:",
             '{"request_id": "<copy from the item>", "label": "<one label>", "fields": {"same_sense": true, "genus_a": "...", '
             '"genus_b": "...", "conflicts": [], "confidence": 3, "rationale": "<=40 words"}}',
             "No other text. Every request_id must appear exactly once.", ""]
    for k, r in enumerate(items, 1):
        lines += [f"=== ITEM {k} of {len(items)} | request_id: {r['request_id']} ===", r["user"], ""]
    lines += [f"=== END OF {name.replace('.jsonl', '')}: reply with the jsonl block now ==="]
    text = "\n".join(lines) + "\n"
    if args.write: open(args.write, "w").write(text); print(f"wrote {args.write} ({len(items)} items, {name})")
    else: sys.stdout.write(text)

def import_reply(args):
    """Chat-only fallback: validate a pasted JSONL reply and store it as results/<judge_id>/<batch>."""
    out, jid = args.out, args.judge_id
    rec = judge_record(out, jid)
    if not rec: sys.exit(f"{jid} has not joined")
    name, items = pick_batch(out, jid, args.batch)
    byid = {r["request_id"]: r for r in items}
    raw = open(args.reply).read()
    got, errs = [], []
    for ln, line in enumerate(raw.splitlines(), 1):
        line = line.strip()
        if not line.startswith("{"): continue
        try: got.append(json.loads(line))
        except ValueError: errs.append(f"reply line {ln}: not JSON")
    ids = [g.get("request_id") for g in got]
    for i in sorted(set(ids)):
        if i not in byid: errs.append(f"{i}: not in {name}")
    for i in byid:
        if ids.count(i) != 1: errs.append(f"{i}: answered {ids.count(i)} times (need exactly 1)")
    for g in got:
        r = byid.get(g.get("request_id"))
        labels = LABELS.get(r["stage"]) if r else None
        if r and labels and g.get("label") not in labels | {"UNSURE"}: errs.append(f"{g['request_id']}: label {g.get('label')!r} not allowed")
    if errs:
        for e in errs[:50]: print("ERROR", e)
        sys.exit(f"nothing stored: fix the reply (or ask the model again) and re-import")
    import datetime
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    who = {k: rec.get(k) for k in WHO}
    hdr = {"_batch": name.replace(".jsonl", ""), "judge_id": jid, **who, "harness": args.harness or "chat",
           "harness_version": None, "effort": rec.get("effort"), "plan": rec.get("plan"), "started_at": args.started_at or now,
           "source": "import (chat-only)", "reply_sha256": hashlib.sha256(raw.encode()).hexdigest()}
    os.makedirs(os.path.join(out, "results", jid), exist_ok=True)
    with open(os.path.join(out, "results", jid, name), "w") as f:
        f.write(json.dumps(hdr) + "\n")
        for g in got:
            r = byid[g["request_id"]]
            f.write(json.dumps({"judgment_id": f"{jid}-{r['request_id']}-0", "request_id": r["request_id"], "stage": r["stage"],
                                "concept_id": r["concept_id"], "field": "definition" if r["stage"] == "P2" else None,
                                "judge": {"id": jid, "type": "model", **who, "harness": args.harness or "chat", "judge_version": 1},
                                "run_index": 0, "order_seed": None, "prompt_version": r["prompt_version"],
                                "prompt_sha256": r["prompt_sha256"], "label": g["label"], "fields": g.get("fields", {}),
                                "notes": None, "confirmed": None, "valid": True, "attempts": 1, "raw_sha256": None,
                                "created_at": now}) + "\n")
        f.write(json.dumps(dict(hdr, finished_at=now)) + "\n")
    errs, warns, n = check(out, jid)
    for w in warns: print("WARNING", w)
    for e in errs[:50]: print("ERROR", e)
    print(f"stored results/{jid}/{name}: {len(got)} judgments; validator: {len(errs)} errors"); sys.exit(1 if errs else 0)

def judge_record(out, jid):
    p = os.path.join(out, "results", jid, "judge.json")
    return json.load(open(p)) if os.path.exists(p) else None

REQUIRED = ("judgment_id", "request_id", "stage", "concept_id", "judge", "run_index", "prompt_version", "label",
            "fields", "notes", "confirmed", "created_at")
WHO = ("provider", "model_name", "model_version", "model_reported")

def stats(args):
    """Fold every judge's results (results/<judge_id>/...) into definition agreement, per judge and per edition pair."""
    keys = {k["request_id"]: k for k in jload(args.keys or os.path.join(args.out, "keys", "anon.jsonl"))}
    if not keys: sys.exit("stats needs the PRIVATE key file: pass --keys PATH/anon.jsonl")
    files = glob.glob(os.path.join(args.out, "results", "*", "**", "*.jsonl"), recursive=True)
    if not files: sys.exit("no results/ yet: judges have not handed in")
    by = defaultdict(list)
    for f in files:
        for j in jload(f):
            if "_batch" in j or j.get("stage") != "P2" or j["request_id"] not in keys: continue
            k = keys[j["request_id"]]
            by[(j["judge"]["id"], tuple(sorted((k["A"], k["B"]))))].append((j["concept_id"], DEF_SCORE.get(j["label"]), j["label"]))
    for (judge, pair), xs in sorted(by.items()):
        cs = sorted({c for c, _, _ in xs}); sc = defaultdict(list)
        for c, s, _ in xs:
            if s is not None: sc[c].append(s)
        st = lambda cc: (lambda v: sum(v) / len(v) if v else None)([sum(sc[c]) / len(sc[c]) for c in cc if sc[c]])
        rec = judge_record(args.out, judge) or {}
        flag = " [FLAGGED: version unknown; not in primary panel]" if "version_unknown" in rec.get("flags", []) else ""
        print(judge + flag, pair, "mean definition score", bootstrap(cs, st, args.reps), Counter(l for _, _, l in xs).most_common())
    # TODO(draft): family-balanced panel label, Codex-only, leave-one-judge-out, self-preference DiD (AGREEMENT-METHOD.md 4.4)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    r = sp.add_parser("run"); r.add_argument("out"); r.add_argument("--edition", action="append", required=True)
    r.add_argument("--seeds", default=SEEDS_DEFAULT, help="the concept frame (default: data/seeds.tsv)")
    r.add_argument("--lexicon", help="reviewed canonical edition, lexicon/entries.jsonl (once it exists)")
    r.add_argument("--with-reference", action="store_true")
    r.add_argument("--seed", type=int, default=7); r.add_argument("--reps", type=int, default=2000)
    r.add_argument("--batch-size", type=int, default=50); r.add_argument("--concepts", help="file of concept ids to keep")
    r.add_argument("--private-dir", help="where keys, canonical drafts and tables go (keep out of public repos)")
    g = sp.add_parser("register", help="human judges only"); g.add_argument("out"); g.add_argument("--judge-id", required=True)
    g.add_argument("--type", choices=("human", "model"), default="human"); g.add_argument("--name")
    g.add_argument("--size", type=int, default=100); g.add_argument("--overlap", type=float, default=0.3)
    g.add_argument("--pool-size", type=int, default=50); g.add_argument("--trap-share", type=float, default=0.1)
    g.add_argument("--salt", default="agree-v1"); g.add_argument("--force", action="store_true")
    def ident(q, extra=True):
        q.add_argument("out"); q.add_argument("--provider", required=True, help="openai | anthropic | xai | google | ...")
        q.add_argument("--model-name", required=True, help='for example "claude-fable", "gpt-sol", "grok"')
        q.add_argument("--version", help='exact version as your harness states it, e.g. "5.2"')
        q.add_argument("--version-unknown", action="store_true", help="you cannot see your exact version (flags the run)")
        if extra:
            q.add_argument("--model-reported", required=True, help="the model string exactly as the harness or chat shows it")
            q.add_argument("--harness", help="codex | claude-code | chat | ..."); q.add_argument("--harness-version")
            q.add_argument("--effort"); q.add_argument("--plan"); q.add_argument("--batch-size", type=int, default=50)
    ident(sp.add_parser("join", help="join as a model judge, or resume"))
    ident(sp.add_parser("judge-id", help="print the versioned judge id only"), extra=False)
    x = sp.add_parser("export-packet", help="chat-only: one paste block"); x.add_argument("out"); x.add_argument("--judge-id", required=True)
    x.add_argument("--batch", help="batch number (default: next unfinished)"); x.add_argument("--write", help="write to this file")
    m = sp.add_parser("import", help="chat-only: store a pasted JSONL reply"); m.add_argument("out"); m.add_argument("--judge-id", required=True)
    m.add_argument("--batch"); m.add_argument("--reply", required=True, help="file holding the model's reply")
    m.add_argument("--harness"); m.add_argument("--started-at")
    e = sp.add_parser("build-exclusions", help="operator: rebuild requests/exclusions.json from the private key")
    e.add_argument("out"); e.add_argument("--keys", required=True)
    v = sp.add_parser("validate"); v.add_argument("out"); v.add_argument("--judge-id", required=True)
    s = sp.add_parser("stats"); s.add_argument("out"); s.add_argument("--reps", type=int, default=2000)
    s.add_argument("--keys", help="private keys/anon.jsonl")
    a = ap.parse_args()
    {"run": run, "register": register, "join": join, "judge-id": judge_id_cmd, "export-packet": export_packet,
     "import": import_reply, "build-exclusions": build_exclusions, "validate": validate, "stats": stats}[a.cmd](a)
