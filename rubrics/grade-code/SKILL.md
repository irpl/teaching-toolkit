---
name: grade-code
description: >
  Grades student code submissions (.cs, .py, .aspx, .html, .css, .js, .java, etc.)
  against a rubric. Triggers on 'grade code', 'mark code', 'grade program',
  'mark assignment code', 'check code submission', or 'grade lab work'.
argument-hint: "[rubric description or assignment details]"
---

# Code Assignment Grading

Grades student programming assignments. Follows the shared /grade workflow for feedback and tracking.

## Reading Submissions

- Read **every** code file in the student's folder (may be nested in project subfolders).
- Common file types: `.cs`, `.py`, `.aspx`, `.aspx.cs`, `.html`, `.css`, `.js`, `.java`, `.cpp`, `.c`
- If files are inside a project folder (e.g., `WebApplication1/`), navigate into it.
- Also check for config files (`Web.config`, `appsettings.json`, etc.) when relevant.
- If a `.sln` or `.csproj` exists, note the project structure.

## Evidence Tiers — what actually counts as code evidence

Code rubrics grade **the code itself**, not the student's description of it or the program's outputs. When the source code is not directly observable, you must not award method/structure marks based on weaker forms of evidence. Use this hierarchy:

| Tier | Evidence | Awards |
|------|----------|--------|
| **A — Direct code** | `.cs`/`.py`/etc. file submitted, OR full code text inside a document, OR a clear, readable screenshot of the code on screen, OR readable frames extracted from a screen-share video at the IDE | Award rubric marks normally — every criterion is verifiable. |
| **B — Behavioural** | Clear console screenshot showing prompts, computed values, and formatting; or a clear screen-capture video showing the program running with values visible | Award only what is *directly observable in the output*: prompts (Problem Setup), specific tested values (Subtotal/Tax/Total math, only for the tier(s) actually tested), receipt items (DisplayReceipt items present), output formatting. **Do not** award method-structure marks (signature correctness, array use, while-loop validation) — these aren't visible in output. |
| **C — Verbal / claim only** | Student says in a video "I used a while loop to validate" or "my method returns the subtotal", with no code or behaviour to back it up | Award **0** for that criterion. A claim about code is not evidence of code. |
| **D — Blurry / unreadable** | Phone-camera video of a monitor where text is too small to read; transcript-only with no visible IDE or console | Treat as Tier C — no code marks awarded for the unreadable parts. Only award marks for what *is* clearly visible. |

### Common mistakes this prevents

- **Verbal walkthrough fallacy:** "She said in the video that her tax method takes amountAfterDiscount and returns 0.15 ×" → this is a claim, not evidence. 0 unless you've also seen the code.
- **Output-implies-code fallacy:** "Tax came out to $498.75 in the screenshot, so `CalculateTax` must be correct" → the math is verified, but the *method's existence, signature, and structure* is not. Award only the math-correctness portion.
- **One-tier-implies-all-tiers fallacy:** Output shows the 5% discount tier working → award credit for that tier only, not the full discount criterion. The 0% and 10% branches are unverified.
- **"Surely they have a while loop" fallacy:** A program that re-prompts on bad input could be using `while`, recursion, `goto`, or a try/catch retry. Without code, the *while-loop-specifically* requirement can't be confirmed.

### What to write in feedback when downgrading on evidence

Be explicit so the student knows what to provide for the grade to rise:
> "Method signature and array usage could not be verified without the source code file. Once the `.cs` file is submitted, the grade can be revised."

This makes the grade *provisional* and gives the student a path forward, rather than just being a punishment.

## Cosmetic vs functional deviations — don't deduct for cosmetic ones

When a student's code differs from the brief in ways that are purely **cosmetic** (typos, renamed identifiers, slightly different output labels, extra/missing optional parameters), do **not** reduce marks if the code still behaves correctly.

