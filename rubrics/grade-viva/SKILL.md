---
name: grade-viva
description: >
  Grades student viva (oral defence) recordings — sessions where a lecturer
  questions a student about previously submitted work and the student must
  defend, explain, or justify what they did. Triggers on 'grade viva',
  'mark viva', 'grade oral defence', 'mark oral exam', 'grade viva voce',
  'check viva recording', or 'assess viva'.
argument-hint: "[viva rubric or assignment context]"
---

# Viva Grading

Grades student viva recordings. Builds on the shared /grade workflow (folder layout, feedback.md template, grades.csv tracking, AI Authorship Indicators) — read that skill first. This document only covers what's different about vivas.

## What a viva actually is

A viva is **not** a walkthrough. The student is not narrating a tour of work they've prepared in advance — they are answering unscripted questions about work they have **already submitted**. Two consequences shape the entire grading approach:

1. **The source of truth is the original submission**, not the video. A viva tests whether the student can correctly describe, justify, and extend work that already exists on disk. To grade, you must read the submission first.
2. **There are at least two speakers** (lecturer + student) and the rubric usually only cares about what the **student** said. Without speaker labels, a transcript is hard to grade — half of it is the question, not the answer.

## Step 1: Read the original submission first

Before touching the viva recording, locate and read the work the viva is about:

- The submission usually lives in the same student folder, possibly in a subfolder like `submission/` or `original/`.
- Read it the way you would for a regular grading session — code, document, presentation, whatever it is.
- Note specifically: variable names, design choices, terminology used in comments, anything the student would need to be able to explain.

This pre-reading is what lets you tell "correct answer" from "rote answer" later. A student who cannot name their own variables on demand is a stronger AI signal than any prose tell.

## Step 2: Transcribe with speaker diarization

Follow the standard transcription workflow from /grade — extract audio with `ffmpeg`, transcribe with `whisperx` — but **add diarization** so each segment is labelled by speaker.

**One-time setup (per machine):**
1. Create a free HuggingFace account.
2. Accept the user agreement on the gated model: https://huggingface.co/pyannote/speaker-diarization-3.1 (and the segmentation model it depends on).
3. Generate a read-only access token at https://huggingface.co/settings/tokens.
4. Store it as `HF_TOKEN` in the environment, or pass it on the command line each time.

**Per-viva pipeline:**

```bash
# 1. Extract audio (same as standard /grade workflow)
ffmpeg -i "path/to/viva.mp4" -vn -ac 1 -ar 16000 -acodec pcm_s16le "path/to/audio.wav"

# 2. Transcribe with diarization. Vivas are almost always exactly 2 speakers,
#    so locking min/max to 2 improves accuracy and speed.
whisperx "path/to/audio.wav" \
    --model large-v3 \
    --device cuda \
    --compute_type int8 \
    --diarize \
    --hf_token "$HF_TOKEN" \
    --min_speakers 2 \
    --max_speakers 2 \
    --output_format json \
    --output_dir "path/to/"
```

The output JSON gains a `speaker` field on each segment (`SPEAKER_00`, `SPEAKER_01`).

**Identify which speaker is which:**
The diarization labels are arbitrary — `SPEAKER_00` may be the lecturer or the student. Resolve this once, then use the labels consistently:

- The first segment is almost always the lecturer opening the session — listen to (or read) the first ~30 seconds.
- The lecturer typically asks more questions; the student typically gives longer answers. Run a quick check: count segments per speaker and average length per speaker.
- If still ambiguous, extract a frame at any timestamp and check who's speaking on camera.

Once identified, **rewrite the transcript JSON** (or work from a derived file) so labels read `[Lecturer]` and `[Student]`. Save this as `audio_diarized.txt` or similar inside the student folder so the work is reusable.

**If a session has more than 2 speakers** (e.g., second examiner, group viva): set `--min_speakers` / `--max_speakers` to the actual count and resolve each label individually. Group vivas are messy — diarization regularly merges similar voices; spot-check a few timestamps before grading.

## Step 3: Structure the transcript as Q&A

A flat speaker-labelled transcript is still hard to grade. Restructure it into question-answer pairs so each rubric criterion can be tied to a specific exchange.

