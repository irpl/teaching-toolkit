---
name: grade-spreadsheet
description: >
  Grades student spreadsheet submissions (.xlsx, .xls) including formulas, formatting,
  charts, and data analysis. Triggers on 'grade spreadsheet', 'mark Excel',
  'grade workbook', 'check spreadsheet submission', or 'mark Excel assignment'.
argument-hint: "[rubric description or assignment details]"
---

# Spreadsheet Assignment Grading

Grades Excel and spreadsheet assignments. Follows the shared /grade workflow for feedback and tracking.

## Extracting Content from .xlsx Files

.xlsx files are ZIP archives containing XML. Use Python to extract:

```python
import zipfile
import xml.etree.ElementTree as ET

z = zipfile.ZipFile(r'path\to\file.xlsx')

# List all files in the archive
print(z.namelist())

# Key files:
# xl/workbook.xml        - Sheet names and structure
# xl/worksheets/sheet1.xml - Cell data for sheet 1
# xl/sharedStrings.xml   - Text values referenced by cells
# xl/styles.xml          - Formatting information
# xl/charts/             - Chart definitions

# Read shared strings (text values)
ss = z.read('xl/sharedStrings.xml')
ss_root = ET.fromstring(ss)
ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
strings = [t.text for t in ss_root.findall('.//s:t', ns) if t.text]

# Read a worksheet
sheet = z.read('xl/worksheets/sheet1.xml')
sheet_root = ET.fromstring(sheet)

# Find cells with formulas
for row in sheet_root.findall('.//s:row', ns):
    for cell in row.findall('s:c', ns):
        ref = cell.get('r')  # Cell reference like A1, B2
        formula = cell.find('s:f', ns)
        value = cell.find('s:v', ns)
        if formula is not None:
            print(f"{ref}: formula={formula.text}, value={value.text if value is not None else 'N/A'}")
```

## What to Assess

Grade against the rubric provided. If no rubric is given, use these general criteria and ask the user for marks allocation:

### Data Entry and Structure
- Data organised in appropriate rows and columns
- Correct use of data types (numbers, dates, text)
- Appropriate column headers and labels
- Data is clean and consistent

### Formulas and Functions
- Required formulas are present and correct (SUM, AVERAGE, MIN, MAX, COUNT, IF, VLOOKUP, etc.)
- Formulas reference cells dynamically — not hardcoded values
- Formulas produce correct results
- Appropriate use of absolute vs relative references

### Formatting
- Number formatting (currency, percentages, decimal places)
- Cell alignment and text wrapping
- Column widths appropriate for content
- Borders, shading, and visual organisation
- Conditional formatting if required

### Charts and Visualisation
- Appropriate chart type for the data
- Chart has title, axis labels, legend
- Data range is correct
- Chart is clear and readable

### Advanced Features (if required)
- Data validation (dropdown lists, input restrictions)
- Pivot tables
- Named ranges
- Sorting and filtering
- Macros or VBA

## Key Checks

1. **Real formulas vs typed values** — Always check XML for `<f>` (formula) elements. Students sometimes type the answer instead of writing a formula.
2. **Correct cell references** — Formulas should reference the right cells, not hardcoded numbers.
3. **Formula results** — Even if the formula is present, verify it produces the correct output.
4. **Sheet structure** — Check if multiple sheets are required and present.

## AI Indicators for Spreadsheet Assignments

Watch for these in addition to the general indicators in the shared /grade skill:

- **Perfect formulas with no iteration errors** — students usually get a formula wrong on the first try, fix it, and sometimes leave remnants. A sheet where every formula is correct on every cell is unusual for beginners.
- **Overly sophisticated formulas** — nested IF statements, INDEX/MATCH, or array formulas that haven't been taught in the course.
- **Suspiciously clean data** — perfectly formatted, no typos in data entries, consistent decimal places throughout. Real students make data entry mistakes.
- **Identical spreadsheet structure across students** — same column widths, same colour schemes, same data layout. Flag both students.
- **AI can't directly create .xlsx files** — but students may have asked AI for the formulas and typed them in. Watch for formulas that are correct but the student clearly doesn't understand the structure (e.g., correct VLOOKUP but wrong understanding shown elsewhere).

## Feedback Template for Spreadsheet Assignments

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
**File Reviewed:** [filename.xlsx]

---

## Overall Score: X/[Total] (X%)

---

## [Section Name] (X/[Section Total])

| Criteria | Marks | Feedback |
|----------|-------|----------|
| [Criterion] | X/[Max] | [1-3 sentences — reference specific cells, formulas, or sheets] |

[Repeat table for each rubric section]

## Formula Verification

| Location | Expected | Found | Correct? |
|----------|----------|-------|----------|
| [Cell ref] | [e.g., =SUM(B2:B6)] | [What was actually there] | Yes/No |

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
