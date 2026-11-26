# Help build NanoLex

There is no draft yet, so this is a good time to shape the method. We're looking for collaborators who can draft or check independent editions, review entries in their field, or help write the paper. You don't need to review the whole project to help.

## Keep independent editions independent

If you are drafting an edition, with a model or by hand, follow [AGENTS.md](AGENTS.md) and the [replication kit](replication/README.md) only. Never open the initial lexicon, another model's run, judging results or the reviewed edition while you draft, and hand your run in privately: never commit drafts, source bundles, run folders or judging keys to this repository. If you are judging, follow the [judging kit](replication/judging/README.md). Everything below is for other kinds of help, or for after you have handed in.

## Getting started

1. **Read first.** Read the [README](README.md), the [seed list's provenance](data/README.md) and the [rules for the reviewed edition](lexicon/README.md).
2. **Choose one thing to do.** Pick one row from [Pick a way to help](#pick-a-way-to-help), and narrow it to one rule, one set of terms or one source.
3. **Email Nik** at bear@bearbrown.co with the subject "NanoLex: contributor". Include:
   - your name and your GitHub username;
   - the contribution you chose, and exactly what you will look at;
   - whether you hope to become an author, or want to help without authorship.

   Nik will add you to the repository as a collaborator. GitHub then emails you an invitation, which you must accept within seven days.
4. **Claim the work.** Check the [open issues](https://github.com/nikbearbrown/nano-lex/issues) so nobody else is doing it, then [open an issue](https://github.com/nikbearbrown/nano-lex/issues/new) that says what you are taking on, and assign it to yourself.
5. **Make a branch** named `your-name/short-description`. Don't commit to `main`.
6. **Do the work,** one piece of work per branch.
7. **Open a pull request.** Say what you changed, how you checked it, and where you used an AI tool. Write "Closes #" and your issue's number, and request a review from `nikbearbrown`.
8. **Respond to the review** on the same branch until it is agreed and merged.
9. **Present your work** at Nik's Tuesday meeting or his office hours. Cover what you set out to do, what you did, what you found and the evidence for it, and what comes next. Do this each time you attend, even when the work is unfinished. Nik sends the meeting details when he adds you.
10. **Keep your record.** Your issues and pull requests are the record of what you did. The paper's contribution statement is drawn from them.

## Pick a way to help

| Contribution | Where to start | What to send |
|---|---|---|
| **Draft an independent edition** | [AGENTS.md](AGENTS.md), then the [replication kit](replication/README.md) | A complete run, handed in privately as the kit says. Name the provider, model and exact version you actually used. |
| **Review the method** | [Seed provenance](data/README.md) and the [replication kit](replication/README.md) | Name the rule (seed selection, entry shape, scope flags) and what could go wrong, with an example, and propose a fix. |
| **Judge agreement** | The [judging kit](replication/judging/README.md) | Judgments made as the kit says, by a person or by a model that drafted none of the entries it judges. |
| **Review entries in your field** | [Rules for the reviewed edition](lexicon/README.md) | Once editions exist: check a set of claims against their cited sources and record each decision with the evidence. |
| **Place it against existing vocabularies** | Established vocabularies such as eNanoMapper or the NanoParticle Ontology | How they name and scope these terms, and what this lexicon adds or gets wrong. Primary sources, with links. |
| **Write part of the paper** | This README's [Abstract](README.md#abstract) and [What needs to be done](README.md#what-needs-to-be-done) | Once results exist: a section draft or a substantive revision, in a pull request. |
| **Recommend a journal Northeastern covers in full** | [Below](#recommend-a-journal-northeastern-covers-in-full) | One journal and a runner-up, with the evidence that section asks for. Every contributor does this once. |

## Rules for this lexicon

- **Describe terms, never advise.** Entries describe what a term means. No medical advice, and no claim that a product works or is safe.
- **Keep the initial lexicon out.** Its text never enters this repository, an issue or a pull request.
- **Cite, don't copy.** Link the source for every claim; don't paste source text into the repository.

## Recommend a journal Northeastern covers in full

Northeastern's library has agreements that pay the open-access fee for papers whose corresponding author is at Northeastern. Nik is the corresponding author, so they apply.

1. Read the abstract. Note the field, the method, the kind of article (research, resource, dataset) and its likely length.
2. Read [Open access publishing at Northeastern](https://library.northeastern.edu/resource_discovery/open-access-publishing/) and search [SciFree for Northeastern](https://search.scifree.se/northeastern).
3. Keep only journals whose fee is covered in full. A discount doesn't count, and some publishers cap the number of articles they cover each year.
4. Check three journals on the publisher's own site: scope, whether they take this kind of article, two or three recent papers close to this one, their policy on public drafts and preprints, and their practical limits.
5. [Open an issue](https://github.com/nikbearbrown/nano-lex/issues/new) titled "Venue recommendation: " and the journal's name, with one journal, a runner-up, your reasons, your links and the date you checked.

Confirm coverage yourself on the library's or the publisher's page. Don't rely on memory or on an AI tool's answer, because the agreements change.

## Credit and what we expect from authors

The author list isn't decided yet. We follow [Yale's guidance on authorship](https://provost.yale.edu/policies/academic-integrity/guidance-authorship-scholarly-or-scientific-publications). Under it, an author has done **all four** of these:

1. **Contributed to a component of the work:** its conception, design, conduct, analysis, or interpretation of at least part of the results.
2. **Helped write the paper:** drafted part of it, or revised it for substance, not just copy edits.
3. **Approved the final version** before submission.
4. **Agreed to be accountable** for the work, including helping resolve questions about its accuracy or integrity.

Running a model to draft an edition, or judging, on its own earns acknowledgment by name. Raise authorship early, and again if your role changes. Disclose any AI help, and check every claim and citation an AI tool gave you.