| Cosmetic (no deduction) | Functional (deduct) |
|-------------------------|---------------------|
| Method named `SumTotal` instead of brief's `CalculateSubtotal` — same return type, same parameter, correct logic | Method missing entirely or returns the wrong value |
| Output line reads `Before Discount: 1000.00` instead of `Subtotal: 1000.00` — same number shown | Subtotal not displayed at all, or wrong number |
| `Recipt` misspelled in receipt header but all required items present | Required receipt items missing |
| Extra parameter on a method that the implementation doesn't strictly need | Missing parameter that the brief required |
| Different prompt wording ("How many books you gonna buy?" vs brief's "Enter number of books:") | No prompt at all, or prompt asks for the wrong thing |

**Why:** the rubric measures whether the program does the right thing, not whether the student matched the brief's spelling. Penalising spelling on top of a working implementation gives a misleading picture of what the student actually understood.

**Always:** mention the cosmetic issue in the feedback comments (so the student can improve), but don't reduce marks for it. Phrase as "for future work, match the brief's exact naming for consistency", not as "you lost a mark on this".

## What to Assess

Grade against the rubric provided by the user or in a project CLAUDE.md. If no rubric is given, use these general criteria and ask the user for marks allocation:

### Functionality
- Does the code meet the assignment requirements?
- Do the features work as specified?
- Are required controls, components, or elements present?

### Code Quality
- Correct syntax — no errors that would prevent compilation/execution
- Appropriate use of language features (loops, conditions, methods, classes)
- Proper naming conventions for the language
- Code organization (separation of concerns, file structure)

### Specific Checks by Language

**ASP.NET (.aspx / .aspx.cs):**
- Server controls have `runat="server"`
- Event handlers are correctly wired (`OnClick`, `Page_Load`)
- `IsPostBack` check in `Page_Load` where needed
- Validation controls linked to correct targets
- Code-behind matches the .aspx markup

**Python (.py):**
- Proper indentation
- Use of functions/classes as required
- Input validation where specified
- File handling done correctly (with `with` statements)

**HTML/CSS/JS:**
- Valid structure (doctype, head, body)
- Semantic HTML where appropriate
- CSS linked/embedded correctly
- JavaScript event handling and DOM manipulation

**C# (.cs):**
- Proper class structure and access modifiers
- Exception handling where appropriate
- Correct use of data types
- Method signatures match requirements

## Deductions

Apply deductions only if the rubric specifies them. Common deduction categories:
- Syntax errors that prevent execution: note severity
- Missing `runat="server"` on ASP.NET controls
- Logic errors (e.g., initialization outside `!IsPostBack`)
- Use of inline script when code-behind was required
- Hardcoded values where dynamic input was expected

List each deduction with the specific issue and penalty in the feedback.

## Feedback Style for Code

- Reference specific file names and line numbers when noting issues.
- Quote small code snippets to illustrate problems or good practices.
- Distinguish between "missing entirely" vs "attempted but incorrect" — award partial marks for attempts.
- If a student used a different approach than expected but it works, give credit unless the rubric requires a specific technique.

## Feedback Template for Code Assignments

Use this exact structure for every student. Do not rearrange sections between students.

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
**Assessment:** [Assessment Name]<br>
**Files Reviewed:** [List all files read, e.g., Registration.aspx, Registration.aspx.cs]

---

## Overall Score: X/[Total] (X%)

---

## [Section Name] (X/[Section Total])

| Criteria | Marks | Status | Feedback |
|----------|-------|--------|----------|
| [Criterion] | X/[Max] | Earned/Partial/Missing | [1-3 sentences referencing specific code] |

[Repeat table for each rubric section]

## Deductions (if applicable)

| Issue | File | Penalty |
|-------|------|---------|
| [Description] | [filename:line] | -X |
| **Total Deductions** | | **-X** |

*(If no deductions: "No deductions applied.")*

---

## Summary

| Section | Score |
|---------|-------|
| [Section 1] | X/[Max] |
| [Section 2] | X/[Max] |
| Deductions | -X |
| **Total** | **X/[Total] (X%)** |

### Strengths
- [What was done well — reference specific code]

### Areas for Improvement
- [What needs work — reference specific code]

---

*Feedback generated for assessment purposes.*
```

### Status Values
- **Earned** — Full marks awarded
- **Partial** — Some marks awarded (explain what was missing)
- **Missing** — Not implemented, 0 marks

## AI Indicators for Code Assignments

Watch for these in addition to the general indicators in the shared /grade skill:

- **Overly clean code with zero syntax errors** — beginner students almost always have minor issues (missing semicolons, wrong casing, typos in variable names). Flawless code from a weak student is suspicious.
- **Excessive comments explaining every line** — AI-generated code often has a comment above every block. Real students rarely comment this thoroughly.
- **Unusually consistent naming conventions** — perfect camelCase or PascalCase everywhere with no slips. Students usually mix styles at least once.
- **Advanced patterns beyond course level** — e.g., LINQ, async/await, design patterns, or error handling sophistication that hasn't been taught yet.
- **Generic variable names that are still descriptive** — AI tends to use names like `userInput`, `resultList`, `isValid` consistently. Students often use `x`, `temp`, `myVar`, or names from class examples.
- **Code that works perfectly but the student can't explain it** — note if the code quality doesn't match what you'd expect from other parts of their submission.
- **Identical code structure across students** — same method order, same comment style, same variable names in multiple submissions. Flag both students.
- **Try-catch blocks everywhere** — AI over-applies error handling. Students at this level usually skip it entirely or use it only where taught.
