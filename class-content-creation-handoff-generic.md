# Class Content Creation — Handoff Document

This document captures a methodology for producing high-quality class teaching materials — paired slide decks and verbatim teaching scripts — for any course. It's intended to let any new chat (or new Claude instance) pick up this style of work and produce session materials that match a polished, consistent standard.

Read this document end-to-end before producing anything. The patterns are interlocking — skipping one section will produce work that looks "close but wrong."

The user will provide course-specific context (course name, students, schedule, units, etc.) — this doc covers everything else.

---

## 1. What Gets Produced

**Every teaching session produces TWO paired deliverables, always together:**

1. **A PowerPoint slide deck** (`.pptx`) — for displaying during class
2. **A Word document teaching script** (`.docx`) — the lecturer reads this verbatim during class and ad-libs from it

These are always produced as a pair. Never produce one without the other unless explicitly asked. The deck is what students see; the script is the lecturer's lectern document.

**Filenames follow this pattern:**
- `{COURSE_CODE}_Session{N}.pptx`
- `{COURSE_CODE}_Session{N}_Script.docx`

**Other deliverables sometimes produced:**
- Coursework brief documents (`.docx`)
- Answer keys for in-class practice (`.docx`)
- Grading rubrics (`.docx`)
- Semester plan documents (Markdown or `.docx`)

---

## 2. Standing Rules (Establish Early With Lecturer)

These rules are common across courses. Confirm each one with the lecturer at the start of a new course relationship — they may or may not all apply, but the patterns below are the defaults that produce safe, professional materials.

### 2.1 No Exam Question Number References in Student-Facing Materials

When materials are seen or read by students, do not write "Q1," "Q2," "Essay Q5(c)," or anything mapping content to specific exam question numbers. This prevents leaking exam structure to students and avoids over-coaching.

**Acceptable in student-facing materials:** topic names (e.g. "BPI," "Testing," "Project Management").

**Acceptable in private lecturer notes** (the "Notes for Lecturer" section at the end of the script and stage directions): exam question numbers can appear here freely — these aren't read to students.

**Subtle violations to also avoid:**
- "The exam expects you to..."
- "This is exam-relevant..."
- "You'll see this on the test..."

These should be reworded to focus on understanding and articulation rather than test prep framing.

### 2.2 No Named Student Call-Outs in Engagement Prompts

Engagement prompts and discussion questions in the script should be **generic**. Never include "[Name], you start us off" or "Call on [Name] first." The lecturer directs in the moment based on who's there and engaged.

**Wrong:** "Now your turn. Give me another example. [Name], you go first."

**Right:** "Now your turn. Give me another example."

Stage directions to the lecturer can mention students if useful (e.g. "Expected: a brief answer; if students are quiet, prompt with X"), but the spoken-aloud `SAY:` text never names anyone.

### 2.3 No Repeat of Scenario Companies/Examples

Each session should use a fresh scenario or example to keep things vivid. Maintain a running mental list of what's been used and avoid repeats. Where the course has a regional or industry context, anchor scenarios there for relatability.

---

## 3. The Slide Design System

This is a polished, consistent design system that produces professional decks. Establish it with the lecturer at the start of a new course (they may want to adjust colors or accents) and then **lock it** — apply it across every deck without re-specifying.

### 3.1 Default Color Palette

```
Top bar:        #48BF84  (green, on every slide)
Dark bg:        #1A3C5E  (navy)
Card on dark:   #0D2137  (very dark navy)
Light bg:       #F0F4F8  (cool light grey)
Box on light:   #F0F7FF  (very pale blue with left colored border)

Accents:
  Teal:         #2E86AB
  Green:        #48BF84
  Orange:       #E8734A
  Purple:       #7B4EAF
  Red:          #D64545

Text:
  On dark:      #CBD5E0  (light grey, for body text on navy)
  On dark:      #FFFFFF  (white, for headings on navy)
  On light:     #4A5568  (mid-grey, for body text on light)
  On light:     #1A3C5E  (navy, for headings on light)
```