For each question the lecturer asks, capture:

```
Q1 [00:42 – 00:51]  Lecturer: "Can you walk me through how your CalculateTax method works?"
A1 [00:51 – 01:18]  Student: "Sure, so I... I take the amount and multiply it by 0.15..."
                    [pause 4s] "...and I think it returns a decimal."
```

- Note pauses longer than ~3 seconds in `[pause Ns]` — they are evidence.
- Note hedging language verbatim ("I think", "I'm not sure", "let me check") — also evidence.
- Note any moment the student reads aloud from notes or scrolls back through their own code — these undercut "explains own work" criteria.

You don't have to format the whole transcript this way. Format the exchanges that map to rubric criteria. Save as `viva_qa.md` inside the student folder.

## Evidence Tiers — what counts as a correct answer

A viva measures **understanding**, not recall. Use this hierarchy when judging an answer:

| Tier | Evidence | Awards |
|------|----------|--------|
| **A — Correct + applied to own work** | Student answers correctly AND references their own variable names, file structure, or specific design decisions accurately | Award rubric marks normally — they understand what they submitted. |
| **B — Correct in general, vague on own work** | Student gives a textbook-correct answer but can't tie it to their own code (e.g., "validation uses a while loop" without naming the actual variable being validated) | Award **partial** marks — they know the concept but ownership is unclear. |
| **C — Correct under prompting only** | Student gives a wrong/incomplete first answer, lecturer prompts ("are you sure? what about X?"), student then corrects | Award **partial** marks — credit the recovery, but a student who fully understood wouldn't have needed the prompt. |
| **D — Wrong, even under prompting** | Student maintains an incorrect answer about their own work, or gives up | Award **0** for that criterion. |
| **E — Won't engage** | Student says "I don't remember", "I'd have to check", or stays silent on a question that is core to the submission | Award **0** and flag in AI Authorship Indicators. |

### Common mistakes this prevents

- **Confident-wrong fallacy:** A student who answers smoothly and at length but is *wrong* about how their own code works is not better than a student who hesitates and gets it right. Score on correctness, not delivery.
- **Recovery-erases-the-gap fallacy:** If a student needed three lecturer prompts to arrive at a correct answer, they did not demonstrate independent understanding. Document the prompting in the feedback so the lecturer can re-verify.
- **Articulate-but-rote fallacy:** "I implemented input validation using a while loop with a TryParse check" sounds correct, but if the student also can't say *which variable* they're validating or *what file* the loop is in, the answer is at Tier B at best.
- **Silence-isn't-zero fallacy:** Sometimes silence is the student thinking; sometimes it's the student stalling. The transcript timestamps tell you which — a 30-second pause followed by a topic change is not the same as a 5-second pause followed by a correct answer.

## What to look for that's specific to vivas

These signals don't appear in walkthrough recordings — they only emerge under questioning:

- **Cannot name own variables, methods, or files without scrolling back to look.** Strong AI-authorship signal.
- **Asks the lecturer to repeat or rephrase questions about basic functionality.** A student who wrote the code understands the question on first hearing.
- **Confidently misnames their own design choices.** E.g., calls their `for` loop a `while` loop. Suggests they did not write it.
- **Cannot extend or modify on the spot.** Lecturer asks "what would you change to handle negative numbers?" — a real author can answer in seconds; a non-author often cannot answer at all.
- **Defaults to general principles when asked specifics.** Question: "why did you choose to put validation in a separate method?" Answer: "Separation of concerns is important..." — generic answer to a specific question is a tell.
- **Hedging clusters.** Three or more "I think" / "I'm not sure" / "I believe" within a single answer is unusual for genuine authors of their own work.

## Cross-referencing answers against the submission

For every load-bearing claim the student makes, check the original submission:

1. Student says "I used a `while` loop for validation" → grep the submission for `while` and confirm.
2. Student says "the `CalculateTax` method takes the discounted amount and returns 15%" → open the file and check the actual signature and body.
3. Student says "I tested with values from 50 to 5000" → check whether test code or sample inputs reflect that.

