# Instructions for human judges

Thank you for helping. This page is for people. You don't need to write code, upload files, or know anything about the models.

## What the study is

NanoLex is a descriptive dictionary of nanomedicine: nanomaterials and carriers, formulations and named products, techniques, and the biological targets they act on. It covers 977 terms. It says what each term **is**. It never explains how to make or dose anything, and it never says whether a product works. Several AI models each wrote their **own** version of the dictionary, without seeing the others or the first NanoLex written in 2024–2025. We want to know how far they agree, and agreement has to mean **in meaning**, not in wording.

AI judges do most of the comparing. **Your job is to tell us whether the AI judges can be trusted.** You'll see pairs of entries side by side, written by models you won't be told the names of, and say how their meanings relate. We then compare your answers with the AI judges' answers, and with other people's.

There are no right answers we're hoping for. An honest "I'm not sure" is far more useful than a guess.

## How much time it takes

- About **100 items**, or **50** if you prefer. Most take one to two minutes, so plan on about **3 to 5 hours in total**, split into as many sittings as you like.
- About a third of your items are also shown to other judges, so we can see how far people agree with each other. The rest are yours alone. Your sample is drawn at random for you.

## How to start

1. Open **Claude Code** or **Codex** in a copy of this repository (Bear will send the link and the run folder name).
2. Type: **"I'm a human judge."**
3. The assistant asks your name and an id (for example `human-jsmith`), and whether you want 100 items or 50. It then draws your sample.
4. It shows you **one item at a time**. Answer in your own words, as you would to a colleague: "B is just a narrower version of A", say, or "these are about completely different things". The assistant turns that into one of the labels below, **reads it back to you**, and saves it only when you confirm. Your own words are saved alongside, exactly as you said them.
5. When you finish, or whenever you stop, it checks your answers and saves them under your name.

The assistant will not suggest an answer before you have given yours. If it seems to, tell it to stop.

## Pausing and resuming

- Say **"pause"** at any time. Everything you have confirmed is saved.
- To resume, open Claude Code or Codex in the repository again and say **"I'm a human judge, resuming as human-jsmith"** (with your id). It picks up at your next unanswered item.
- You can change an earlier answer: say "go back to item 12".

## The labels, with worked examples

Most items show **two definitions** of the same concept, labelled A and B. Pick the relation between their **meanings**:

| Label | Meaning | Worked example |
|---|---|---|
| **Equivalent** | Same thing, same essentials. Either could replace the other. | *[Worked example: placeholder, to be written by Nik Bear Brown]* |
| **A narrower** or **B narrower** | Same thing, but one covers strictly less. | *[Worked example: placeholder, to be written by Nik Bear Brown]* |
| **Overlapping** | Same thing, different emphasis. Neither contains the other, and nothing contradicts. | *[Worked example: placeholder, to be written by Nik Bear Brown]* |
| **Conflicting** | Same thing, but they contradict each other on a fact. | *[Worked example: placeholder, to be written by Nik Bear Brown]* |
| **Different sense** | They're about different things. | *[Worked example: placeholder, to be written by Nik Bear Brown]* |
| **Not sure** | You can't tell, or you don't know the concept well enough. | Use it freely. It is counted as "no answer", not as a wrong answer. |

Some items ask something slightly different. The assistant explains each kind when it first comes up:

- **Same sense?** Several short statements of what a concept means. Which ones are about the same thing?
- **Same name?** A list of alternative names or related concepts. Which ones name the same thing? Something broader or narrower is **not** the same thing. *[Worked example: placeholder, to be written by Nik Bear Brown]*
- **Relation type.** Two models link the concept to the same other concept in different ways. *[Worked example: placeholder, to be written by Nik Bear Brown]* Are those the same kind of link, compatible ones, reversed (one says "kind of", the other "has kinds"), or in conflict?

## Two rules that always apply

- **Describe, don't advise.** You are judging whether two dictionary definitions mean the same thing. Please don't judge whether a material, product or treatment works or is safe, and don't add how to make or dose anything. If the assistant is asked for medical advice, it won't give it during the session.
- **No personal details.** Never mention anyone's health, including yours or anyone you know, in your answers or comments. If an item seems to contain such details, say "Not sure", tell the assistant "possible personal information", and don't repeat it.

## A few tips

- Judge **meaning**, not writing quality. A longer or more polished definition is not more correct.
- Don't look things up to decide which one is *right*. We only ask whether they *agree*. (Looking up a term you don't know at all is fine, and so is "Not sure".)
- Don't talk with other judges about specific items until everyone has finished.

## Your answers and your name

Your answers are saved in the repository under your id, together with your name as the author, so your contribution is credited. Your comments are stored word for word. If you would rather be credited by initials only, tell the assistant at the start.