Adjust the palette to match course or institutional branding if specified, but keep the dark/light alternation system and the role-based color assignments.

### 3.2 Typography

- **Headings:** Georgia, bold
- **Body text:** Calibri
- **Always specify these fonts explicitly in pptxgenjs** — don't rely on defaults

### 3.3 Standard Slide Components

**Top bar:** Every slide has a thin colored bar at the very top:
```javascript
slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: GREEN } });
```

**Hero icon (used on title slide and key transitions):** Double-circle pattern — a darker outer circle with a colored inner circle containing a white icon.

**Callout boxes (most common element):** A rectangle with a thin colored stripe on the LEFT edge. On dark slides, the rectangle uses the dark card color; on light, the light box color. Inside, a colored bold label, then body text.

**Bulb callouts:** Orange light bulb icon + italic orange text in a callout box. Used for emphasis, asides, "things to remember." Never put exam-relevance language here.

**Summary slides:** Use a green checkmark icon next to each item, with a dark sidebar panel showing "The Big Picture" copy on the right. End the deck with a colored bottom bar showing what's next.

**Title slide:** Always includes course code as a small label, the session title in big Georgia, then a subtitle, then session metadata. Bottom bar reads the institution name in the dark card color.

### 3.4 Slide Layout (16:9)

PowerPoint is in 16:9 layout. Coordinate space is **10 wide × 5.625 tall** (inches).

```javascript
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "{LECTURER_NAME}";
pres.title = "{COURSE_CODE} Session N";
```

### 3.5 Alternating Backgrounds Across Detail Slides

When producing 4-7 detail slides in a row (e.g. five characteristics, seven considerations), **alternate light and dark backgrounds** session by session. This creates visual rhythm and prevents fatigue. Pattern: light, dark, light, dark, ...

### 3.6 Icons

Icons come from `react-icons/fa` (Font Awesome). Pick icons that semantically match the topic. Common ones:
- `FaCheckCircle` (green, for summary slides)
- `FaLightbulb` (orange, for callouts)
- `FaProjectDiagram`, `FaCogs`, `FaVial`, `FaChartLine` (general topic icons)
- `FaShieldAlt`, `FaUserTie`, `FaFileContract` (professional contexts)
- Browse the full library at https://react-icons.github.io/react-icons/icons?name=fa for more.

**CRITICAL ICON BUG:** `react-icons` uses `fill="currentColor"`. Hex values passed without `#` prefix fall back to black. **Always prepend `#` in the `renderIconSvg` helper.** See section 5 for the correct helper code.

---

## 4. The Script Style

### 4.1 Format

Scripts are written as **flowing conversational prose** that the lecturer reads VERBATIM and ad-libs from. Never bullet points in the body. Mobile-friendly format (lecturers often read off phones via Google Docs).

**No tables. No colored cells/boxes. No multi-column layouts.** Google Docs mobile mangles them. Plain paragraphs only.

### 4.2 Components

**Slide heading (`Heading 1`):** `Slide N: Title` — marks each slide section in the script.

**`SAY:` paragraphs:** A bold colored `SAY:` label, followed by the verbatim words the lecturer reads, in dark text wrapped in curly quotes `\u201C ... \u201D`. Each `SAY:` is one self-contained chunk of speech, a few sentences long.

```javascript
function say(text) {
  return new Paragraph({
    spacing: { after: 160 },
    children: [
      new TextRun({ bold: true, color: TEAL, size: 22, text: "SAY: " }),
      new TextRun({ color: DARK, size: 22, text: `\u201C${text}\u201D` })
    ]
  });
}
```

**`[Direction]` paragraphs:** Stage directions in italic orange text on a pale orange background. Used for: engagement prompts, things the lecturer should do/say with timing/tone notes, what to listen for in student responses.

```javascript
function direction(text) {
  return new Paragraph({
    spacing: { after: 160 },
    shading: { fill: ORANGE_BG, type: ShadingType.CLEAR },
    children: [new TextRun({ italics: true, color: ORANGE, size: 22, text: `[${text}]` })]
  });
}
```

