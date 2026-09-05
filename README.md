# Teaching Toolkit

A collection of methodologies, templates, and reference documents for producing high-quality class teaching materials with the help of AI chatbots.

This repo holds reusable assets that travel from one course to the next — methodologies for how to produce content, templates that match a polished design system, and course-specific notes when they accumulate enough volume to warrant their own folder.

---

## What's in here

```
teaching-toolkit/
├── asr.py                The local speech-to-text engine (see below)
├── transcribe.py         Diarization + word→speaker merge, used by asr.py
├── methodologies/        Generic guides for how to produce class content
├── course-specific/      Per-course handoff docs and reference material
│   └── [course-code]/
├── templates/            Reusable .docx and .pptx templates
└── rubrics/              Standalone marking rubrics
```

### Transcription (`asr.py`)

Every local speech-to-text job on this machine goes through `asr.py` — the
grading skills, the video-summary pipeline, and the video editing skill all
call it. It runs **NVIDIA Parakeet TDT 0.6b v3** on the 6 GB RTX 3060 and
handles the VRAM ceiling itself (fp16, 600 s chunks, worker subprocesses,
resumable).

```bash
# Transcribe. Writes <base>.txt / .srt / .json next to the input.
python asr.py audio.wav

# Add speaker labels. ALWAYS pass the speaker count when you know it.
python asr.py audio.wav --diarize --speakers 2
```

Audio must be 16 kHz mono:
`ffmpeg -i in.mp4 -vn -ac 1 -ar 16000 -acodec pcm_s16le out.wav`

Rough costs on this GPU: ~1–2 min to transcribe 30 min of audio; add ~230 s if
you pass `--diarize`. A run that dies partway is resumable — re-run the same
command and banked chunks are skipped.

Setup, tuning, benchmarks and the hard-won failure modes are in
`parakeet-setup.md`. **Read §7.2 before changing any chunk-size setting** — the
intuitive change (smaller chunks) buys nothing and costs a lot.

### `methodologies/`

Generic, course-agnostic guides. The most important file here is the **content creation handoff** — a complete methodology document that can be dropped into a fresh AI chat to produce slide decks and teaching scripts in a consistent, professional style for any course.

Use these when starting work on a new course or onboarding a new AI chat.

### `course-specific/`

When a single course accumulates enough specific context — student lists, scenario libraries, terminology to clarify, exam scenarios to mirror, semester plans — it gets its own folder here. Course-specific docs override or extend the generic methodologies for that one course.

### `templates/`

Pre-built `.docx` and `.pptx` files that match the locked design system, plus the `.js` builder scripts that generate them. Useful when an AI chat needs to start from a working file (or a working build script) rather than build from scratch.

### `rubrics/`

Standalone marking rubrics that can be reused across courses or assessments, plus the grading skills used to apply them. Coursework brief documents that include rubrics live with their course; standalone rubrics live here.

Inside `rubrics/` you'll find folders named `grade`, `grade-code`, `grade-cohort`, `grade-database`, `grade-document`, `grade-presentation`, `grade-spreadsheet`, `grade-video`, `grade-viva` — these are snapshots of the Claude Code skills installed at `~/.claude/skills/`. Each is a single `SKILL.md` describing how to grade a particular kind of student submission against a rubric. The repo copies are a snapshot for sharing and archival; the live versions used by Claude Code are the ones in `~/.claude/skills/`. Re-snapshot when they change meaningfully.

---

## How to use this repo

**Starting a new course:**

1. Open the relevant methodology doc from `methodologies/`
2. Paste it into a fresh AI chat
3. Add your course-specific context (course code, schedule, units, students, etc.)
4. Ask the chat to start producing materials

**Continuing work on an existing course:**

1. Open the course-specific folder under `course-specific/`
2. Find the most recent handoff doc or session reference
3. Paste both the methodology AND the course-specific notes into a fresh chat
4. Continue from there

**Adding a new asset:**

- Generic, reusable across courses → `methodologies/` or `templates/`
- Specific to one course → `course-specific/[course-code]/`
- Standalone marking rubric → `rubrics/`

---

## Conventions

- **Markdown for documentation.** Easier to copy-paste into AI chats than Word or PDF.
- **One topic per file.** Don't bundle multiple methodologies into one doc.
- **Filenames are descriptive, lowercase, hyphenated** (e.g. `content-creation-handoff.md`, not `Content Creation Handoff.md`).
- **Version anything that gets revised significantly** — keep an old version with a date suffix if the new one departs meaningfully from the old.

---

## Notes

The methodologies in this repo encode hard-won patterns refined across many sessions of class delivery. They aren't theoretical — they reflect what actually works in practice, what students actually find confusing, and what consistently produces polished output from AI chats.

When something doesn't fit a pattern, the right move is usually to ask the lecturer (or yourself) a clarifying question rather than guess. Wrong assumptions get rebuilt three times. A 30-second clarification saves a 30-minute rework.
