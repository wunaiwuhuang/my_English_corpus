# English Dictionary Warehouse

A comprehensive English dictionary management system for building personal vocabulary corpus. Built with Streamlit and SQLite, featuring a clean interface and intuitive operations.

Version: 1.0.0
Python: 3.8+
License: MIT

## Features

### Core Functions

- Lemma Management: Add, edit, and delete word entries with support for multiple parts of speech and definitions
- Example Management: Add example sentences with intelligent lemma association
- Relation Management: Build semantic relationship networks between words
- Smart Search: Quick search by alphabet, topic, or keywords

### Advanced Features

- Automatic lemma formatting (spaces to underscores, lowercase conversion)
- Intelligent example-lemma association (automatic validation, grayed display for non-existent lemmas)
- Auto-refresh example validity when adding new lemmas
- Strict lemma existence validation for relations (prevents dirty data)
- Relationship network visualization (supports multi-depth exploration)
- Ultra-compact list display (one-line view, expand on demand)
- Inline editing for all fields (including POS and meanings)
- Custom CSS styling (adjustable line height and spacing)

## Quick Start

### Requirements

- Python >= 3.8
- streamlit >= 1.28.0

### Installation

#### 1. Create Environment

```bash
conda create -n dictionary python=3.8
conda activate dictionary
```

#### 2. Clone Repository

```bash
git clone https://github.com/wunaiwuhuang/my_English_corpus
cd my_English_corpus
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Run Application

```bash
streamlit run app.py
```

The application will automatically open in your browser at `http://localhost:8501`

## User Guide

### Adding Lemmas

1. Click "Add Lemma" in the sidebar
2. Fill in basic information:
   - Lemma: Word entry (spaces automatically converted to underscores)
   - Pronunciation: British pronunciation (optional)
   - Spell Nuance: Spelling differences (optional, British left, American right)
   - Collocation: Word combinations (optional)
   - Topic: Category classification (optional)
3. Configure parts of speech and meanings:
   - Select part of speech (n., v., adj., etc.)
   - Enter one meaning per line
   - Can add multiple parts of speech
4. Optional fields:
   - Inflection: Irregular forms (format: `verb: past, past_participle | noun: plural`)
   - Derivation: Derived words (format: `word:meaning`, one per line)
5. Click "Save" to save

Example:

```
Lemma: break down
Pronunciation: breɪk daʊn
Topic: phrasal_verbs

POS 1: v.
Meanings:
- (of a machine) stop working
- lose control of emotions
- analyze into components

Inflection: verb: broke down, broken down
Derivation: breakdown: noun form
```

### Adding Examples

1. Click "Add Example" in the sidebar
2. Enter example sentence
3. Enter associated lemmas (comma-separated)
4. System automatically validates:
   - Green: lemma exists
   - Gray: lemma does not exist (will auto-link when lemma is added later)
5. Click "Save" to save

Example:

```
Example: My car broke down on the highway yesterday.
Lemmas: break_down, car, highway
```

### Adding Relations

1. Click "Add Relation" in the sidebar
2. Enter first word:
   - Lemma 1: Word entry (must exist)
   - Specific Word 1: Specific usage (single word)
3. Enter second word:
   - Lemma 2: Word entry (must exist)
   - Specific Word 2: Specific usage (single word)
4. Select relationship type:
   - Interchangeable: Interchangeable
   - Contextual Synonym: Contextual synonym
5. Add notes (optional)
6. Click "Save" to save

Example:

```
Lemma 1: provide        Specific Word 1: provide
Lemma 2: postulate      Specific Word 2: postulate
Type: contextual_synonym
Note: 'provide' in law, 'postulate' in academic
```

### Browsing Dictionary

1. Click "Browse" in the sidebar
2. Use search and filters:
   - Search box: Enter keywords
   - Topic filter: Select specific topics
   - Sort by: Alphabetical / Recently added / Topic
3. Entry operations (one-line display):
   - View: Expand to see details
   - Edit: Edit entry (all fields editable)
   - Delete: Delete entry
   - Network: View relationship network (if relations exist)
4. When expanded, view:
   - Complete parts of speech and meanings
   - Inflection, derivation, collocation
   - Associated examples
   - Related relations

## Database Structure

### lemmas Table

| Field                 | Type      | Description                               |
| --------------------- | --------- | ----------------------------------------- |
| id                    | TEXT      | UUID primary key                          |
| lemma                 | TEXT      | Unique word entry (spaces to underscores) |
| pronunciation_british | TEXT      | British pronunciation                     |
| spell_nuance          | TEXT      | Spelling differences                      |
| pos_meaning           | TEXT      | JSON format for POS and meanings          |
| inflection            | TEXT      | JSON format for inflections               |
| derivation            | TEXT      | JSON format for derivations               |
| collocation           | TEXT      | Word combinations                         |
| topic                 | TEXT      | Topic classification                      |
| created_at            | TIMESTAMP | Creation time                             |
| updated_at            | TIMESTAMP | Update time                               |

### examples Table

| Field      | Type      | Description      |
| ---------- | --------- | ---------------- |
| id         | TEXT      | UUID primary key |
| example    | TEXT      | Example sentence |
| created_at | TIMESTAMP | Creation time    |

### example_lemma_links Table

| Field      | Type    | Description                           |
| ---------- | ------- | ------------------------------------- |
| example_id | TEXT    | Example ID (foreign key)              |
| lemma      | TEXT    | Lemma (foreign key)                   |
| is_valid   | INTEGER | Validity (1=exists, 0=does not exist) |

