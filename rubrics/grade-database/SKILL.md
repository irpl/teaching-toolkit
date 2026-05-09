---
name: grade-database
description: >
  Grades student database assignments — Microsoft Access (.accdb), SQL scripts, or
  verbal descriptions of database work. Triggers on 'grade database', 'mark database',
  'grade Access', 'mark SQL', 'check database submission', or 'grade db assignment'.
argument-hint: "[rubric description or assignment details]"
---

# Database Assignment Grading

Grades database assignments (Access, SQL Server, MySQL, etc.). Follows the shared /grade workflow for feedback and tracking.

## Submission Types

Database assignments may come as:
- **SQL scripts** (.sql files) — read directly
- **Database backups** (.bak, .7z) — note their presence, may need user to describe contents
- **Access files** (.accdb) — cannot be read directly as text; user may describe verbally
- **Verbal descriptions** — user describes the student's tables, queries, forms, and reports

When the submission is verbal, ask clarifying questions if details are unclear about:
- Table names, fields, data types, and relationships
- Query names and what they do
- Form design elements
- Report structure (grouping, sorting, summaries)

## Reading SQL Scripts

For .sql files, read them directly and assess:
- Table creation statements (CREATE TABLE)
- Data types and constraints
- Primary and foreign key definitions
- Stored procedures
- Queries (SELECT, INSERT, UPDATE, DELETE)

## What to Assess

Grade against the rubric provided. If no rubric is given, use these general criteria and ask the user for marks allocation:

### Table Design
- Appropriate tables created for the domain
- Correct field names and data types
- Appropriate use of numeric, text, date, and boolean fields
- Each table has a suitable primary key
- Minimum record count met (typically 4+ records per table)

### Relationships
- Foreign keys properly defined
- Relationships between tables are logical and correct
- Referential integrity enforced where appropriate

### Queries
- Required query types present (SELECT, UPDATE, DELETE, etc.)
- Queries named correctly (if specific names required by rubric)
- Multiple table joins where required
- Sorting implemented correctly
- Filtering criteria correct (WHERE, AND, OR)
- Date fields used in criteria where required
- Wildcards used appropriately (LIKE with % or *)
- Queries produce correct/expected results

### Forms
- Form exists and is functional
- Appropriate layout and design
- Connected to correct data source
- Usable for data entry

### Reports
- Report generated with correct fields
- Data grouped appropriately
- Data sorted as required
- Summary calculations present (SUM, AVG, COUNT, etc.)
- Professional appearance (logo/image if required)

### Data Validation
- Validation rules applied to appropriate fields
- Meaningful error messages for validation failures
- Input masks where appropriate

## Common Issues

1. **Missing relationships** — Tables exist but no foreign keys defined between them.
2. **Wrong data types** — Using text for numbers, or short text for fields that need memo/long text.
3. **No validation rules** — Fields accept any input with no constraints.
4. **Manually typed query results** — Results pasted rather than actual query definitions.
5. **Generic field names** — "Field1", "Field2" instead of meaningful names.
6. **Missing queries** — Not all required query types present, or queries named incorrectly.

## AI Indicators for Database Assignments

Watch for these in addition to the general indicators in the shared /grade skill:

- **Perfect SQL syntax with advanced features** — CTEs, window functions, subqueries, or optimisation hints that haven't been covered in the course.
- **Overly normalised design** — a database schema that's textbook-perfect 3NF when the assignment only requires basic table relationships. Students at this level usually under-normalise, not over-normalise.
- **Generic sample data** — AI-generated data often uses names like "John Smith," "Jane Doe," "Product A," "Product B." Students more often use local or personal references (Jamaican names, local businesses, etc.).
- **Identical table structures across students** — same field names, same data types, same sample data. Flag both students.
- **SQL comments explaining every line** — similar to code, AI over-comments SQL. Students rarely comment their queries at this level.
- **Consistent formatting in SQL** — perfect indentation, consistent capitalisation of keywords (SELECT, FROM, WHERE all uppercase), consistent alias conventions. Students usually mix styles.
- **Stored procedures with robust error handling** — TRY/CATCH, transactions, and parameter validation beyond what was taught.

## Feedback Template for Database Assignments

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
**Assessment:** [Assessment Name]

---

## Overall Score: X/[Total] (X%)

---

## [Section Name] (X/[Section Total])

| Criteria | Marks | Feedback |
|----------|-------|----------|
| [Criterion] | X/[Max] | [1-3 sentences — reference specific tables, queries, or fields] |

[Repeat table for each rubric section]

## Database Structure Overview

| Table | Fields | Primary Key | Records |
|-------|--------|-------------|---------|
| [Table name] | [List key fields] | [PK field] | [count] |

## Query Summary

| Query Name | Type | Criteria Used | Working? |
|------------|------|---------------|----------|
| [Name] | [SELECT/UPDATE/DELETE] | [What conditions] | Yes/No/Partial |

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
