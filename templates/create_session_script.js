/**
 * ============================================================
 * CLASS TEACHING SCRIPT BUILDER
 * ============================================================
 *
 * This is a reusable Node.js script that produces a verbatim
 * teaching script as a .docx file. The output matches a polished,
 * consistent style: SAY: paragraphs for what to read aloud,
 * orange [direction] callouts for stage directions, plain grey
 * stage notes, and a "Notes for Lecturer" section at the end.
 *
 * ============================================================
 * HOW TO USE THIS FILE
 * ============================================================
 *
 * 1. SAVE this file as `create_session_script.js` (or similar).
 *
 * 2. INSTALL dependencies:
 *      npm install docx
 *
 *    The `docx` library is the only dependency.
 *
 * 3. EDIT the content:
 *    - Replace the {COURSE_CODE}, {COURSE_NAME}, {N}, {SESSION_TOPIC}
 *      placeholders in the title page section.
 *    - Replace the example slide sections with your real content.
 *    - Add or remove slide sections as needed.
 *    - Update the "Notes for Lecturer" bullets at the end.
 *    - Update the OUTPUT_FILENAME constant.
 *
 * 4. RUN:
 *      node create_session_script.js
 *
 *    The .docx file will be saved to the path defined by
 *    OUTPUT_PATH below.
 *
 * 5. VALIDATE (optional but recommended):
 *      python3 /mnt/skills/public/docx/scripts/office/validate.py {OUTPUT_FILENAME}
 *    Or open the file in Word to visually inspect.
 *
 * ============================================================
 * STYLE GUIDE — WHAT EACH HELPER PRODUCES
 * ============================================================
 *
 *   say("text here")
 *     Bold teal "SAY: " label, then dark text in curly quotes.
 *     This is what the lecturer READS VERBATIM. Each call should
 *     be one self-contained chunk of speech, a few sentences long.
 *     Avoid bullet points inside SAY blocks — flowing prose only.
 *
 *   direction("text here")
 *     Italic orange text on pale orange shading.
 *     Used for: engagement prompts, things the lecturer should DO
 *     (with timing/tone notes), what to listen for in student
 *     responses. Wrap the text in [square brackets] inside the
 *     string — the helper does not add them.
 *
 *   stageNote("text here")
 *     Italic mid-grey text, no shading.
 *     Less prominent stage notes (e.g. "no talking points needed").
 *     Same rule on [square brackets] as direction().
 *
 *   slideHead("Slide N: Title")
 *     Heading 1 — marks each slide section in the script.
 *     Use exactly the format "Slide N: Title". The final section
 *     should be "Notes for Lecturer" (still uses slideHead).
 *
 *   bullet("text here")
 *     Bullet point used in the Notes for Lecturer section only.
 *     Don't use bullets inside SAY blocks.
 *
 * ============================================================
 * STANDING RULES
 * ============================================================
 *
 *   1. NO exam question number references (Q1, Q2, Q5(c), etc.)
 *      in SAY blocks or anywhere students will see. Topic names
 *      only. Exam Q numbers ARE allowed in the Notes for Lecturer
 *      section because that's private.
 *
 *   2. NO named student call-outs in SAY blocks (no "Tyreke, you
 *      go first"). The lecturer directs in the moment. Stage
 *      directions can mention students if useful.
 *
 *   3. NO scenario reuse across sessions. Track examples used
 *      and pick fresh ones each time.
 *
 * ============================================================
 */

const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, HeadingLevel,
        AlignmentType, LevelFormat, BorderStyle, ShadingType } = require("docx");

// ============================================================
// COLOR CONSTANTS (do not change unless redesigning the system)
// ============================================================

const DARK = "1A2B33";      // Almost-black, body text
const TEAL = "0E7C86";      // SAY: labels, headings
const GREY = "6B8290";      // Subtitle, plain stage notes
const ORANGE = "E8913A";    // Stage directions / engagement
const ORANGE_BG = "FFF3E0"; // Pale orange shading for directions

// ============================================================
// OUTPUT CONFIGURATION
// ============================================================

const OUTPUT_FILENAME = "Session_Script.docx"; // Edit this
const OUTPUT_PATH = `/home/claude/${OUTPUT_FILENAME}`; // Or wherever

// ============================================================
// HELPER FUNCTIONS — DO NOT MODIFY
// ============================================================

function say(text) {
  return new Paragraph({
    spacing: { after: 160 },
    children: [
      new TextRun({ bold: true, color: TEAL, size: 22, text: "SAY: " }),
      new TextRun({ color: DARK, size: 22, text: `\u201C${text}\u201D` })
    ]
  });
}

function direction(text) {
  return new Paragraph({
    spacing: { after: 160 },
    shading: { fill: ORANGE_BG, type: ShadingType.CLEAR },
    children: [new TextRun({ italics: true, color: ORANGE, size: 22, text: `[${text}]` })]
  });
}

function stageNote(text) {
  return new Paragraph({
    spacing: { after: 200 },
    children: [new TextRun({ italics: true, color: GREY, size: 22, text: `[${text}]` })]
  });
}

function slideHead(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [new TextRun({ text })]
  });
}

function bullet(text) {
  return new Paragraph({
    spacing: { after: 100 },
    numbering: { reference: "bullets", level: 0 },
    children: [new TextRun({ size: 22, text })]
  });
}

// ============================================================
// CONTENT — EDIT THIS SECTION
// ============================================================

