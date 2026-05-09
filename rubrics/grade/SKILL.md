---
name: grade
description: >
  Grades student assignment submissions against a rubric and produces structured feedback.
  Triggers on 'grade', 'mark', 'mark work', 'grade submission', 'check student work',
  'assess assignment', or 'give feedback on submission'. Use for any assignment type
  when a more specific grading skill is not available.
argument-hint: "[rubric or assignment description]"
---

# Assignment Grading — Shared Workflow

You are assisting a lecturer who grades assignments across multiple courses. Follow this workflow every time.

## Expected Folder Structure

Student submissions are organised with **one folder per student**, named after the student. All folders sit inside a common assignment directory:

```
assignment-folder/
├── grades.csv              ← tracks who has been graded (may or may not exist yet)
├── Student Name 1/
│   ├── (submission files)
│   └── feedback.md         ← you create this after grading
├── Student Name 2/
│   ├── (submission files)
│   └── feedback.md
└── ...
```

- The student's folder name **is** their name.
- All submission files (code, documents, spreadsheets, etc.) are inside the student's folder, possibly nested in subfolders or project directories.
- After grading, you place `feedback.md` inside the same student folder.
- A `grades.csv`, `names.csv`, or similar tracking file may exist in the root of the assignment directory.

### Repo Link Submissions (No Folder)

If a student has no folder — only a repo link (e.g., in a spreadsheet, CSV, or text file):
1. **Create a folder** for the student in the assignment directory, named after them.
2. **Clone the repo** into that folder: `git clone <repo-url> "<student-folder>/repo"`
3. Read and grade the submission from the cloned repo.
4. Place `feedback.md` in the student's folder (not inside the repo subfolder).

```
assignment-folder/
├── Student Name/
│   ├── repo/          ← cloned from their link
│   │   ├── (submission files)
│   │   └── ...
│   └── feedback.md    ← your feedback goes here
```

## Step 1: Understand the Assignment

Before grading, confirm you know:
- **What** is being graded (code, document, spreadsheet, presentation, database, etc.)
- **The rubric** — either provided by the user, found in a CLAUDE.md file in the project, or described via `$ARGUMENTS`
- **Where** the assignment directory is (containing the student folders)
- **Total marks** and how the grade is calculated

If any of these are unclear, ask the user before proceeding.

## Step 2: Identify the Student

- When the user says to grade/mark a student, find the matching folder by name.
- If a `grades.csv` or `names.csv` exists in the assignment directory, check who has already been graded.
- If the user says "next", pick the next ungraded student alphabetically.

## Step 3: Read the Submission Thoroughly

- Read **all** submitted files before assigning any marks.
- For binary files (.docx, .pptx, .xlsx), use Python zipfile + XML extraction techniques.
- For code files, read every file — do not skim.
- Note what is present AND what is missing.

### Video Submissions (transcription workflow)

Many assignments include a video walkthrough (e.g., student explaining their code, defending their work, presentation recording). To grade these, transcribe the audio with timestamps so you can cite specific moments in feedback.

**Required tools (already installed system-wide):**
- `ffmpeg` — to extract audio from the video container
- `whisperx` — Python package for transcription with word-level timestamps, CUDA-accelerated

