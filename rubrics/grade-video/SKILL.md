---
name: grade-video
description: >
  Grades student walkthrough / demonstration videos that accompany a coursework
  submission (code, document, spreadsheet, etc.) as a rubric deliverable.
  Triggers on 'grade video', 'mark walkthrough', 'process student demo video',
  'transcribe walkthrough', 'grade video submission', or when a rubric
  criterion explicitly requires a video and the marker has to assess its
  content. Use ALONGSIDE the type-specific grading skill (e.g. grade-code) —
  this skill handles the video portion only.
argument-hint: "[path to student folder or video file]"
---

# Walkthrough Video Grading

Grades the video deliverable that students submit alongside their code / docx
/ spreadsheet for coursework. The video is supporting evidence that the rubric
explicitly counts — not a replacement for the primary deliverable, but in
some rubric lines it stands in for or supplements the written explanation.

## When to use this skill vs. the others

| If… | Use |
|-----|-----|
| Student submits a **walkthrough video** explaining their own code / document / spreadsheet | **`grade-video`** (this skill) plus the type-specific skill for the underlying work |
| Recording is a **lecturer-conducted oral defence / viva** (lecturer + student, Q&A) | `grade-viva` (it has the diarization workflow) |
| You want to summarise a **third-party YouTube / Instagram URL** that is not a student submission | `video-summary` |
| You need the underlying **transcription pipeline** itself | `grade` (defines the canonical ffmpeg + `asr.py` workflow) — this skill references it |

## Cloud-hosted video links (Google Drive, etc.) — DO NOT skip this step

Students will often submit a Google Drive link inside a docx rather than
attaching the video locally. **Drive is the canonical channel for video
submissions in this course** (HOD directive — Canvas has limited storage).
Do not advise students to switch to Canvas, and do not treat a Drive link as
automatic Tier C/D evidence.

### Procedure for every cloud-hosted video link

1. **Try to fetch the video** before assessing whether it can be graded.

   ```bash
   # Single Drive file (anyone-with-the-link, public, or accessible to the
   # signed-in account)
   python -m gdown "<drive-url>" -O "<student-folder>/walkthrough.mp4"

   # Drive folder
   python -m gdown --folder "<drive-url>" -O "<student-folder>/"

   # YouTube / Instagram link — use yt-dlp via the video-summary skill
   python -m yt_dlp -o "<student-folder>/walkthrough.%(ext)s" "<url>"
   ```

   Always invoke `gdown` and `yt-dlp` via `python -m` — on Windows the
   bare CLI scripts often aren't on PATH while the module form always works.

2. **Outcome A — download succeeds**: proceed to the Transcription section
   below. Grade the video against the rubric line normally.

3. **Outcome B — `gdown` fails with HTTP 401/403, "Permission denied", or
   redirects to a login page**: the link is restricted. Do NOT silently
   deduct marks on the rubric for the missing video — that conflates a
   permissions problem with a content problem, and it's the wrong
   procedural branch.

   Instead:
   - **Hold the rubric grade as provisional** — set the posted grade to
     `0/total` in `grades.csv` with the underlying rubric score noted as
     "recoverable" (e.g. `0/30 (provisional - rubric X/30 held pending video
     access)`).
   - In `feedback.md`, write the underlying rubric breakdown on the basis
     of the evidence that IS available (code, screenshot, docx). Mark the
     video-dependent rubric line(s) as "pending video access".
   - In the Canvas-facing comment, ask the student to **change Drive
     sharing to "Anyone with the link"** (not to upload to Canvas — that
     contradicts the HOD directive).
   - Once the student fixes sharing, re-run `gdown`, transcribe, and update
     `feedback.md` + `grades.csv` to the recovered score.

   **Why this matters:** the procedural branch differs depending on the
   reason for the missing video. A direct rubric deduction is correct when
   the video genuinely doesn't exist or genuinely doesn't show what the
   rubric requires. The provisional-hold pattern is correct when the video
   may exist and may be fine but the marker can't see it yet. Treating them
   the same penalises the student for a permissions misconfiguration.

   **Precedent:** lecturer ruling on 2026-05-11 for Channer A2 — Drive
   folder link with Restricted sharing, `gdown --folder` returned HTTP
   401. Held provisional `0/40` with rubric `29/40` noted as recoverable;
   resolved when sharing was fixed.

