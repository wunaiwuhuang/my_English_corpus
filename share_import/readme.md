# Database Integration Tool

## Functionality Overview

This tool is designed to merge multiple `dictionary.db` files that have been independently created by different contributors.

### Integrated Content
- **Lemmas** – Entries (automatically deduplicated; conflicts are skipped)
- **Examples** – Example sentences (automatically deduplicated; intelligently merged)

### Excluded Content
- **Relations** – Semantic relations (excluded to avoid conflicts; manual handling required)

---

## Quick Start Guide

### Step 1: Prepare Database Files

Place all `.db` files to be merged into the `input_db/` directory:

```
share_import/
├── input_db/
│   ├── dictionary_zhangsan.db
│   ├── dictionary_lisi.db
│   └── dictionary_wangwu.db
├── integrate_databases.py
└── integrate.bat
```

### Step 2: Run Integration

**Windows:**
```bash
# Double-click to run
integrate.bat

# Or run from command line
cd share_import
python integrate_databases.py
```

**Mac/Linux:**
```bash
cd share_import
python integrate_databases.py
```

### Step 3: Review Output

The merged database is saved in the `output_db/` directory:

```
share_import/
└── output_db/
    ├── integrated.db                      ← Merged result
    ├── integrated_backup_*.db             ← Automatic backups
    └── conflict_report_*.txt              ← Conflict report
```

### Step 4: Apply to Main Database

```bash
# After verification, replace the main database
copy share_import\output_db\integrated.db data\dictionary.db
```

---

## Integration Rules

### Lemmas

| Scenario | Action |
|--------|--------|
| Distinct lemmas | All added |
| Duplicate lemma | Skipped; first occurrence retained |
| Conflicting entries | Logged in conflict report |

**Example:**
```
Zhangsan's DB: break_down (first occurrence → kept)
Lisi's DB:    break_down (duplicate → skipped)
Wangwu's DB:  give_up    (new → added)
```

### Examples

| Scenario | Action |
|--------|--------|
| Distinct example sentences | All added |
| Identical sentence content | Merged under shared ID |
| Lemma validation | Automatically verified |

**Example:**
```
Zhangsan: "My car broke down."  (added as new)
Lisi:     "My car broke down."  (merged with Zhangsan’s example)
Wangwu:   "The machine broke down." (new → added)
```

### Relations

**Not integrated at all.**

Reasons:
- Relations involve complex semantic links
- Contributors may define different relationships
- Automatic resolution is error-prone

Recommendation:
- Add relations manually after integration
- Or assign one person to manage all relations

---

## Sample Integration Report

```
======================================================================
  Integration Report
======================================================================

Data Sources: 3 database files

Lemmas:
  Added: 145
  Skipped (conflicts): 5
  
  Conflicting lemmas (top 10):
     - break_down
     - give_up
     - take_off

Examples:
  Added: 180
  Merged into existing: 20
  New links created: 200

Relations:
  Skipped (by design): 15

Final Totals:
  Lemmas: 145
  Examples: 200
```

---

## Conflict Report

If lemma conflicts occur, a detailed report is generated:

**conflict_report_20241124_153020.txt**

```
======================================================================
  Conflict Report
======================================================================

Generated: 2024-11-24 15:30:20
Total Conflicts: 5

Details:
----------------------------------------------------------------------

1. Lemma: break_down
   Source: dictionary_lisi.db
   Reason: Lemma already exists

2. Lemma: give_up
   Source: dictionary_wangwu.db
   Reason: Lemma already exists

...
```

### Resolving Conflicts

**Option 1: Prevent conflicts in advance**
```bash
# Before task assignment
cd ..
python export_lemmas.py --mode simple

# Share the list to avoid duplicate entries
```

**Option 2: Manual resolution**
```bash
# 1. Open integrated.db with DB Browser for SQLite
# 2. Query conflicting lemma:
SELECT * FROM lemmas WHERE lemma = 'break_down';

# 3. Open source DB (e.g., input_db/dictionary_lisi.db)
# 4. Compare and decide which version to keep or merge
# 5. Edit integrated.db manually if needed
```

---

## Advanced Usage

### Batch Integration

```bash
# First batch (Zhangsan + Lisi)
# Place their .db files in input_db/
python integrate_databases.py

# Rename result
move output_db\integrated.db output_db\batch1.db

# Clear input_db, then second batch (Wangwu + Zhao)
python integrate_databases.py

# Final merge: combine batch1.db and latest integrated.db
python integrate_databases.py
```