async function main() {
  const c = []; // Array of paragraphs that will become the document body

  // ----------------------------------------------------------
  // TITLE PAGE — edit placeholders below
  // ----------------------------------------------------------
  c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 },
    children: [new TextRun({ font: "Georgia", bold: true, color: DARK, size: 36, text: "{COURSE_CODE} \u2014 {COURSE_NAME}" })] }));
  c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 },
    children: [new TextRun({ font: "Georgia", color: TEAL, size: 28, text: "Session {N} Talking Points" })] }));
  c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 },
    children: [new TextRun({ color: GREY, size: 22, text: "Topic: {SESSION_TOPIC}" })] }));
  c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 },
    children: [new TextRun({ color: GREY, size: 22, text: "Duration: ~60 minutes  |  Format: Verbatim script" })] }));
  c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
    border: { bottom: { style: BorderStyle.SINGLE, color: TEAL, size: 6, space: 8 } },
    children: [] }));

  // ----------------------------------------------------------
  // SLIDE 1 — Title slide (typical pattern: stageNote only)
  // ----------------------------------------------------------
  c.push(slideHead("Slide 1: Title Slide"));
  c.push(stageNote("No talking points needed \u2014 just greet students as they join"));

  // ----------------------------------------------------------
  // SLIDE 2 — Opening / framing
  // ----------------------------------------------------------
  c.push(slideHead("Slide 2: {Opening / Where We Are}"));
  c.push(say("{Opening greeting and framing. State what was covered last session, what tonight covers, and how it fits the bigger picture.}"));
  c.push(say("{Walk through tonight's agenda in plain language. List the 2\u20134 main things you'll cover.}"));
  c.push(direction("{Optional opener: any reminders or quick check-ins, e.g. assignment due dates}"));

  // ----------------------------------------------------------
  // SLIDE 3 — Concept introduction
  // ----------------------------------------------------------
  c.push(slideHead("Slide 3: {Concept Introduction}"));
  c.push(say("{Introduce the concept clearly. Define it in plain language.}"));
  c.push(say("{Give an example or analogy that makes the concept concrete. Use a regional/local example for relatability where possible.}"));
  c.push(say("{Tie the example back to the concept explicitly. Don't assume students will infer the link.}"));

  // ----------------------------------------------------------
  // SLIDE 4 — Deep dive with engagement prompt
  // ----------------------------------------------------------
  c.push(slideHead("Slide 4: {Deep Dive Topic}"));
  c.push(say("{Walk through the topic in detail. Each SAY: should be self-contained \u2014 don't run on.}"));
  c.push(say("{Continue with the next sub-point. Reinforce the through-line so students don't lose the thread.}"));
  c.push(say("{Synthesise: pull the sub-points together into one clean statement.}"));
  c.push(direction("Engagement prompt: \u201C{Set up a scenario in 1\u20132 sentences. Then ask an open-ended question.}\u201D Listen for: {what good answers will sound like}. If they're stuck, probe with: \u201C{a fallback prompt}\u201D"));

  // ----------------------------------------------------------
  // SLIDE 5 — Comparison / distinction (good for confusion points)
  // ----------------------------------------------------------
  c.push(slideHead("Slide 5: {Comparison or Distinction}"));
  c.push(say("{Set up the comparison. State what's being compared and why the distinction matters.}"));
  c.push(say("{Describe the first thing in concrete terms.}"));
  c.push(say("{Describe the second thing using parallel structure to make the contrast easy to see.}"));
  c.push(say("{State the key distinction in one memorable sentence. Introduce a mnemonic if there is one.}"));

  // ----------------------------------------------------------
  // SLIDE 6 — Worked example or application
  // ----------------------------------------------------------
  c.push(slideHead("Slide 6: {Application or Worked Example}"));
  c.push(say("{Set up the worked example. State what it is and why you're using it.}"));
  c.push(say("{Walk through the example step by step. Don't rush \u2014 students learn from the process.}"));
  c.push(say("{Conclude: state what it demonstrated and how it generalises.}"));

  // ----------------------------------------------------------
  // SLIDE 7 — Summary / closing
  // ----------------------------------------------------------
  c.push(slideHead("Slide 7: {Summary / Closing}"));
  c.push(say("{Recap what was covered: \u2018Tonight we covered X, Y, and Z.\u2019 Keep it brief.}"));
  c.push(say("{State what's coming next session. Helps students prepare.}"));
  c.push(say("{Closing line. \u2018Good work tonight. See you {next class day}.\u2019}"));
  c.push(direction("Answer any questions, then close out."));

  // ----------------------------------------------------------
  // NOTES FOR LECTURER (always last; private; not read aloud)
  // Exam question numbers / mark allocations / etc. are OK here.
  // ----------------------------------------------------------
  c.push(slideHead("Notes for Lecturer"));
  c.push(bullet("Total talking time: ~{N\u2013N} min"));
  c.push(bullet("{Common confusion point to watch for during this session}"));
  c.push(bullet("{Where to compress if running short on time}"));
  c.push(bullet("{Where to expand if running long}"));
  c.push(bullet("{Any private references \u2014 exam Q#s, mark allocations, etc., are fine here}"));

  // ============================================================
  // BUILD AND SAVE — DO NOT MODIFY BELOW THIS LINE
  // ============================================================

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
        levels: [{
          level: 0,
          format: LevelFormat.BULLET,
          text: "\u2022",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      }]
    },
    sections: [{
      properties: {
        page: {
          size: { width: 12240, height: 15840 }, // US Letter
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
        }
      },
      children: c
    }]
  });

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(OUTPUT_PATH, buffer);
  console.log(`Script saved to ${OUTPUT_PATH}`);
}

main().catch(console.error);