4. **Outcome C — the link is to a platform `gdown`/`yt-dlp` cannot reach
   (e.g. private OneDrive, university SSO-walled storage)**: same
   provisional-hold treatment as Outcome B. Chase the student to re-host
   on Drive with public sharing.

### What this DOES NOT mean

- It does **not** mean "always accept whatever the student linked to". The
  hold pattern only applies when the link is inaccessible *but plausibly
  fixable*. If the linked content turns out to be a different video, an
  unrelated file, or empty, that is a content problem and the rubric line is
  legitimately 0 with no hold.
- It does **not** override the AI authorship policy. If the video is
  accessible and the student cannot explain their own code in it, that's a
  separate viva-track issue (see `grade-viva`).

## Video-substitutes-written-explanation rule (CPRG1205-specific)

For CPRG1205 code assessments where the rubric has a written-explanation
criterion (e.g. A2's "Written Explanations" line covering Q10–Q13; A3's
"Output and Explanation" 3rd sub-point coupling written explanation + video):

- **The video substitutes the docx when the docx is missing**, and **the
  docx substitutes the video when the video is inaccessible** (after the
  Cloud-link procedure above has been attempted).
- If only one of the two is available and it covers the rubric questions
  substantively, award the full mark for that sub-point. Note the
  substitution explicitly in the rubric row of `feedback.md` with a quoted
  excerpt from whichever source was used.
- This overrides the general Tier C policy ("verbal claim only = 0 marks")
  for this specific class of rubric criteria in CPRG1205 — the rule was set
  2026-05-11 after the Hinds A2 spot-check.
- If neither is accessible / present, the criterion is 0 with no hold —
  there's no recoverable evidence.
- Still recommend the missing artefact in "Areas for Improvement" so
  students learn the standard expectation.

**Scope:** CPRG1205 confirmed for A2 and A3. Likely extends to future
CPRG1205 assessments. Does not automatically extend to other courses.

## Transcription workflow

Do not duplicate the canonical pipeline — defer to the `grade` skill, which
has the full ffmpeg + `asr.py` recipe and the hardware profile (RTX 3060,
6 GB VRAM; the engine handles the ceiling itself). The summary:

```bash
# 1. Extract audio (mono, 16 kHz)
ffmpeg -i "<video>" -vn -ac 1 -ar 16000 -acodec pcm_s16le "<video-stem>.wav"

# 2. Transcribe — single-speaker walkthrough, no diarization needed
python C:/Users/philo/Projects/teaching-toolkit/asr.py "<video-stem>.wav"
```

Writes `<video-stem>.txt` / `.srt` / `.json` next to the input.

- **Always save the `.wav` and the transcript JSON next to the source
  video**, named after the video stem (e.g. `walkthrough.mp4` →
  `walkthrough.wav` + `walkthrough.json`). This keeps the work reusable
  across grading reruns.
- Walkthrough videos in this course are almost always **single-speaker**
  (the student narrating their own code). Diarization is unnecessary; do
  not add `--diarize` for these — it adds dependency on the pyannote model
  for no benefit.
- **Multi-speaker exception:** if the video clearly has a second voice
  (e.g. a peer, an instructor in the background, the student's phone
  playing audio of someone else explaining), switch to the diarization
  workflow in `grade-viva`. Pass the actual count to `--speakers`.
- **Long video warning:** a 30 min video takes roughly 1–2 min to
  transcribe on this GPU (~32x real time, plus a ~20 s model load per
  worker). If you queue it as a background job, do not poll it
  indefinitely — set a reasonable timeout and check on completion. A run
  that dies partway is resumable: re-run the same command.

## Frame extraction for Tier B evidence

