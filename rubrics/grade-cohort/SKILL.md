---
name: grade-cohort
description: >
  Coordinates a parallel multi-agent grading pipeline for a whole student
  cohort across ANY rubric-driven assessment — code, web apps, documents,
  spreadsheets, presentations, databases — across any course. Spawns
  teammates, runs calibration, audits outliers, and writes final feedback
  files. Use when grading more than ~5 submissions for the same assessment
  and you want parallel throughput with quality-drift control. Triggers on
  'grade the cohort', 'grade the whole class', 'parallel grade', 'team
  grade', 'spawn graders', 'batch grade students', 'grade everyone'. Use
  ALONGSIDE the type-specific grading skills (grade-code / grade-document
  / grade-spreadsheet / grade-presentation / grade-database / grade-video)
  — this skill orchestrates them; it does not replace them. The brief,
  rubric, taught-patterns file, and per-type skill are all gathered in
  the configuration block at the start of each run, so the skill is
  course- and assessment-agnostic.
argument-hint: "[course code + assessment ID, or brief path]"
---

# Cohort Grading Pipeline

Orchestrates parallel multi-agent grading for any rubric-driven assessment
across any course. The lead (you) handles pre-flight, calibration, audit,
and finalisation; spawned teammates do the per-student rubric scoring. The
workflow is identical whether you're grading C# programs, ASP.NET web
apps, research papers, Excel workbooks, or Access databases — only the
per-type skill that teammates invoke and a few configuration knobs
change.

## Configuration block — gather these before Step 0

Run this block first. The lecturer answers, you record the answers in a
working file (e.g. `_step2/run_config.md`) that is passed to every
spawned teammate so the cohort-wide settings are uniform.

| Question | Example answers |
|----------|-----------------|
| **Course code + assessment ID** | `CPRG1205 A4`, `CWEB1205 A2`, etc. |
| **Brief / spec file path** | `assessment4/CPRG1205-CW-04.pdf`, etc. |
| **Submissions root directory** | `assessment4/` |
| **Roster file** | `students.txt` at project root |
| **Rubric — total marks + locked criterion names + sub-point weights** | from the brief |
| **Assessment type** | `code` / `document` / `spreadsheet` / `presentation` / `database` / `web-app` / `mixed` |
| **Per-type grading skill to invoke** | `grade-code` / `grade-document` / `grade-spreadsheet` / `grade-presentation` / `grade-database` |
| **Is a video walkthrough required?** | `yes` (use `grade-video`) / `no` / `optional` |
| **Buildable artefact?** (something to compile / run / open) | `yes — dotnet build` / `yes — open in browser` / `yes — open in Access` / `no — read-only document` |
| **Path to `taught_patterns.md`** | project root or assessment subfolder |
| **Lecturer-style references** (hand-graded `feedback.md` from prior assessments) | 1–2 paths, contrasting scores |
| **Per-deliverable deduction scale** | e.g. `-1 per missing standard deliverable`, or "set at finalisation" |
| **Viva-window framing for held grades** | `"provisional pending viva window"` / `"viva opt-in"` with deadline |
| **AI-flag canonical anchor** | `"Low" when fingerprints counter-AI` / `"None" only on positive AI evidence` |
| **Naming convention for student folders** | matches `students.txt` spelling exactly |

If any answer is unknown, **stop and ask the lecturer** before spawning
anything. Don't guess — the failure modes are silent and consequential
(wrong skill invoked → tier rules wrong; missing video config → teammates
each try to transcribe → GPU contention; missing taught_patterns →
convergent false-negatives on AI authorship).

## Per-assessment-type adaptations

Workflow is identical across types; the differences sit in three places:

| Concern | Code (CPRG1205) | Web app (CWEB1205) | Document | Spreadsheet | Database | Presentation |
|---------|-----------------|--------------------|---------|-------------|----------|--------------|
| Per-type skill | `grade-code` | `grade-code` (HTML/CSS/JS/ASP.NET) | `grade-document` | `grade-spreadsheet` | `grade-database` | `grade-presentation` |
| Buildable artefact? | Yes — `dotnet build` / `python -m py_compile` | Yes for ASP.NET (`dotnet build`); no for static HTML/CSS/JS (smoke-test with `python -m http.server`) | No (just open + verify not corrupt) | No (open in Excel) | Yes — open `.accdb` / dry-run SQL | No (open in PowerPoint) |
| Walkthrough video typical? | Yes (mandatory in CPRG1205) | Often (mandatory if specified) | Rare | Sometimes | Sometimes | Rare (presentation IS the artefact) |
| Evidence-citation format | `file:line`, method name | `file:line`, DOM selector, route | page + paragraph + quote | sheet + cell + formula | table/query/form name + field | slide # + element + on-slide text |
| Common untaught patterns to watch | TryParse/out, generic collections, base-typed refs | async/await, fetch, ES6 destructuring, jQuery | unfamiliar citation styles, polished prose w/ no hedging | array formulas, INDEX/MATCH if VLOOKUP taught, pivot tables | subqueries, joins beyond INNER, parameterised queries | embedded media if not taught, transitions/animations beyond basic |
| Cosmetic-vs-functional examples | renamed methods, output typos | class-name typos, indentation | font choice, heading style | column width, cell colour | table-name plurals, view layout | slide-number font, theme colour |