Where the student's claim **disagrees** with the submission, the submission wins for "did the work get done" rubric criteria, but the **disagreement itself** lowers "explains own work" criteria and goes in AI Authorship Indicators.

## When there is no screen-share

Many vivas are pure conversation — no IDE visible, possibly no camera. In that case you cannot extract verification frames the way /grade describes for walkthroughs. Adjust:

- **Skip frame extraction.** It will not produce evidence.
- **Lean harder on the submission as source of truth.** Every claim the student makes is checked against the actual files, not against a screenshot.
- **Camera-required rubric items** (e.g., "student visible on camera throughout") still need a frame check if any video stream exists. If there is genuinely no video at all, note this in feedback and award per the rubric's audio-only provision (or 0 if the rubric required camera).

## Feedback Template for Viva

Use this exact structure for every student.

```markdown
<style>
  table { break-inside: avoid; }
  tr { break-inside: avoid; }
  h2, h3 { break-after: avoid; }
  .section-break { break-before: page; }
</style>

# [Assessment Name] — Viva Feedback

**Student:** [Full Name]<br>
**Course:** [Course Code - Course Name]<br>
**Assessment:** [Assessment Name]<br>
**Viva Recording:** [filename, duration]<br>
**Submission Reviewed:** [list submission files cross-referenced]

---

## Overall Score: X/[Total] (X%)

---

## [Section 1 Name] (X/[Section Total])

| Criteria | Marks | Tier | Evidence (timestamp + quote) |
|----------|-------|------|------------------------------|
| [Criterion] | X/[Max] | A/B/C/D/E | "(at 2:15) student said '...'; cross-checked against [file] — confirms/disagrees" |

[Repeat per rubric section]

---

## Summary

| Section | Score |
|---------|-------|
| [Section 1] | X/[Max] |
| [Section 2] | X/[Max] |
| **Total** | **X/[Total] (X%)** |

### Strengths
- [What was demonstrated clearly under questioning — quote a specific moment]

### Areas for Improvement
- [Where the answer was thin or wrong — quote and reference the submission]

---

*Feedback generated for assessment purposes.*
```

### Tier Values (column 3)

- **A** — Correct and applied to own work
- **B** — Correct in general, vague on own work
- **C** — Correct under prompting only
- **D** — Wrong even under prompting
- **E** — Refused / silent on core question

## AI Indicators for Vivas

Watch for these in addition to the general indicators in the shared /grade skill. A viva is the single most reliable surface for AI-authorship signal — most of these cannot be faked in real time:

- **Cannot explain own naming choices.** "Why did you call this method `ProcessFinal`?" → "Um, I don't really remember why."
- **Cannot point to specific lines in own code.** Answers describe the program in the abstract but never reference line numbers, file names, or method names without scrolling/searching.
- **Long pauses before basic questions.** A 10+ second pause before "what does your main loop do?" is unusual for a real author.
- **Smooth answers to conceptual questions, weak answers to specific questions.** AI explains concepts well; only the actual author knows specifics.
- **Inability to predict program behaviour on a new input.** "If the user enters -5, what happens?" — a real author can simulate it; a non-author guesses or refuses.
- **Disagreement between answer and submission.** Student says the program does X; the code does Y. Quote both.
- **Reading-aloud cadence.** Long, complete, well-formed sentences with no hesitation, especially on technical topics, can indicate the student is reading from notes or a generated script. Listen for paper rustle / scroll noise.

Score these in the AI Authorship Indicators section per the shared /grade format. **High** confidence is appropriate for any single one of: confident misnaming of own code, refusal to engage with own work, or sustained disagreement between answers and submission.

## Pacing

Same as shared /grade workflow: one student at a time, write feedback.md, update grades.csv, wait for "next". Vivas typically take longer to grade than walkthroughs because of the cross-referencing step — budget accordingly.

## Important

- If the recording has no audio, no diarization output, or is corrupted, do not award marks based on the submission alone — note "Viva recording could not be processed" in feedback and ask the user how to proceed.
- If the lecturer's questions are missing from the rubric (e.g., the rubric just says "viva quality" without listing what was asked), ask the user for the question list before grading. Without it, every criterion is a guess.
