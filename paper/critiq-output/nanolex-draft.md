# NanoLex: A Protocol for Auditable Nanomedicine Terminology

*Rough methods manuscript, 27 November 2026. The public artifact is a terminology project, not a technical synthesis or treatment guide. No independent edition comparison or expert review result is reported.*

> **Drafting or judging an edition?** Start with [the role instructions](../../AGENTS.md). Do not consult other editions, the withheld original, or paper materials while participating in a blind round.

## Abstract

A specialized vocabulary can appear coherent even when its entries have no recoverable evidence history. NanoLex proposes a rebuild from an unchanged names-only seed frame. Its public manifest contains 977 seeds and provides a versioned replication kit. The protocol separates coverage, semantic agreement, and independent source verification. Editions are frozen before comparison; reviewers audit supported claims against allowed sources instead of presuming that matching definitions are correct. A proposed bibliographic test would ask whether validated synonyms improve discovery of relevant records. The draft makes no claims about clinical validity or the correctness of any seed.

## Introduction

A vocabulary should distinguish whether an entry exists, whether independent people or systems mean the same thing by it, and whether a statement is supported by evidence. A single polished model glossary gives no direct answer to the last two questions. NanoLex addresses a narrower problem: how to make terminology decisions and provenance inspectable without representing an unreviewed original as authoritative.

We ask three questions. How often can a fixed name be classified or resolved without an ambiguity flag? When eligible editions agree on a meaning, does independent source review support the claims they share? And what changes if reviewed synonyms, rather than all generated variants, are used to discover bibliographic records? These outcomes do not imply health benefits, safety, or operational research capability.

## Materials and methods

### Seed frame and audit boundary

The [public manifest](../../data/source-manifest.json) records 977 cleaned headings taken from the legacy glossary as names only. Names are not necessarily unique concepts: unresolved spellings, aliases or ambiguous names can persist. Retain IDs and record exclusions and normalization rules; do not remove items from the denominator because they are hard to resolve. An older model-written edition is kept outside this study environment and will not be used as truth. The present paper did not open or copy it.

### Independent editions and review

The [replication kit](../../replication/README.md) standardizes inputs, entry shape and evidence bookkeeping. Isolate drafters from each other and the withheld legacy text; record served model/version, source-access policy, completion and abstention. Freeze outputs before permitting cross-edition access. A structural pass checks completeness and evidence pointers; it does not certify a claim. Separate exact normalized agreement, judged semantic agreement and source verification.

An independent comparison pass aligns meanings, not merely identical spellings, and reports both-present, one-present, and neither-present before estimating agreement. Randomize side and order and blind the judge to provenance where possible. Do not have a drafter evaluate its own output. Label ambiguous, missing and not elicited separately. Stratify by term form and record judge reversals under swapped order. Ask independent reviewers to check the evidence supporting each proposed claim; retain unresolved items outside the reviewed edition rather than treating majority preference as verification. Distinguish reviewer calibration from evaluation on held-out concepts.

### Proposed bibliographic evaluation

[ASSUMPTION: a permissioned or freely reusable fixed bibliography can be assembled.] Define relevance at the paper–topic level with a rubric and independent reference reviewers. On one fixed metadata snapshot, compare an exact-title/abstract keyword baseline with reviewed aliases at the same shortlist length. Keep topic families separate across development and testing; log versions, source fields, and missing abstracts. Count precision at a preregistered shortlist length and additional relevant records within a pooled judged set, not corpus-wide recall. Record false matches by ambiguity class. This is a metadata-discovery experiment only, with no patient data, intervention decisions, population inferences, or applied biological procedures.

## Results status

| Artifact or outcome | Status |
|---|---|
| Names-only seed manifest | Available, 977 seeds; does not establish valid concepts. |
| Replication and proposed agreement protocol | Available; design only. |
| Complete independent editions and expert-adjudicated comparison | [NEEDS: freeze and document completed editions, confirm sampling frame and reviewer availability.] No agreement or accuracy result claimed. |
| Bibliographic benchmark | Proposed, not collected. |

## Discussion

A term can attract agreement because reviewers share a convention or because models share sources. Conversely, disagreement may preserve a real boundary between different concepts. Either case needs claim-level evidence inspection. The unusual seed frame limits coverage, and an apparently comprehensive version could still exclude vocabulary uncommon in the original glossary. Report missing concepts and contested categories separately before making any claim of added value. Existing alternative vocabularies are relevant comparators, not universal ground truth. [CITATION NEEDED: primary documentation for external terminology comparators and a verified crosswalk method.]

## Data and disclosures

Only public inventory documentation and the replication kit are cited for protocol claims. Private editions, keys, and restricted source text are not part of this manuscript. [NEEDS: agreement-plan reconciliation, assessment of human reviewer study requirements, author/funding disclosures, and license review before submission.] NanoLex is terminology research and makes no product, safety or efficacy claims.