A transcript alone is not sufficient. ASR can mis-hear, and the
student's narration is a *claim* about what's on screen — Tier B requires
the marker to *see* it.

```bash
# Extract one frame at HH:MM:SS for visual verification
ffmpeg -ss 00:02:15 -i "<video>" -frames:v 1 "<student-folder>/frame_2-15.png"

# Put -ss BEFORE -i for fast seek (decode-after-seek). For frame-accurate
# extraction on long videos, also pass -accurate_seek.
```

Then **Read** the PNG file (the Read tool accepts images) to visually
inspect what was on screen at that moment. Cite the frame filename and
timestamp in the feedback's justification, so the lecturer can re-verify.

**When to extract frames:**

- Any rubric line whose award depends on what was visible (output
  screenshot match, IDE-window confirmation, rubric-criterion call-out
  the student claims to have on screen).
- Any narration moment where the student says "as you can see here…" —
  verify *that they actually showed it*.
- The end of the video, for a final-state output capture.
- Any moment the student claims to demonstrate a specific construct (e.g.
  "I'm running the override method now") — verify the IDE / console
  matches the claim.

## Evidence tier handling for video evidence

The general `grade-code` evidence tier table applies, with these
video-specific clarifications:

| Tier | What the video shows | Awards |
|------|----------------------|--------|
| **A** | Clear, readable frames of the actual source code in the IDE, OR the video repeats the source file content visibly | Can award method/structure marks — equivalent to reading the `.cs` file |
| **B** | Program running and producing output that's clearly visible on screen, with student narrating; OR student walking through what their code does with the code visible | Award marks for the *observed behaviour* (output values, prompts, control flow that actually executed) — but **not** method-signature / data-structure / loop-type marks unless the code is also readable in-frame |
| **C** | Student verbally claims something is in the code but the code is not visible in the frame, OR the student reads code aloud without showing it | **0** on any criterion that depends on code structure — no Tier-A award. Verbal claim only |
| **D** | Phone-camera recording of a monitor, blurry, unreadable text, audio garbled, IDE not visible | Treat as Tier C — no code marks awarded for the unreadable portions |

**Brief-vs-grade-code conflict:** assignment briefs sometimes say "markers
may use the video as evidence for class design, inheritance, etc." Resolve
this by treating the brief's licence as applying *only when the code is
actually visible at Tier A clarity in the video frames* — verbal-only
narration over an unreadable screen does not become Tier A just because
the brief permits video evidence.

## Authenticity markers — real student vs. AI-scripted walkthrough

The walkthrough video is one of the most reliable AI-authorship signals in
the cohort. Real students sound nothing like scripted narration.

### Authentic-student markers (counter-indicate AI)

- **Technical-term slips and self-corrections:** mispronouncing or
  swapping technical terms in real time. "Public veto" for "void",
  "construction" for "constructor", "static form" for "static void main",
  "probably override" for "public override" — these are heard-only-once
  fingerprints. Quote them verbatim with timestamps in feedback.