### relations Table

| Field          | Type      | Description                |
| -------------- | --------- | -------------------------- |
| id             | INTEGER   | Auto-increment primary key |
| lemma1         | TEXT      | First lemma (foreign key)  |
| specific_word1 | TEXT      | First specific word        |
| lemma2         | TEXT      | Second lemma (foreign key) |
| specific_word2 | TEXT      | Second specific word       |
| relation_type  | TEXT      | Relationship type          |
| note           | TEXT      | Notes                      |
| created_at     | TIMESTAMP | Creation time              |

## Data Backup

### Automated Backup Scripts

Windows users:

```bash
# Double-click to run
backup.bat

# Or run from command line
.\backup.bat
```

Mac/Linux users:

```bash
# Add execution permission (first time only)
chmod +x backup.sh

# Run backup
./backup.sh
```

Backup files will be saved in the `backups/` directory with naming format:

```
dictionary_backup_20241124_153020.db
```

### Manual Backup

Method 1: Direct file copy

```bash
# Windows
copy data\dictionary.db backups\dictionary_backup.db

# Mac/Linux
cp data/dictionary.db backups/dictionary_backup.db
```

Method 2: SQLite export

```bash
sqlite3 data/dictionary.db .dump > backup.sql
```

### Data Recovery

```bash
# Method 1: Replace file
copy backups\dictionary_backup_20241124.db data\dictionary.db

# Method 2: Import from SQL
sqlite3 data/dictionary.db < backup.sql
```
## Export Functionality

New feature: Export lemma lists for team collaboration and progress tracking.

### Features

- **Simple mode**: Export lemma names only
- **Detailed mode**: Include topic, part-of-speech, and pronunciation data
- **Topic-separated mode**: Create individual files for each topic category
- **Database flexibility**: Export from any specified SQLite database
- **Customizable output**: Control filenames and export destinations

### Usage

```bash
# Simple export (default, saves to ./share_export)
python share_export/export_lemmas.py

# Detailed export with metadata
python share_export/export_lemmas.py --mode detailed

# Export one file per topic
python share_export/export_lemmas.py --mode by-topic

# Export from specific database
python share_export/export_lemmas.py --db path/to/database.db
```

Default export directory is `./share_export`. To change the save location, modify the `EXPORT_DIR = "share_export"` entry in `./share_export/export_lemmas.py`.

## Technology Stack

- Frontend Framework: Streamlit 1.28+
- Database: SQLite3
- Backend Language: Python 3.8+
- Data Format: JSON (flexible field storage)
- Architecture Pattern: MVC layered architecture

## Project Structure

```
english_dictionary/
├── app.py                      # Main application entry (routing)
├── config.py                   # Global configuration
├── requirements.txt            # Python dependencies
├── backup.bat / backup.sh      # Backup scripts
├── README.md                   # Project documentation
│
├── database/                   # Database layer
│   ├── __init__.py
│   ├── schema.sql              # Table structure definition
│   ├── db_manager.py           # Database operation wrapper
│   └── models.py               # Data models
│
├── services/                   # Business logic layer
│   ├── __init__.py
│   ├── lemma_service.py        # Lemma business logic
│   ├── example_service.py      # Example business logic
│   └── relation_service.py     # Relation business logic
│
├── ui/                         # User interface layer
│   ├── __init__.py
│   ├── browser.py              # Browser interface
│   ├── add_lemma.py            # Add Lemma interface
│   ├── add_example.py          # Add Example interface
│   ├── add_relation.py         # Add Relation interface
│   └── components/             # UI components
│       └── __init__.py
│
├── utils/                      # Utility functions
│   ├── __init__.py
│   ├── validators.py           # Data validation
│   └── helpers.py              # Helper functions
│
├── data/                       # Data directory
│   └── dictionary.db           # SQLite database (auto-generated)
│
├── share_export/               # Export functionality
│   ├── export_guide.md         # Export readme
│   ├── export_lemmas.py        # Export script
│   └── export_lemmas.bat       # Windows batch file
│
└── backups/                    # Backup directory (auto-created)
    └── dictionary_backup_*.db  # Backup files
```

## Viewing Data

### Using DB Browser (Recommended)

1. Download [DB Browser for SQLite](https://sqlitebrowser.org/)
2. Open `data/dictionary.db`
3. Graphically view and edit all tables

### Using Command Line

```bash
sqlite3 data/dictionary.db

# View all tables
.tables

# View lemmas
SELECT lemma, pronunciation_british, topic FROM lemmas;

# Exit
.quit
```

## FAQ

### Q: How to migrate to another computer?

A: Simply copy the entire project folder, especially the `data/dictionary.db` file.

### Q: Where is data stored?

A: All data is stored in a single SQLite file: `data/dictionary.db`.

### Q: How to clean up old backups?

A: Manually delete old files in the `backups/` directory. Recommended to keep the most recent 10 backups.

### Q: Can I run multiple instances simultaneously?

A: Not recommended. SQLite does not support high concurrent writes, which may lead to data conflicts.

### Q: How to reset all data?

A: Delete the `data/dictionary.db` file. Running the application again will automatically create an empty database.

## Contributing

Issues and Pull Requests are welcome!

If this project helps you, please give it a Star for support!

---

Built with Streamlit and SQLite
