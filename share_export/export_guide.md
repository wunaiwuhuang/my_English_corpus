# Lemma Export Utility

A tool to export lemma entries from SQLite databases for collaborative dictionary management.

## Purpose

Generate lemma lists to prevent duplicate work during team-based dictionary curation and track progress across different topics.

## Features

- **Simple mode**: Export lemma names only
- **Detailed mode**: Include topic, part-of-speech, and pronunciation data
- **Topic-separated mode**: Create individual files for each topic category
- **Database flexibility**: Export from any specified SQLite database
- **Customizable output**: Control filenames and export destinations

## Installation

No installation required. Ensure Python 3.x is installed with standard libraries (sqlite3, csv).

## Usage

### Basic Commands

```bash
# Simple export (default)
python export_lemmas.py

# Detailed export with metadata
python export_lemmas.py --mode detailed

# Export one file per topic
python export_lemmas.py --mode by-topic

# Export from specific database
python export_lemmas.py --db path/to/database.db

# Custom output filename
python export_lemmas.py --output custom_name.csv
```

### Batch Processing

For multiple databases:

```bash
# Linux/Mac
for db in *.db; do
    python export_lemmas.py --db "$db" --output "${db%.db}_lemmas.csv"
done

# Windows
for %f in (*.db) do python export_lemmas.py --db "%f" --output "%~nf_lemmas.csv"
```

### Windows Shortcut

Run `export_lemmas.bat` to launch interactive mode with menu options.

## Output Formats

- **Simple**: `lemma` column only
- **Detailed**: `lemma,topic,pos,pronunciation` columns with summary statistics
- **By Topic**: Individual CSV files organized by topic, plus `_no_topic.csv` for uncategorized items

All files are UTF-8 encoded CSVs compatible with spreadsheet applications.

## Configuration

Default export directory is `./share_export`. To change the save location, modify the `EXPORT_DIR = "share_export"` entry in `./share_export/export_lemmas.py`.
</details>