- **Disfluencies:** "um", "uh", repeated false starts ("class car
  vehicle… um the class the car class"), hesitations before reading their
  own variable names.
- **Reading off the screen in code order:** narration tracks top-to-bottom
  with the file, not the rubric. The student is *seeing* the code, not
  reciting from memory.
- **Authentic regional voice:** local accent, code-switching, casual
  phrasing ("alright, this is my crew", "sarah ma run the code right now
  here"). AI-scripted walkthroughs are uniformly neutral-corporate.
- **Conceptual statements at the end that map runtime to concept:** "and
  because of the inheritance both shared the same info, and because of
  the polymorphism each shows its own extra detail" — when the
  *connection* between behaviour and concept is articulated in the
  student's own words, that's authentic understanding.

### AI-scripted-walkthrough red flags

- **Uniform sentence structure across the whole video** — e.g. every line
  reads "It is to X / It is because Y / This is for Z". Real student
  narration is wildly uneven.
- **No disfluencies at all** — perfectly fluent reading, no false starts,
  no rephrasing. Suspicious especially in students whose in-class baseline
  shows hesitation.
- **Narration order does not track the on-screen code** — student says
  "let me explain inheritance" while the screen shows the override method;
  the narration follows the *concept order of the brief* not the *file
  order*. Indicates a pre-written script.
- **Systematic avoidance of specific topics that appear in the code** —
  e.g. code uses `TryParse` and `out` but the narration covers everything
  except those. Pairs with a known prior-viva failure pattern.
- **Mismatch between narration and screen** — student claims to be on
  line 40 but the IDE shows line 200; student "demonstrates the override"
  but the displayed method has no `override` keyword.
- **Camera off when rubric required it on** — see brief / CLAUDE.md per
  course.
- **No on-screen IDE / console** — student narrates audio-only or with
  a static slide / image. Tier C/D automatically.

Flag any of these in the lecturer-only `## AI Authorship Indicators`
section of `feedback.md`, with timestamps and quoted phrases.

## Single-speaker vs. multi-speaker — handle correctly

Walkthrough videos are almost always single-speaker. But:

- **Background voices**: someone in the room, a phone on speaker, a
  classmate. If they're not contributing to the walkthrough, ignore — but
  note in feedback if it makes the audio hard to follow.
- **Student playing a recording**: if the student plays an AI-generated
  narration or a peer's video over their own walkthrough, that's a strong
  authenticity red flag. Diarize to confirm.
- **Group walkthroughs** (rare in this course but possible): treat each
  speaker's contribution separately, only credit the named student for
  what they personally said. Use `grade-viva`'s diarization workflow with
  the actual speaker count.

## Output: what to write in the per-criterion feedback

Cite the video in any justification that draws from it, using this format:

> `(in video8261914783.mp4 at 0:42–1:05)` student narrates the
> `Displayvehicledetails` override on the Truck class and quote a
> distinctive phrase verbatim, especially any technical-term slip.

For frame-based evidence:

> `(frame_2-15.png)` console window visible at 2:15 shows the receipt
> output matching `Program.cs:81-86` exactly.

For Drive-link provisional holds:

> Walkthrough video is hosted at Google Drive (link in submission docx);
> `gdown` returned HTTP 401, suggesting Restricted sharing. Video sub-point
> held pending sharing fix. Underlying rubric score 30/30 is recoverable
> when the video is accessible.

## Standard processing checklist (use every time)

1. Locate the video — either as a local file in the student's folder or a
   cloud link in the docx / submission notes.
2. If cloud-hosted, run the gdown / yt-dlp step from the Cloud-link
   procedure above. On failure: provisional hold, no rubric-line deduction.
3. Extract audio with ffmpeg (mono, 16 kHz, PCM).
4. Transcribe with `asr.py` (single-speaker; no `--diarize` unless the
   audio actually has multiple voices).
5. Read the transcript end-to-end before grading. Note authenticity
   markers as you go.
6. For every rubric line the video bears on, identify load-bearing
   timestamps. Extract frames at those timestamps with ffmpeg.
7. Read each frame (the Read tool accepts PNGs) to verify what the student
   is claiming is actually on screen.
8. Write the per-criterion justification with the timestamp + video
   filename and any quoted distinctive phrase or frame filename.
9. AI Authorship Indicators section: include video-specific markers from
   the lists above, with timestamps and verbatim quotes.

## What to recommend in feedback when something's wrong

- **Restricted Drive link:** "Please re-share the Drive link with 'Anyone
  with the link' permissions, then reply on Canvas so the video can be
  reviewed." Do NOT suggest uploading to Canvas instead.
- **Camera off when rubric required it on:** flag for course policy
  enforcement; do not deduct on the rubric unless the rubric explicitly
  awards marks for camera-on.
- **No screen share / no IDE visible:** "For future walkthroughs, please
  share your screen so the marker can see your code and IDE alongside
  your narration — without that, several rubric lines can only be Tier B
  at best."
- **Garbled audio or excessive background noise:** "For future
  walkthroughs, please record in a quieter environment and check the
  microphone level — sections of this recording were too unclear to
  transcribe reliably."
