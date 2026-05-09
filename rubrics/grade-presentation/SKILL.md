---
name: grade-presentation
description: >
  Grades student presentation submissions (.pptx) including slide content, design,
  media, animations, and transitions. Triggers on 'grade presentation', 'mark PowerPoint',
  'grade pptx', 'mark slides', 'check presentation submission', or 'grade slideshow'.
argument-hint: "[rubric description or assignment details]"
---

# Presentation Assignment Grading

Grades PowerPoint and presentation assignments. Follows the shared /grade workflow for feedback and tracking.

## Extracting Content from .pptx Files

.pptx files are ZIP archives. To analyse:

### Step 1: Copy and Extract
```bash
powershell -Command "Copy-Item 'PATH_TO_PPTX' 'STUDENT_FOLDER/temp.zip'; Expand-Archive -Path 'STUDENT_FOLDER/temp.zip' -DestinationPath 'STUDENT_FOLDER/temp_extract' -Force"
```

### Step 2: Key Files to Read
| File | Contains |
|------|----------|
| `ppt/presentation.xml` | Overall presentation settings |
| `ppt/slides/slide1.xml` ... `slideN.xml` | Individual slide content |
| `ppt/slides/_rels/slideN.xml.rels` | Relationships (images, videos, hyperlinks, audio) |
| `ppt/media/` | Embedded media files |

### Step 3: What to Look for in Slide XML
| Feature | XML Element |
|---------|-------------|
| Animations/timing | `<p:timing>` |
| Auto-advance | `<p:transition advTm="5000">` (milliseconds) |
| Hyperlink to slide | `<a:hlinkClick r:id="rIdX" action="ppaction://hlinksldjump"/>` |
| Background | `<p:bg>` |
| Background colour | `<a:srgbClr val="XXXXXX">` |
| Footer | `<p:ph type="ftr">` |
| Date | `<p:ph type="dt">` |
| Slide number | `<p:ph type="sldNum">` |
| Bullet animation | `<p:bldP ... build="p"/>` |

### Step 4: Check Relationships (.rels files)
| Media Type | Relationship Type |
|------------|------------------|
| Video | `Type="...relationships/video"` — check `TargetMode="External"` means linked, not embedded |
| Audio | `Type="...relationships/audio"` |
| Images | `Type="...relationships/image"` |
| Slide hyperlinks | `Type="...relationships/slide"` with Target like `slide3.xml` |

### Step 5: List Files Using Glob
Use the Glob tool to list slides and media — do NOT use PowerShell with `$_` variable references as they fail due to escaping issues.

### Step 6: Cleanup
```bash
powershell -Command "Remove-Item -Path 'STUDENT_FOLDER/temp_extract' -Recurse -Force; Remove-Item -Path 'STUDENT_FOLDER/temp.zip' -Force"
```

## What to Assess

Grade against the rubric provided. If no rubric is given, use these general criteria and ask the user for marks allocation:

### Content and Structure
- Slide count meets requirements
- Logical flow and organisation of content
- Appropriate amount of text per slide (not cluttered)
- Spelling and grammar
- Topic coverage and accuracy

### Design and Layout
- Consistent theme/design applied
- Appropriate fonts and colours
- Professional appearance
- Slide backgrounds (global and individual where required)
- Footer with required information (name, date, slide numbers)

### Media and Elements
- Images present and relevant
- Video embedded (not just linked) where required
- Audio included where required
- Hyperlinks functional and pointing to correct targets

### Animations and Transitions
- Slide transitions applied
- Object animations present (images, text)
- Bullet-by-bullet animations where required
- Auto-advance timing where required

### Specific Slide Checks
When the rubric specifies requirements for particular slides (e.g., "slide 5 must be a duplicate of slide 4"), verify each one individually by reading the corresponding slide XML.

## Common Issues

1. **Linked vs embedded video** — Check `.rels` for `TargetMode="External"`. External means linked (often loses the video), not embedded.
2. **Missing media** — Media folder may be empty even if slides reference files.
3. **Duplicate slides** — Compare XML content of two slides to verify duplication.
4. **Fake footers** — Text boxes that look like footers vs actual footer placeholders (`<p:ph type="ftr">`).

## AI Indicators for Presentation Assignments

Watch for these in addition to the general indicators in the shared /grade skill:

- **Slide text reads like an essay** — AI-generated content pasted into slides often has full paragraphs instead of bullet points. Real students tend to use short phrases.
- **Overly polished speaker notes** — if the pptx has speaker notes that read like a script with perfect transitions, that's unusual. Students rarely write detailed speaker notes.
- **Generic stock content** — slides that define concepts with textbook-perfect definitions rather than the student's own understanding or class-specific framing.
- **Uniform bullet point style** — every slide has the same structure (3-4 bullets, same length, same sentence pattern). Real students vary their approach slide to slide.
- **Content depth mismatch** — the text on slides shows deep understanding but the actual PowerPoint skills (animations, formatting, media) are poorly done. Suggests the content was generated but the student built the slides themselves.
- **Identical slide text across students** — same definitions, same bullet points, same phrasing. Flag both students.

## Feedback Template for Presentation Assignments

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
**File Reviewed:** [filename.pptx]<br>
**Slide Count:** [X slides]

---

## Overall Score: X/[Total] (X%)

---

## [Section Name] (X/[Section Total])

| Criteria | Marks | Feedback |
|----------|-------|----------|
| [Criterion] | X/[Max] | [1-3 sentences — reference specific slides by number] |

[Repeat table for each rubric section]

## Slide-by-Slide Notes

| Slide | Content Found | Issues |
|-------|---------------|--------|
| 1 | [What's on the slide] | [Any problems] |
| 2 | ... | ... |

*(Include this table when the rubric has per-slide requirements)*

---

## Summary

| Section | Score |
|---------|-------|
| [Section 1] | X/[Max] |
| [Section 2] | X/[Max] |
| **Total** | **X/[Total] (X%)** |

### Strengths
- [What was done well]

### Areas for Improvement
- [What needs work]

---

*Feedback generated for assessment purposes.*
```