**Plain stage notes (greyed out):** Less prominent stage directions — italic mid-grey text with no shading.

```javascript
function stageNote(text) {
  return new Paragraph({
    spacing: { after: 200 },
    children: [new TextRun({ italics: true, color: GREY, size: 22, text: `[${text}]` })]
  });
}
```

### 4.3 Script Color Palette

These colors are slightly different from the slide palette — designed for paper/screen reading:
```
DARK:       #1A2B33  (almost-black, body text)
TEAL:       #0E7C86  (SAY: labels, headings)
GREY:       #6B8290  (subtitle, plain stage notes)
ORANGE:     #E8913A  (stage directions/engagement)
ORANGE_BG:  #FFF3E0  (light orange shading for directions)
GREEN_DARK: #2D7A5F  (used in answer keys for "concepts to include" headers)
```

### 4.4 Title Page Pattern

Every script starts with a centered title block: course name, session title, topic, duration estimate, format note, then a horizontal teal divider.

```javascript
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 },
  children: [new TextRun({ font: "Georgia", bold: true, color: DARK, size: 36, text: "{COURSE_CODE} \u2014 {COURSE_NAME}" })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 },
  children: [new TextRun({ font: "Georgia", color: TEAL, size: 28, text: "Session N Talking Points" })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 },
  children: [new TextRun({ color: GREY, size: 22, text: "Topic: ..." })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 },
  children: [new TextRun({ color: GREY, size: 22, text: "Duration: ~60 minutes  |  Format: Verbatim script" })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
  border: { bottom: { style: BorderStyle.SINGLE, color: TEAL, size: 6, space: 8 } },
  children: [] }));
```

### 4.5 Notes for Lecturer Section (Always Last)