When the configuration block answers an ambiguous case ("is this static
HTML/CSS or ASP.NET?", "is this a research paper or a report?"), use the
table to pick the right per-type skill and the right Phase 7 build/open
check. If the answer is genuinely "mixed" (e.g. a code submission with a
written design document), spawn each teammate with BOTH per-type skills
loaded.

## When to use this skill

- Grading **5+ submissions** for the same assessment
- The assessment has a clear rubric (not open-ended creative work)
- You have access to the per-type grading skill for the work
- The cohort has enough variation that parallel grading saves real time

## When NOT to use this skill

- **1–4 submissions** — just use the per-type skill directly, one at a time
- **No rubric** — there's nothing for teammates to converge on
- **You are the only grader the lecturer trusts on this cohort** —
  don't introduce parallel agents into work that requires your eye
- **First time grading this assessment with no calibration material** —
  hand-grade 1–2 students yourself first, those become anchors

## Required prerequisites (verify before Step 0)

1. **Brief / assessment specification** at a known path
2. **Rubric** — either inside the brief or in a separate file. Locked
   criterion names, sub-point weights, total marks
3. **Student roster file** (typically `students.txt` at project root, one
   name per line)
4. **Submissions directory** with one folder per student, named after the
   student (or a zip you can extract into that shape)
5. **Per-type grading skill installed** (`grade-code`, `grade-document`,
   `grade-spreadsheet`, etc.) — the cohort skill defers all rubric judgment
   to these
6. **`grade-video` skill installed** if videos accompany the submissions
7. **`taught_patterns.md`** at the project root — see below
8. **Project `CLAUDE.md`** with grading conventions, AI authorship policy,
   per-student baselines (lecturer-only context)

### `taught_patterns.md` — the single biggest gap-closer

Non-negotiable for any assessment where students could plausibly use
external tools (AI assistants, tutorials, copy-paste from older students)
to produce work above their demonstrated baseline. The file lists
**TAUGHT** vs **NOT-TAUGHT** patterns for the assessment in question.

The shape of the patterns varies by course. Examples:

**For an introductory C# course (CPRG1205):**
- TAUGHT: `Convert.ToInt32`, standard `while (condition)`, basic `try/catch`,
  `virtual`/`override`, `: base(...)` chaining, same-name + `this.field = parameter`
- NOT-TAUGHT: `TryParse` / `out` / `while(true)+break`, `\n` escape
  sequence, differing field/parameter names to avoid `this.`, `List<T>`
  with `.Add()`, `Vehicle car1 = new Car(...)` base-typed-reference
  polymorphism, `Console.ReadKey()` / "press any key" pattern

**For an introductory web dev course (CWEB1205 / similar):**
- TAUGHT: semantic HTML5 tags, basic CSS selectors + flexbox or grid (one
  of), inline event handlers, `document.getElementById`, basic form
  validation, ASP.NET `runat="server"` controls, code-behind event handlers
- NOT-TAUGHT (typical examples — confirm per-cohort): `async`/`await`,
  `fetch()` or AJAX, ES6 destructuring/spread, arrow functions in
  load-bearing places, jQuery, CSS preprocessors, framework patterns
  (React/Vue), `async`/`await` in C# code-behind, `LINQ` queries,
  database access patterns the lecturer hasn't covered

**For a research-paper assessment:**
- TAUGHT: APA citation format, in-text citations with author + year, basic
  literature review structure, paragraph topic sentences
- NOT-TAUGHT (typical): unfamiliar citation styles (Vancouver, Chicago)
  appearing without explanation, suspiciously polished prose with zero
  hedging, references to obscure journals the student wouldn't know,
  perfect APA formatting from a student whose prior work didn't use it

**Why this matters:** spawned teammates have access to the brief, the
rubric, and the student's submission — but they have **no idea what was
taught in class**. Without a taught-patterns reference, teammates flag AI
authorship only on positive evidence ("polished work → suspicious") and
miss the much stronger negative evidence ("used pattern X that isn't on
the syllabus, by a student who has never used X before"). The lecturer is
the only person who can author this file.

If `taught_patterns.md` is missing when this skill runs, **stop and ask
the lecturer to author it** before proceeding. Don't fall back to "guess"
mode — the failure mode is silent and consequential (false negatives on
AI authorship). For a new course / new assessment the lecturer can write
it in 15-30 minutes; that's the cheapest investment in the whole
pipeline.

## STEP 0 — PRE-FLIGHT (lead only, before any teammates spawn)

1. **Verify prerequisites** (brief, rubric, roster, taught_patterns.md,
   CLAUDE.md, per-type skill installed). If any missing, stop.
2. **Extract any zips** and reconcile filenames to roster names. Canvas
   typically names submission zips with a surname-firstname slug; map each
   to the roster spelling.
3. **Build the present-roster.** Cross-check submissions against the
   roster; any roster student with no submission gets a `0/[total]
   (no submission)` entry in `grades.csv` and is excluded from teammate
   work.
4. **Per-student inventory report.** For each present submission, record:
   - source code present? (actual files, not just project stubs)
   - compiled document present?
   - console screenshot present? (file or embedded in docx)
   - walkthrough video present locally OR cloud link in docx OR neither
   - signed Authorship Statement present?
   - problem statement reproduced in docx?
   - **multi-zip submissions** (note which is primary)
   - **empty / abandoned video clips** (mark these ignored)
   - **non-standard file paths** (e.g. `work sam.cs` instead of `Program.cs`)

   **Surface anomalies to the lecturer BEFORE Step 1.** They affect grading
   paths and shouldn't be discovered mid-flight by individual teammates.

5. **Note baseline list** from CLAUDE.md — students with confirmed prior
   AI flags (Cat A or Cat B) and students on lecturer-trusted baselines.
   Pass each teammate the relevant baseline for the student they're
   grading — and only that student's baseline, not the full table.

6. **Pre-fetch + pre-transcribe ALL videos centrally** — *only if the
   assessment requires/allows video walkthroughs* (skip entirely if not).
   Three phases:
   - **Phase 1 — gdown / yt-dlp (serial, fast):** scan each docx for
     Drive / YouTube / Instagram URLs. For Drive, use the file ID alone
     with `python -m gdown "<file-id>"` — older gdown sometimes chokes on
     `?usp=sharing` URLs. On HTTP 401/403, record in a
     `_provisional_holds.txt` and skip; those students get the
     provisional-hold treatment per `grade-video`.
   - **Phase 2 — ffmpeg audio extraction (parallelize):** ffmpeg is
     CPU-bound. Run extractions in parallel.
     `ffmpeg -i <video> -vn -ac 1 -ar 16000 -acodec pcm_s16le <video>.wav -y`
   - **Phase 3 — transcription (strictly serial, smallest first):** GPU
     contention is real on consumer cards; 6 GB VRAM cannot fit two
     concurrent ASR jobs. Order videos shortest-first so quick wins land
     early. One call per video:
     `python C:/Users/philo/Projects/teaching-toolkit/asr.py <video-stem>.wav`
     Parakeet v3 auto-detects language across 25 European languages —
     there is no language flag to pass — but detection can still mis-fire
     on very short or very noisy clips, so **eyeball the first line of
     each `.txt`** before handing transcripts to teammates. A run that
     dies partway is resumable: re-run the same command.
   - Save outputs as `<video-stem>.wav` + `<video-stem>.json` next to the
     source video — `grade-video` assumes this naming.

   **Why centrally:** if teammates each transcribe in parallel, the GPU
   serialises and most teammates time out waiting. Central pre-fetch is
   the single biggest reliability fix. Budget ~1-2 min per 30 min of
   video (~32x real time) plus a ~20 s model load per worker.

7. **Verify the buildable / openable artefact for every submission** —
   *only if the configuration block flagged one* (skip if the assessment
   is a read-only document/spreadsheet/etc.). Record the result with a
   timestamp. Examples:
   - **Code:** `dotnet build` / `python -m py_compile` / `tsc --noEmit`
     / `npm run build` — record exit code + warnings + errors verbatim
   - **Web app (ASP.NET):** `dotnet build`; for HTML/CSS/JS, validate with
     a headless browser load (e.g. `python -m http.server` + curl smoke
     test) or note "static — no build step"
   - **Database (Access):** open the `.accdb` and verify it loads without
     errors; for SQL scripts, dry-run against an empty schema
   - **Spreadsheet / presentation / document:** open and verify it isn't
     password-protected or corrupt; no "build" status to record
   
   Build/open status can go stale if the lecturer fixes an issue
   mid-review — re-verify before Step 4.

## STEP 1 — CALIBRATION (mandatory, before any real grading)

The goal of calibration is *not* to prove the agents agree (they almost
always will) — it's to expose direction-of-drift and to validate that the
agents are reading the right question.

### If a hand-graded anchor exists

Pass each of 3 teammates the anchor and the rubric. Compare their outputs
against each other AND against the anchor. Tolerances:
- Per-criterion score divergence > 1 → fail
- Total divergence > 3 across teammates → fail
- Total divergence > 3 from the anchor → fail
- Different deductions flagged on the same code section → fail

### If no anchor exists (more common)

Calibrate from inter-teammate agreement, grounded in **lecturer-style
references** from prior assessments (hand-graded `feedback.md` files
showing the lecturer's evidence-tier handling, partial-credit logic, and
house style — these don't need to share rubric criteria with the current
assessment, just style). Pick **two real submissions** as calibration
cases — contrasting shape (one likely-clean, one likely-flawed, picked
using baselines as priors) — and tighten the agreement bands:
- Per-criterion divergence > 1 → fail
- Total divergence > 2 across teammates → fail
- Different section names for the same criterion → fail
- Tier violations (code-structure marks awarded from Tier B/C/D) → fail
- Any teammate categorising AI authorship (Cat A/B/C) → fail
- **Baseline sanity check:** if all three teammates land on a score that
  contradicts the baseline strongly, surface it. Three teammates can
  agree and all be wrong in the same direction.

### Adversarial probe — REQUIRED, not optional

Convergent teammate readings prove the agents agree, not that they're
right. **Every teammate must explicitly enumerate, in their JSON output,
every construct in the submission that does NOT appear on
`taught_patterns.md`.** Schema field: `not_taught_constructs`, an array
of `{construct, file:line, taught_alternative, significance}`.

This is the safeguard that catches AI authorship the convergent-agreement
test misses. Three convergent teammates can all read a polished AI-generated
submission as authentic if none of them know which constructs aren't on
the syllabus. The probe forces them to surface the negative evidence.

### Lecturer spot-review at the end of Step 1

Present the two calibration grades + section naming + AI flags to the
lecturer for a brief spot-review before Step 2. The lecturer signs off
(or adjusts), and the chosen output becomes the template-and-rubric
lock-in for the rest of the run. The two calibration submissions are
treated as graded — their `feedback.md` files are written now using the
lecturer-signed-off output (lead writes; see Step 2).

## STEP 2 — PARALLEL GRADING

**Default: 1 submission per teammate.** Within-agent context contamination
is the dominant drift risk; calibration shows agents converge tightly
per-submission. Spawning N agents at depth-1 is structurally cleaner than
N/3 agents at depth-3, with roughly equivalent total token cost and faster
wall time. Raise above 1 only with a compelling token-budget reason.

**Always pre-fetch and pre-transcribe ALL videos in Step 0** — never let
teammates transcribe themselves. The first-run pipeline that did this
had two of three teammates time out at 12-13 minutes each.

**Teammates produce JSON only — they do NOT write `feedback.md`.** Lead
writes feedback.md centrally after the outlier audit, for four reasons:
(a) cohort-wide phrasing consistency is only enforceable centrally;
(b) prior-Cat-A/B students need custom AI-Authorship-Indicators sections
+ viva questions that teammates lack the context to write;
(c) viva-window framing is set by per-assessment policy the lecturer
controls; (d) one phrasing-canonicalisation pass is faster than editing
N feedback files.

### Each teammate must:

1. Invoke **the per-type grading skill named in the configuration block**
   (`grade-code` / `grade-document` / `grade-spreadsheet` /
   `grade-presentation` / `grade-database`) AND `grade-video` if the
   configuration block flagged a walkthrough video as present/required.
2. Read every submitted artefact relevant to the rubric.
3. Run the build/open check named in the configuration block (skip if
   the assessment is a read-only document); record verbatim.
4. Read the pre-transcribed video JSON if present (do NOT re-transcribe).
   Extract frames at load-bearing timestamps if Tier B/A verification is
   needed. Cite the most specific evidence the artefact type allows in
   every justification:
   - **Code:** `file:line`, method/class name, video timestamp + filename
   - **Web app:** `file:line` + DOM selector / page route / event handler name
   - **Document:** page number + paragraph + quoted phrase
   - **Spreadsheet:** sheet name + cell address + formula
   - **Presentation:** slide number + element + on-slide text
   - **Database:** table/query/form name + field/column
5. Apply the rubric using the per-type skill's Earned/Partial/Missing
   model. No invented partial credit between integer values. No "half
   marks for effort."
6. Apply the cosmetic-vs-functional rule from the per-type skill — don't
   deduct for typos / renames / formatting tweaks if the underlying work
   is correct.
7. Enumerate `not_taught_constructs` per the calibration adversarial probe.
8. Return JSON matching the canonical schema, write to `_step2/` (NOT
   `_calibration/` — keep them separate so audit selectors don't get
   muddled).

### Canonical JSON schema

The schema is mostly type-agnostic. Fields marked `(if applicable)` apply
only when the configuration block flagged that capability — omit them
otherwise so the JSON stays clean.

```json
{
  "submission_id": "string — roster name",
  "files_read": ["string — relative paths actually opened"],
  "build_status": "success | warnings | errors | not_attempted",   // if buildable
  "build_errors": ["string"],                                       // if buildable
  "deliverables_present": {
    "primary_artefact": true,           // the code / paper / sheet / etc.
    "compiled_document": true,          // docx / pdf if required by brief
    "problem_statement_in_doc": true,   // if required by brief
    "screenshot_of_output": true,       // if required by brief
    "authorship_statement": true,       // if required by course-wide policy
    "walkthrough_video": true           // if required/optional per config
  },
  "deliverables_missing": ["string"],
  "walkthrough_video_status": "local_file | downloaded_from_cloud | drive_link_restricted | absent",  // if video applicable
  "walkthrough_video_notes": "string — local path and transcript path, or URL attempted on restricted",  // if video applicable
  "criteria": [
    {
      "name": "string — must match the rubric's locked section names exactly",
      "score": 0,
      "max": 0,
      "status": "Earned | Partial | Missing",
      "evidence_tier": "A | B | C | D",
      "justification": "string — MUST cite the most specific evidence the artefact type allows (file:line / page+paragraph / sheet+cell / slide+element / table+field / video timestamp + filename)"
    }
  ],
  "rubric_subtotal": 0,
  "rubric_max": 0,
  "ai_indicators": {
    "level": "None | Low | Medium | High",
    "indicators": [
      { "type": "string", "detail": "specific evidence", "confidence": "Low | Medium | High" }
    ]
  },
  "not_taught_constructs": [
    { "construct": "string", "evidence_location": "string — file:line / page / sheet:cell / slide / etc.",
      "taught_alternative": "string", "significance": "string" }
  ],
  "student_feedback_preview": "Strengths bullets + Areas for Improvement bullets only — NO baseline content"
}
```

### AI flag canonical anchor (set during calibration)

Pick one anchor and apply it cohort-wide. Two options:
- **"Low" when fingerprints counter-AI** — log indicators even when they
  argue *against* AI; "None" only when nothing notable. Preserves
  audit trail.
- **"None" when no positive AI evidence** — only log indicators that
  positively suggest AI; "None" is the clean default. Less noise.

Whichever you pick, bake into the Step 2 teammate prompt.

### Hard rules for teammates

- Do NOT write `feedback.md` to disk
- Do NOT categorise AI authorship (Cat A/B/C) — flag indicators only;
  categorisation is the lecturer's call
- Do NOT award method/structure marks from Tier B/C/D evidence
- Do NOT use shortcut phrases ("half marks for effort", "good faith
  attempt", "benefit of the doubt", "I think they meant")
- Do NOT echo per-student baseline content into the student-facing
  `student_feedback_preview` field
- Do NOT rename the locked criterion names

## STEP 3 — OUTLIER AUDIT + MANDATORY SPOT-REVIEWS (lead only)

Once all teammates return, before anything is treated as final, review:

- **Submissions > 2σ from the cohort mean** (high or low)
- **Single-teammate deductions** flagged on a section nobody else flagged
  on analogous code shapes
- **Justifications that don't quote** a file:line, method name, or
  timestamped video frame
- **Status mismatches** — `Earned` with `score < max`, `Partial` with
  `score == max`, etc.
- **Tier violations** — `evidence_tier: "C"` or `"D"` with > 0 awarded
  on a code-structure criterion
- **AI indicators Medium or High** — pair with the student's baseline
  and pass to the lecturer for viva decision; never write categorisation
  into feedback
- **Mandatory lecturer spot-review for every prior-Cat-A/B student**,
  regardless of teammate flag level. Surface to the lecturer with
  (a) teammate's AI indicator list and level, (b) student's classroom
  baseline from CLAUDE.md, (c) video transcript with any segments
  showing first-time-reading cadence or unexplained design choices,
  (d) `not_taught_constructs` from the JSON. The lecturer's review is
  the final answer on category for these students. Teammates cannot see
  what was taught in class, so they cannot tell an authentic-clean
  submission from an AI-clean submission read aloud.
- **Section heading drift** from the calibration template
- **Cohort-wide phrasing check** — pull every `student_feedback_preview`
  for identical situations (missing screenshot, missing video, same
  rubric-section partial) and rewrite divergent phrasings to a single
  canonical form before feedback files are finalised.
- **Build/open re-verify pass** (only if applicable per config) — re-run
  the build/compile/open check before finalising rubric scores. Status
  can go stale when the lecturer fixes a typo mid-review; rubric sub-
  points tied to "runs and produces output" are sensitive to this.

### Cross-check second wave (~20% of cohort)

Pick 2 (for ~9 submissions) for a blind cross-check — spawn fresh agents
with the same prompts, instruct them NOT to read prior teammate JSONs,
write to `crosscheck_<student>.json`. Compare scores; > 3-point divergence
feeds back into outlier audit as cohort-level drift evidence.

**Selection rule (load-bearing):** pick **at least one prior-Cat-A/B
student plus one anomalous-evidence student** — not two of one kind. The
prior-Cat picks validate the highest-stakes dispositions; the anomalous-
evidence picks (no source code, extreme video lengths, multi-zip
submissions) validate unusual evidentiary calls.

Surface the audit findings for lecturer manual review before grades.csv
is written.

## STEP 4 — FINALISATION (lead only, after lecturer sign-off)

1. **Apply per-deliverable deductions centrally** using a fixed scale
   set once and applied cohort-wide.
2. **Apply provisional-hold treatment** for any teammate-flagged
   `walkthrough_video_status: "drive_link_restricted"` per `grade-video`'s
   established procedure: `grades.csv` entry reads `0/[total]
   (provisional - rubric X/[total] held pending video access)`, full
   underlying rubric noted as recoverable, Canvas comment asks the
   student to fix Drive sharing (NOT switch platforms).
3. **Apply provisional-hold treatment** for prior-Cat-A/B students
   flagged at the lecturer's spot-review per the project's framework.
   Match the wording style used in prior assessments' `grades.csv` for
   consistency.
4. **Compute final scores** = `rubric_subtotal − deliverable_deductions`
   for non-held students.
5. **Write `feedback.md` for every student** centrally using the
   calibration-locked template. For prior-Cat students who got the
   spot-review treatment, include the lecturer-only AI Authorship
   Indicators section + draft viva questions (apply the four-part
   provenance chain to each `not_taught_construct` entry: Source / Why
   over taught equivalent / Value / Personal understandability) +
   decision tree for after-viva outcomes.
6. **Standardise viva-window framing** across all held students per the
   per-assessment policy ("provisional pending viva window" vs "viva
   opt-in" with explicit deadline language — the lecturer sets this
   once, all four affected feedback files use identical wording).
7. **Write `grades.csv`** matching prior assessments' format.
8. **Canvas comments come last and stay manual** — per the `grade`
   skill's pacing rule, generate one Canvas comment per turn at the
   lecturer's pace; never batch.

## Quality-drift safeguards (the load-bearing ones)

1. **Two calibration submissions, not one** — single anchor catches
   teammates reading the rubric *wrong*, but not teammates reading it
   *softly* or *harshly*. A high+low pair catches both.
2. **Default 1 submission per teammate** — within-agent context
   contamination is the dominant drift risk.
3. **Lock the feedback template before Step 2** — section names, column
   headers, ordering. Set by the calibration grade.
4. **Blind cross-check on ~20%** with the prior-Cat + anomalous-evidence
   selection rule.
5. **Evidence-tier field is mandatory and load-bearing** — forces every
   criterion to declare its tier; tier violations self-report.
6. **Pre-commit blocklist on shortcut phrases** — regex check on JSON
   output for "half marks for effort", "good faith attempt", etc.
7. **AI flagging never blocks grading** — teammates flag, lecturer
   decides viva.
8. **Phrasing canonicalisation pass** at the end (lead does this once;
   teammates can't enforce cross-cohort consistency).
9. **Pacing override is explicit** — this pipeline deliberately breaks
   the `grade` skill's "one student at a time" rule for throughput. The
   lecturer should still spot-read 2-3 random `feedback.md` files before
   posting any grades to Canvas.
10. **Canvas-facing comments stay manual** — JSON-only teammates +
    centrally-written `feedback.md` + manually-written Canvas comments.

## Common pitfalls (each one bit on the first run — internalise before re-running)

1. **Teammates transcribing concurrently → GPU contention → timeouts.**
   Pre-transcribe all videos centrally in Step 0, even local ones.
2. **Language auto-detect mis-firing on short clips** (Javanese, Welsh,
   etc. under WhisperX). Parakeet v3 auto-detects across 25 European
   languages with no flag to pin it, so the guard is to read the first
   line of each transcript before use and re-cut any clip that came out
   in the wrong language.
3. **Teammates can't see what was taught in class** → convergent reading
   on AI-generated work as authentic. This is what `taught_patterns.md`
   + the `not_taught_constructs` adversarial probe + the prior-Cat
   spot-review jointly close.
4. **Convergent teammate readings ≠ correct readings.** Three agents
   reading the same evidence the same wrong way is the dominant false-
   negative mode.
5. **Cross-check picking the wrong axis.** Anomalous-evidence picks are
   tempting but lower-stakes than prior-Cat picks. Mix them.
6. **Per-student inventory discovered mid-flight.** Surface
   missing-primary-artefact (no `.cs` / no `.docx` / no `.accdb`),
   multi-zip uploads, empty / abandoned video clips, and non-standard
   filenames in Step 0. Type-specific examples: code may have project
   stubs without source files; documents may be password-protected;
   spreadsheets may be `.xls` when the brief expected `.xlsx`; databases
   may ship without the linked tables.
7. **Build/open status going stale** when the lecturer fixes the artefact
   mid-review (semicolon typo in code, password removed from docx, etc.).
   Re-verify before Step 4 finalisation.
8. **Teammates writing `feedback.md`** then needing it overwritten when
   the prior-Cat mandatory-spot-review fires. JSON-only from the start.
9. **Viva-window framing drift** between prior-Cat feedback files. Set
   the wording once at Step 0 per-assessment policy.
10. **`_calibration/` and `_step2/` mixed** in the same directory. Keep
    them separate — audit selectors get muddled otherwise.
11. **UTF-8 encoding on JSON I/O.** Python defaults to cp1252 on Windows;
    teammate JSON containing non-ASCII (em-dashes, accented quotes) will
    crash a default `open(file).read()`. Always pass
    `encoding='utf-8', errors='replace'`.
12. **Parallel ffmpeg, serial transcription.** ffmpeg is CPU-bound and
    parallelizes; ASR is GPU-bound and must serialise. Sort transcription
    by video size — smallest first — so quick wins land early.

## Pacing inside this pipeline

The `grade` skill's "one student at a time, never auto-advance" rule is
deliberately broken here for throughput. To compensate:
- Always run Step 1 calibration before Step 2 — never skip
- Always pause after Step 0 inventory for lecturer eyeballs on anomalies
- Always pause after Step 1 calibration for lecturer spot-review
- Always pause after Step 3 outlier audit before writing feedback files
- After feedback files are written, the `grade` skill's per-student
  pacing resumes for Canvas comments (one per turn at lecturer pace)

The pipeline trades sequential-grading depth for parallel throughput.
The pause-points are where lecturer eyes substitute for the depth.