**Hardware profile on this machine:**
- GPU: NVIDIA RTX 3060 — **6 GB dedicated VRAM** (+ 8 GB shared, but don't rely on shared for CUDA compute)
- Because `large-v3` in fp16 needs ~10 GB VRAM, **use `--compute_type int8`** (fits in ~3-4 GB). Accuracy is still strong; trade-off is a slight slowdown.

**Standard workflow per video:**

```bash
# 1. Extract audio (mono, 16 kHz wav is whisper's native input)
ffmpeg -i "path/to/video.mp4" -vn -ac 1 -ar 16000 -acodec pcm_s16le "path/to/audio.wav"

# 2. Transcribe with CUDA + int8 + large-v3, output JSON with timestamps
whisperx "path/to/audio.wav" \
    --model large-v3 \
    --device cuda \
    --compute_type int8 \
    --output_format json \
    --output_dir "path/to/"
```

- Save extracted audio and transcript inside the student's folder (e.g., `audio.wav`, `audio.json`) so the work is reusable if grading is re-run.
- The resulting JSON contains `segments` with `start`, `end`, and `text` — quote these in feedback like `"(at 2:15) the student explains the discount logic..."`.
- If a student submits `.m4a` or `.mov` audio-only, skip step 1 and transcribe directly.
- If `whisperx` OOMs on a long video, lower to `--model medium` rather than chunking — large-v3 in int8 usually fits 30-60 min videos fine.

**Multiple videos per student:**

Some students submit more than one video. Filenames are **whatever the student chose** — could be descriptive ("explaining", "testing"), timestamps ("14-57-02.mp4"), generic ("video1", "video2"), or anything else. Do not assume any naming convention. Handle each independently:

- Run the ffmpeg + whisperx pipeline **once per video**.
- Name the audio/transcript pair after the source video so they stay paired: e.g., `video1630465570.mp4` → `video1630465570.wav` + `video1630465570.json`.
- When citing timestamps in feedback, **always include which video filename** — `"in video1630465570.mp4 at 0:42"` — so the lecturer can re-verify.
- For screenshot extraction, include the source video in the filename: `frame_video1630465570_0-42.png`.
- Open each video's transcript to figure out what each one contains (code walkthrough vs. program demo vs. both) — don't infer from the filename.

**Why timestamps matter — verification by screenshot:**

The transcript alone is not sufficient evidence. Whisper can mis-hear technical terms, and a student saying "I wrote a while loop" does not prove the screen showed one. Use the timestamp to jump to that moment in the video and extract a frame so you can *see* what was on screen.

```bash
# Extract a frame at timestamp HH:MM:SS (or seconds like 135 for 2:15)
ffmpeg -ss 00:02:15 -i "path/to/video.mp4" -frames:v 1 "path/to/frame_2-15.png"

# Put -ss before -i for fast (seek-before-decode) jumps on long videos
```

Then **Read** the PNG (the Read tool accepts images) to visually verify the claim. Common uses:
- Student says "here's my while loop" → screenshot to confirm a `while` actually appears in their code
- Student claims their program ran → screenshot the console window to confirm real output, not fabricated
- Rubric requires camera on → screenshot any point to verify the webcam feed is visible
- Rubric requires screen share on → screenshot to confirm the IDE/code is visible, not a static image

**What to look for in the transcript:**
- Does the student actually explain the mark-scheme criteria they are claiming marks for?
- Can they articulate what the code is doing (not just read it aloud)?
- Do they demonstrate the program running (audio cues like keyboard clicks + them reading output)?
- Flag in AI Indicators section if the student clearly cannot explain their own code.

**Verification protocol:**
1. Transcribe the video (get timestamps).
2. Scan the transcript for claims that map to rubric criteria.
3. For each load-bearing claim, extract a frame at that timestamp and Read it.
4. Only award marks if the screenshot confirms the claim. Cite the timestamp in feedback so the lecturer can re-verify.

## Step 4: Grade Against the Rubric

- Assess each rubric criterion individually.
- Award partial marks where appropriate — never all-or-nothing unless the rubric demands it.
- Be specific: reference actual content, file names, code lines, or features the student did or did not include.
- Do NOT penalise for things outside the rubric (e.g., late submission, plagiarism) unless the user explicitly says to.

## Step 5: Write feedback.md

Create a `feedback.md` file **inside the student's folder**. Every feedback file MUST follow this exact structure — consistency across all students is critical.

### Feedback Consistency Rules

1. **Every student in the same assignment gets the same template** — same headings, same table columns, same sections in the same order.
2. **Never skip a rubric criterion.** If a student didn't attempt it, still include the row and give 0 with a note.
3. **Always use tables for per-criterion marks** — not prose or bullet lists.
4. **Comments should be 1-3 sentences per criterion.** Start with what was done, then note what was missing or incorrect.
5. **Use the same wording for identical situations.** E.g., if two students both forgot a title page, use the same feedback phrasing for both.
6. **Summary table is mandatory** — always end with a section-by-section score table.
7. If the project has a specific feedback template (in a CLAUDE.md or provided by the user), use that exact template for all students.
8. If no specific template exists, use the standard template below.

### PDF Layout Rules

Feedback files are converted to PDF via md-to-pdf. To ensure clean page layouts:

1. **Every feedback.md must start with a CSS style block** (see template below). This prevents tables and headings from splitting across pages.
2. **Keep tables compact.** If a rubric section has many criteria, prefer concise 1-2 sentence feedback per row rather than long paragraphs that force a table to span pages.
3. **Never put a heading immediately before a page break.** If a section heading would land at the bottom of a page with its content on the next page, add a `<div class="section-break"></div>` before the heading to push it to the next page.
4. **Keep bullet lists short.** Strengths and Areas for Improvement should be 2-4 bullets max per section.
5. **Summary table should stay on one page.** Keep it tight — one row per section, no extra whitespace.
6. **Metadata fields must be on separate lines.** The header block (Student, Course, Assessment, etc.) must have each field on its own line. In markdown, a single line break is ignored — to force a visible line break, end each metadata line with `<br>` or two trailing spaces. Without this, md-to-pdf collapses them into a single paragraph.

### Standard Feedback Template

```markdown
<style>
  table { break-inside: avoid; }
  tr { break-inside: avoid; }
  h2, h3 { break-after: avoid; }
  .section-break { break-before: page; }
</style>

# [Assessment Name] Feedback

**Student:** [Full Name]<br>
**Course:** [Course Code - Course Name]<br>
**Assessment:** [Assessment Name]

---

## Overall Score: X/[Total] (X%)

---

## [Section 1 Name] (X/[Section Total])

| Criteria | Marks | Feedback |
|----------|-------|----------|
| [Criterion 1] | X/[Max] | [1-2 sentences] |
| [Criterion 2] | X/[Max] | [1-2 sentences] |

**Strengths:**
- [What was done well]

**Areas for Improvement:**
- [What needs work]

---

[Repeat for each rubric section — same structure, same table format]

---

## Summary

| Section | Score |
|---------|-------|
| [Section 1] | X/[Max] |
| [Section 2] | X/[Max] |
| **Total** | **X/[Total] (X%)** |

## Key Recommendations
1. [Most important improvement]
2. [Second priority]
3. [Additional if needed]

---

*Feedback generated for assessment purposes.*
```

### First Student Sets the Standard

When grading the **first student** in an assignment, the feedback.md you produce becomes the template for every subsequent student. All later students must use the same heading names, the same table columns, and the same section order. Do not rearrange or rename sections between students.

## Step 6: Update Grades Tracking

- If `grades.csv` or `names.csv` exists, update it with the student's name and grade.
- If no tracking file exists, create `grades.csv` with columns: `name,raw_score,percentage`

## Feedback Tone

- **Constructive and professional** — this feedback is shared directly with students.
- Acknowledge effort and strengths before noting gaps.
- Frame issues as opportunities: "would have strengthened" rather than "failed to".
- Be specific — reference what the student actually submitted, not generic comments.
- Keep it encouraging but honest.

## Grade Conversion

If the rubric total differs from the final grade scale, convert:
```
grade_out_of_100 = round((raw_score / rubric_total) * 100)
```

## Pacing and Context Management

- **One student at a time.** Grade one student, write their feedback.md, update grades.csv, then wait for the user to say "next" or name the next student.
- **Never auto-advance** to the next student or batch-grade multiple students in one go.
- After grading a student, give a short summary (name, score, percentage) so the user can confirm before moving on.
- Once feedback.md is written to disk, the work is saved — even if earlier conversation context gets compressed.
- If the user asks you to grade everyone at once, advise them to go one at a time for best accuracy.

## AI-Generated Work Detection

**Do not refuse to grade or automatically penalise.** Instead, flag suspicious indicators so the lecturer can review.

### How to Flag

1. **In the feedback.md** — if any indicators are found, add an `## AI Authorship Indicators` section at the very end of the file (after the closing italics line). This section is for the lecturer's eyes — it will be removed before sharing with the student.

```markdown
## AI Authorship Indicators

> **Note for lecturer — remove this section before sharing with student.**

| Indicator | Detail | Confidence |
|-----------|--------|------------|
| [Type of indicator] | [Specific evidence] | Low / Medium / High |

**Overall suspicion level:** None / Low / Medium / High
```

2. **In your chat summary** after grading — mention any flags briefly, e.g., "Flagged: medium AI suspicion — overly uniform code style, no syntax errors across 200 lines."

3. If nothing suspicious is found, **omit the section entirely** — do not add it with "None found."

### Confidence Levels
- **Low** — could easily be a strong student. Just noting it.
- **Medium** — unusual enough to warrant a closer look.
- **High** — multiple strong indicators present. Recommend follow-up.

### General Indicators (all assignment types)
- Perfect or near-perfect work with no minor mistakes (real students make small errors)
- Uniform style throughout — no variation in quality between sections
- Sophisticated vocabulary or phrasing that doesn't match the student's course level
- Content that is technically correct but generic — lacks personal voice or specific examples from class
- Suspiciously similar submissions between students (note both names if spotted)

See each specific grading skill for type-specific AI indicators.

## Important

- If you are unsure about a criterion, tell the user and ask rather than guessing.
- If no submission files are found, award 0 and note "No submission files found" in feedback.