Every script ends with a `Heading 1` "Notes for Lecturer" section containing bullets. This is private — for the lecturer's eyes only. Things to include:
- Total expected talking time
- Common confusion points to watch for
- Where to compress if running short on time
- Where to expand if running long
- Optional engagement to skip or keep
- Exam question numbers can appear here (rule 2.1 doesn't apply to these private notes)

---

## 5. Technical Pipeline — Slides

### 5.1 Tech Stack

```
node + pptxgenjs + react-icons + react-dom/server + sharp
```

### 5.2 Build Approach

Slides are built in JavaScript (`.js`) using `pptxgenjs`. Icons from `react-icons` are rendered to SVG via `ReactDOMServer.renderToStaticMarkup`, converted to PNG via `sharp`, then embedded as base64 image data in the deck.

### 5.3 Required Helpers (Every Build Script)

```javascript
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const { FaCheckCircle, FaLightbulb /* etc */ } = require("react-icons/fa");

// CRITICAL: '#' prefix is required. Without it, react-icons defaults to black.
function renderIconSvg(Icon, color, size = 256) {
  const validColor = color.startsWith("#") ? color : "#" + color;
  return ReactDOMServer.renderToStaticMarkup(
    React.createElement(Icon, { color: validColor, size: String(size) })
  );
}

async function iconPng(Icon, color, size = 256) {
  const svg = renderIconSvg(Icon, color, size);
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

// Color constants — these match the slide design system:
const NAVY = "1A3C5E";
const CARD_DARK = "0D2137";
const LIGHT = "F0F4F8";
const DEF_BG = "F0F7FF";
const GREEN = "48BF84";
const TEAL = "2E86AB";
const ORANGE = "E8734A";
const PURPLE = "7B4EAF";
const RED = "D64545";
const GREY_DARK = "4A5568";
const GREY_LIGHT = "CBD5E0";
const WHITE = "FFFFFF";

function topBar(slide, pres) {
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: GREEN } });
}
```

### 5.4 Build & QA Process

```bash
# Build
node create_session{N}_slides.js

# Convert to PDF for visual QA
python3 /mnt/skills/public/pptx/scripts/office/soffice.py --headless --convert-to pdf {COURSE_CODE}_Session{N}.pptx

# Rasterize PDF pages to JPEG for inspection
pdftoppm -jpeg -r 150 {COURSE_CODE}_Session{N}.pdf s{N}

# View each JPEG page to verify visual correctness — look for:
# - Icon colors correct (not black)
# - Text not overflowing boxes
# - Card heights appropriate to content
# - No accidental rule violations (Q# references, etc.)
```

If any slide looks wrong, **fix the build script and rebuild — never edit the .pptx directly.**

After QA passes, copy to outputs:

```bash
cp {COURSE_CODE}_Session{N}.pptx /mnt/user-data/outputs/
```

Then call `present_files` to surface to the lecturer.

---

## 6. Technical Pipeline — Scripts

### 6.1 Tech Stack

```
node + docx (the JavaScript docx library)
```

### 6.2 Required Imports

```javascript
const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, HeadingLevel,
        AlignmentType, LevelFormat, BorderStyle, ShadingType } = require("docx");
```

### 6.3 Document Structure Pattern

```javascript
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Calibri", size: 23 } } },
    paragraphStyles: [{
      id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { font: "Georgia", bold: true, color: DARK, size: 32 },
      paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 }
    }]
  },
  numbering: {
    config: [{
      reference: "bullets",
      levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }]
    }]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },  // US Letter
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: c  // array of paragraphs
  }]
});

const buffer = await Packer.toBuffer(doc);
fs.writeFileSync("/home/claude/{COURSE_CODE}_Session{N}_Script.docx", buffer);
```

### 6.4 Build & Validate

```bash
node create_session{N}_script.js

# Validate structure
python3 /mnt/skills/public/docx/scripts/office/validate.py {COURSE_CODE}_Session{N}_Script.docx

# Output should show "All validations PASSED!"

# Then copy to outputs
cp /home/claude/{COURSE_CODE}_Session{N}_Script.docx /mnt/user-data/outputs/
```

### 6.5 Known Construction Pitfalls

**Page breaks via `pageBreakBefore: true` on a dedicated `h1Page()` paragraph helper** — not on the heading itself.

**`cantSplit: true` on all `TableRow` constructors** — prevents tables from splitting across pages. Critical: `sed`-style find/replace will MISS multi-line constructors and named factory functions. Patch these manually.

---

## 7. Working Patterns

### 7.1 Plan Before Execute

Before building anything substantive, **describe the plan in plain English** and wait for the lecturer to approve. Examples:
- Number of slides + topic per slide
- Format choices ("block-based vs one-per-slide")
- Engagement prompts (offer 2-3 options, recommend one, let lecturer pick)
- Scenarios for examples (offer alternatives if relevant)

After approval, build. Don't build first and ask later.

### 7.2 Concise & Directive Communication

Lecturers tend to write short directive instructions and expect you to fill in the full scope from prior context. Examples:
- "yes" = proceed with what you just proposed
- "do it now" = no further confirmation needed
- "today is X. what am I doing?" = remind them of the planned session and offer to build it

Match this energy. Don't pad responses with caveats. Be direct.

### 7.3 Incremental Communication

Lecturers often share feedback from stakeholders (course coordinators, department heads, etc.) as it arrives. When they say "I'm clarifying with [person] — don't make changes yet," **hold all changes** until they confirm.

### 7.4 Engagement Prompts (Pattern)

When the lecturer asks for engagement/discussion prompts:

1. **Offer 2-3 options.** Different framings (e.g. scenario probe vs counter-example challenge vs diagnostic flip).
2. **Recommend one.** Give a one-line reason.
3. **Wait for the lecturer's choice.** Don't just pick one and apply it.
4. **Once chosen, write it as a direction block** in the script using the orange callout style.
5. **No named call-out** in the spoken-aloud part (rule 2.2).

### 7.5 Address Common Confusion Points Proactively

Many courses have terminology that students consistently confuse — words that sound similar but mean different things, or phrases that appear in two units with different meanings. Ask the lecturer early in the engagement what those confusion points are for their course, and weave clarifications into the relevant sessions explicitly. Use mnemonics where they help.

### 7.6 Mirror Real Scenarios Without Naming Them

If exam scenarios or assessment cases use specific company names, you can deliberately mirror those scenarios in teaching examples — same industry, same integration challenge — without naming the specific company. This builds student familiarity with the pattern without violating rule 2.1.

---

## 8. Session Length & Pacing

Default target: ~60 minutes of class time. Confirm with the lecturer — some courses run shorter or longer.

Approximate pacing:
- 10-18 slides per session
- Each slide ~3-4 minutes of talking
- Engagement prompts add 2-5 minutes each
- Always leave 5 minutes for closing / questions

In the "Notes for Lecturer" section, suggest where to compress (if running short) and where to expand (if running long).

---

## 9. End-to-End Session Build Workflow

When the lecturer says "build SX" or "yes" to a session proposal:

1. **Plan the session structure in plain English** — list slides 1 through N with a one-line description of each. Wait for approval if not already given.

2. **Build the script first.** Create `/home/claude/create_session{N}_script.js`. Include `say()`, `direction()`, `stageNote()`, `slideHead()`, `bullet()` helpers. Build paragraphs in array `c`, write to `/home/claude/{COURSE_CODE}_Session{N}_Script.docx`.

3. **Validate the script:**
   ```bash
   python3 /mnt/skills/public/docx/scripts/office/validate.py {COURSE_CODE}_Session{N}_Script.docx
   ```
   Should report "All validations PASSED!"

4. **Build the slide deck.** Create `/home/claude/create_session{N}_slides.js`. Use the icon helpers, color constants, and `topBar()` helper from section 5.3. Build all slides, write to `/home/claude/{COURSE_CODE}_Session{N}.pptx`.

5. **QA the deck visually:**
   ```bash
   python3 /mnt/skills/public/pptx/scripts/office/soffice.py --headless --convert-to pdf {COURSE_CODE}_Session{N}.pptx
   pdftoppm -jpeg -r 150 {COURSE_CODE}_Session{N}.pdf s{N}
   ```
   Use the `view` tool on each `s{N}-XX.jpg` to verify. Check for:
   - Icon colors not black (means color hex didn't have `#` prefix)
   - Text not overflowing boxes
   - No exam Q# references (rule 2.1)
   - No named student call-outs (rule 2.2)
   - Card heights appropriate for content density

6. **Fix any issues** by editing the build script and rebuilding (never edit `.pptx` directly).

7. **Copy to outputs:**
   ```bash
   cp /home/claude/{COURSE_CODE}_Session{N}.pptx /mnt/user-data/outputs/
   cp /home/claude/{COURSE_CODE}_Session{N}_Script.docx /mnt/user-data/outputs/
   ```

8. **Use `present_files` tool** to surface both files. The slide deck filepath should be first.

9. **Brief recap:** Tell the lecturer the slide count, total estimated time, and key pedagogical moves. Mention any standing-rule violations you caught and fixed mid-build (transparency).

10. **Offer a YouTube title** at the end if the lecturer publishes their sessions. Style: punchy, specific, listicle-friendly. Examples of the style: "5 Steps Explained — From Plan to Production," "4 Approaches Compared — When to Use Each One," "Strategic Fit, Functional Integration & 7 Keys to Making It Work."

---

## 10. Common Edits After Initial Build

Lecturers frequently request post-build edits. Patterns:

### Swap a scenario
- Find every reference to the original scenario in BOTH the script and slides
- Replace with the new scenario in both files
- If the new scenario changes integration partners or stakeholders, update those too
- Re-validate, re-render, re-copy, re-present

### Add an engagement prompt
- Insert a `direction()` paragraph between two `say()` paragraphs in the script
- The prompt itself goes in the spoken `SAY:` part inside curly quotes
- Stage notes for the lecturer (expected responses, fallback probes) go in plain text after the spoken part, all wrapped in the orange `[direction]` block
- No named call-outs (rule 2.2)

### Strip exam Q# references
- Search slides and script for `Q1`, `Q2`, `Q3`, etc., and "Question N" patterns
- Replace with topic names
- "The exam expects X" → "You need to be able to X"
- Re-validate, re-render, re-copy, re-present

---

## 11. Onboarding to a New Course

When starting on a new course, ask the lecturer for:

1. **Course code, full name, and institution** — for filenames and title slides
2. **Lecturer's name** — for the `pres.author` field
3. **Schedule** — class days/times, semester start and end, session length
4. **Class size and student names if applicable** — for the lecturer's planning context (never appears in student-facing materials)
5. **Unit/module list** — to map sessions to content
6. **Assessment structure** — exam format, coursework weights, due dates, exam scenarios if any
7. **Common confusion points** — terminology that students typically mix up
8. **Existing constraints** — e.g. what tools are used (Canvas, Moodle, Jira, etc.), whether sessions are recorded, whether scripts are read off mobile
9. **Branding preferences** — whether the default color palette is acceptable or needs to match institutional branding

Confirm the standing rules from section 2 explicitly. They are sensible defaults but every lecturer can adjust.

---

## 12. Quick Reference: Interpreting Common Directives

When the lecturer gives a directive that's ambiguous:

- **"build X"** without prior plan discussion → Propose the structure first, wait for approval
- **"do it"** with prior plan in context → Just build it
- **"youtube title for X"** → Produce one, no preamble
- **"today is X, what am I doing?"** → Remind them of the planned session, offer to build
- **"give me X"** (questions, prompts, etc.) → Provide options + a recommendation, then wait for selection
- **"continue"** → Resume from wherever the last action stopped (often: present files, give summary)
- **A correction or pushback** → Acknowledge, fix immediately, don't over-explain

---

## 13. Other Useful Deliverables

Beyond slide decks and scripts, lecturers often need:

### Coursework brief documents
- Standard CCCJ-style or institution-style header (course code, name, programme, year group, due date, weighting)
- Scenario / case study setup (200-400 words)
- Tasks broken out clearly with mark allocations
- Submission requirements (length, format, file type, referencing style)
- Marking rubric (table format, criteria → marks → what we're looking for)
- Important notes (late penalties, AI disclosure, originality requirements)

### Answer keys for in-class practice
- Question-by-question structure
- "A complete answer should include:" with bulleted concepts
- "If they miss something:" probe in orange-highlighted callout — gives the lecturer a way to draw out missing concepts without giving the answer away
- Closing notes flagging common confusion patterns to watch for

### Canvas/announcement-ready posts
- Short (3-5 sentences)
- Tells students what's happening tonight
- Includes any reminders (assignment due dates, things to bring)
- Casual tone, no formal headers
- "See you at [time]" sign-off

### Semester / session plans
- Markdown format works well
- Table of sessions with date, day, unit, topic, assessment activity
- Risk register with mitigation
- Pre-session checklist

---

## 14. Key Principles to Internalize

If everything else in this document is forgotten, these principles produce most of the value:

1. **Pair every deck with a verbatim script.** Don't ship one without the other.
2. **Lock the design system early and don't drift.** Consistency across sessions matters more than novelty within a session.
3. **Programmatic generation, never manual editing.** Edit the build script and rebuild — never edit the binary file.
4. **Visual QA every deck before shipping.** Convert to PDF, rasterize to JPEG, view every page.
5. **Plan before execute.** A 30-second plan saves a 30-minute rebuild.
6. **Be concise.** Lecturers are busy. Match their directive energy.
7. **No exam Q# references in student-facing materials.** Period.
8. **No named student call-outs in spoken script lines.** Period.
9. **Read past build scripts before guessing patterns.** They encode subtleties that don't appear in any documentation.
10. **When something doesn't fit a pattern, ask. Don't guess.**

---

## End

This document captures a methodology for class content production that has been refined across many sessions of consistent, high-quality output. Apply it consistently and the work will match a polished standard from day one.

If something in a new session doesn't fit a pattern in this doc, ask the lecturer rather than guessing. They prefer a quick clarifying question over a wrong assumption rebuilt three times.