### Selective Integration

```bash
# Only place desired .db files in input_db/
# Others can be temporarily moved elsewhere
```

### Incremental Updates

```bash
# Initial integration
python integrate_databases.py
copy output_db\integrated.db ..\data\dictionary.db

# Later, receive new contributions
# Copy current main DB into input_db/
copy ..\data\dictionary.db input_db\main.db

# Add new contributor DB
copy dictionary_new.db input_db\

# Re-run integration
python integrate_databases.py
```

---

## Full Workflow

### Project Kickoff

```bash
# 1. Export initial lemma list
cd ..
python export_lemmas.py --mode by-topic

# 2. Assign topics
Zhangsan: phrasal_verbs
Lisi:     academic_terms
Wangwu:   daily_expressions

# 3. Distribute project folder
```

### Data Entry Phase (1–2 weeks)

```bash
# Contributors work independently
streamlit run app.py

# Periodic sync via export
python export_lemmas.py
```

### Collection Phase

```bash
# Gather all databases:
dictionary_zhangsan.db
dictionary_lisi.db
dictionary_wangwu.db

# Place in share_import/input_db/
```

### Integration Phase

```bash
# 1. Run integration
cd share_import
integrate.bat

# 2. Review reports
- Check statistics
- Inspect conflict_report_*.txt

# 3. Deploy to main DB
copy output_db\integrated.db ..\data\dictionary.db
```

### Validation Phase

```bash
# 1. Launch main app
cd ..
streamlit run app.py

# 2. Verify in Browse interface:
- Total lemma count
- Spot-check entry content
- Confirm example associations

# 3. Export master list
python export_lemmas.py --mode detailed

# 4. Distribute for next cycle
```

---

## Important Notes

### 1. Relations Are Not Merged

**Why?**
- Semantic relations are subjective
- Multiple definitions may conflict
- Auto-merge risks logical inconsistency

**Solutions:**
- Designate a relations manager
- Add relations post-integration
- Maintain a separate relations database

### 2. Always Back Up

```bash
# Backup before integration
copy ..\data\dictionary.db ..\data\dictionary_before_integrate.db

# Also backup input folder
xcopy input_db input_db_backup\ /E /I
```

### 3. Validate Data Quality

Pre-integration check:
```bash
# Export detailed lists per contributor
python ..\export_lemmas.py --db input_db\dictionary_zhangsan.db --mode detailed --output zhangsan_details.csv

# Review in Excel or similar
```

---

## Directory Structure

```
english_dictionary/
├── share_import/                    ← Integration toolkit
│   ├── input_db/                   ← Input: .db files to merge
│   │   ├── dictionary_zhangsan.db
│   │   ├── dictionary_lisi.db
│   │   └── dictionary_wangwu.db
│   ├── output_db/                  ← Output: results
│   │   ├── integrated.db           ← Merged database
│   │   └── conflict_report_*.txt   ← Conflict logs
│   ├── integrate_databases.py      ← Core script
│   ├── integrate.bat               ← Windows shortcut
│   └── README.md                   ← This document
├── data/
│   └── dictionary.db               ← Main database
└── ...
```

---

## Frequently Asked Questions

### Q: Why aren’t Relations integrated?
**A:** Relations involve subjective semantic links that vary between contributors. Automatic merging often creates inconsistencies. We recommend post-integration curation.

### Q: How do I handle lemma conflicts?
**A:**  
1. Use `export_lemmas.py` beforehand to distribute entry lists  
2. Review the generated `conflict_report_*.txt`  
3. Resolve manually using a SQLite browser

### Q: Can I run integration multiple times?
**A:** Yes. Each run produces a new `integrated.db`, and previous versions are backed up as `integrated_backup_*.db`. Clean old backups periodically.

### Q: In what order are files processed?
**A:** Alphabetically by filename. To control order, prefix filenames:
```
01_dictionary_main.db
02_dictionary_zhangsan.db
03_dictionary_lisi.db
```

### Q: Are example-to-lemma links validated?
**A:** Yes. If a linked lemma doesn’t exist, the example’s `is_valid` flag is set to `0` (displayed in gray).

---

## Technical Support

Troubleshooting steps:
1. Ensure Python ≥ 3.8
2. Verify all `.db` files are valid SQLite databases
3. Check console error logs
4. Inspect `conflict_report_*.txt`

---

Happy Integrating!
```