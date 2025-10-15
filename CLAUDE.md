# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python application that displays on-duty hospital schedules for Athens, Greece. It automatically scrapes official Greek Ministry of Health PDF files daily at 08:00 and displays hospitals grouped by medical specialty with time slots. Additionally, it includes a doctor shift management system for displaying cardiology department shifts.

## Core Architecture

### Multi-Module Design

1. **cardiology_display.py** - GUI application (Primary Interface)
   - Full-screen tkinter GUI for Emergency Department monitors
   - Hospital on-duty display by specialty
   - Doctor shift display section at bottom
   - Auto-refresh every 30 minutes
   - File management for monthly shift schedules
   - Real-time shift editing capability

2. **athens_hospitals.py** - CLI application (Legacy)
   - Command-line interface version
   - Scheduling system (uses `schedule` library)
   - Data caching to JSON
   - Search functionality
   - Runs continuously as a service

3. **moh_scraper.py** - Hospital data source module
   - Web scraping from https://www.moh.gov.gr
   - PDF parsing with `pdfplumber`
   - Hospital name normalization
   - Greek date formatting and matching
   - Independent, reusable module

4. **shift_parser.py** - Doctor shift management module
   - Parses monthly DOCX shift schedules
   - Extracts attending cardiologist shifts
   - Extracts resident shifts (major, minor, TEP)
   - Month/year validation
   - JSON caching for persistence
   - Shift editing support

### Data Flow

**Hospital On-Duty Data:**
```
Ministry of Health Website
  ↓ (scrapes daily files)
MOHHospitalScraper.get_today_schedule()
  ↓ (returns List[Hospital])
GUI: HospitalDisplayGUI.refresh_data()
  ↓ (filters by specialty)
Display in scrollable card layout
```

**Doctor Shift Data:**
```
Monthly DOCX File (User provided)
  ↓ (parses tables)
ShiftParser.parse()
  ↓ (extracts DailyShift objects)
Cache to shifts_cache.json
  ↓ (loads on startup)
GUI: update_shift_display()
  ↓ (shows today's shifts)
Display in bottom section
```

### Key Design Patterns

**Hospital Name Mapping**: `moh_scraper.py:36-61` contains `HOSPITAL_NAMES` dict that maps abbreviations (e.g., "ΕΥΑΓΓΕΛΙΣΜΟΣ") to full names. When adding new hospitals, update this mapping.

**Specialty Normalization**: `moh_scraper.py:64-93` contains `SPECIALTY_NAMES` dict for bilingual (Greek/English) specialty display. All specialties should be normalized through this mapping.

**Time Slot Parsing**: PDF tables have 5 time slot columns defined in `moh_scraper.py:188-194`. Changes to MOH PDF format require updating these column indices.

**Fallback Data**: If scraping fails, `athens_hospitals.py:126-203` provides sample data. This ensures the app always displays something useful.

**Shift Table Parsing**: `shift_parser.py` expects DOCX files with exactly 2 tables:
- Table 1 (Attending): [Day, Month, Weekday, Names] - Names can be multi-line with asterisks for readiness
- Table 2 (Residents): [Day, Month, Weekday, Major Shift, Minor Shift, TEP Cardiologist]

**Month Validation**: Before loading shifts, the system validates month/year against current date (`shift_parser.py:252-254`). Warning dialog allows user to proceed with mismatched files.

## Development Commands

### Setup
```bash
# Activate virtual environment (if venv exists in project)
source bin/activate

# Install dependencies
pip3 install -r requirements.txt
```

### Running

```bash
# Run GUI application (recommended for production)
python3 cardiology_display.py

# Run CLI application (legacy, service mode)
python3 athens_hospitals.py

# Test hospital scraper independently
python3 moh_scraper.py

# Test shift parser independently
python3 shift_parser.py [path_to_docx]
```

### Testing Modules

**Hospital Scraper** has a `__main__` block for standalone testing:
```bash
python3 moh_scraper.py
```
This will:
- List available files on MOH website
- Fetch today's schedule
- Display grouped results

**Shift Parser** has a `__main__` block for standalone testing:
```bash
python3 shift_parser.py
# Or specify a file:
python3 shift_parser.py "/path/to/ΕΦΗΜΕΡΙΕΣ ΟΚΤΩΒΡΙΟΣ 2025.docx"
```
This will:
- Parse the DOCX file
- Extract month and year
- Display today's shift (if available)
- Show first 5 days of shifts
- Generate shifts_cache.json

## Critical Implementation Details

### Greek Date Handling

**MOH Files** use Greek date format: "ΤΡΙΤΗ 14 ΟΚΤΩΒΡΙΟΥ 2025"

The `get_schedule_for_date()` method in `moh_scraper.py:277-316` converts Python dates to Greek format using the `greek_months` dict. **Always maintain this mapping** when working with dates.

**Shift Files** use Greek month names in genitive case: "ΟΚΤΩΒΡΙΟΥ", "ΝΟΕΜΒΡΙΟΥ", etc.

The `ShiftParser` class in `shift_parser.py:31-44` contains `GREEK_MONTHS` dict mapping both nominative and genitive forms to month numbers. This is used to extract month/year from DOCX paragraphs.

### PDF Table Structure

MOH PDF files contain structured tables with:
- **Row 0**: Headers (including "Κλινικές" and time slot labels)
- **Subsequent rows**: Specialty name in column 0, hospitals in columns 1-5

Parser logic in `moh_scraper.py:148-218`:
1. Finds header row containing "Κλινικές"
2. Iterates subsequent rows
3. Extracts specialty from column 0
4. Parses hospitals from time slot columns 1-5

**Important**: If MOH changes PDF format, update the header detection and column mapping logic.

### File Download System

Files are identified by `fdl` parameter: `?fdl=12345`

`get_available_files()` method scans MOH page for links containing `fdl=` and date strings (2024, 2025). When supporting new years, update the year filter in `moh_scraper.py:118`.

### DOCX Table Structure

Shift schedule DOCX files must contain exactly **2 tables**:

**Table 1: Attending Cardiologists** (`shift_parser.py:113-138`)
- Column 0: Day number (01-31)
- Column 1: Month name (genitive case)
- Column 2: Weekday
- Column 3: Doctor names (multi-line, asterisks stripped)

**Table 2: Residents** (`shift_parser.py:140-173`)
- Row 0: Headers (skipped)
- Column 0: Day number
- Column 1: Month name
- Column 2: Weekday
- Column 3: Major shift (24-hour)
- Column 4: Minor shift (24-hour)
- Column 5: TEP cardiologist (12-hour)

**Important**: If DOCX table structure changes, update parsing logic in `shift_parser.py` methods `_parse_attending_table()` and `_parse_resident_table()`.

### Character Encoding

All files use UTF-8 encoding with Greek characters. Always:
- Open files with `encoding='utf-8'`
- Use `ensure_ascii=False` in `json.dump()`
- Keep Greek text in source code (it's intentional, not a bug)

## Data Structures

### Hospital Object (moh_scraper.py)
```python
@dataclass
class Hospital:
    name: str              # Full hospital name
    specialty: str         # Bilingual format: "Καρδιολογία / Cardiology"
    time_slot: str        # e.g., "08:00-14:30", "14:30-08:00 επομένης"
    on_duty_date: str     # ISO format: "2025-10-14"
    address: str = ""     # Optional
    phone: str = ""       # Optional
    area: str = ""        # Optional
```

### Hospital Object (athens_hospitals.py)
Identical structure, converted from MOH Hospital objects in `fetch_hospital_data()` method.

### DailyShift Object (shift_parser.py)
```python
@dataclass
class DailyShift:
    day: int                           # Day of month (1-31)
    month_name: str                    # Greek month name (genitive)
    weekday: str                       # Greek weekday name
    attendings: List[str]              # List of attending cardiologists
    major_shift: Optional[str] = None  # Major 24h shift resident
    minor_shift: Optional[str] = None  # Minor 24h shift resident
    tep_cardiologist: Optional[str] = None  # TEP 12h cardiologist
```

## Scheduling Behavior

### CLI Application (athens_hospitals.py)

Schedules three tasks daily at 08:00:
1. `update_data()` - Fetch new data
2. `display_hospitals()` - Show updated display
3. `save_to_json()` - Export to file

**To change schedule time**: Edit `main()` function in `athens_hospitals.py:298-301`.

The schedule runs in an infinite loop checking every 60 seconds.

### GUI Application (cardiology_display.py)

Auto-refreshes every 30 minutes (1800000 ms):
1. `refresh_data()` - Fetch hospital data from MOH
2. `update_shift_display()` - Update today's doctor shifts
3. Display updates automatically

**To change refresh interval**: Edit `self.auto_refresh_interval` in `cardiology_display.py:65`.

The GUI updates both hospital data and shift information during each refresh cycle.

## Output Files

**hospitals_on_duty.json** - Hospital data cache:
```json
{
  "last_update": "2025-10-14T20:57:46.123456",
  "hospitals": [
    {
      "name": "...",
      "specialty": "...",
      "time_slot": "...",
      // ...
    }
  ]
}
```

**shifts_cache.json** - Doctor shift data cache:
```json
{
  "month": 10,
  "year": 2025,
  "last_update": "2025-10-14T20:57:46.123456",
  "shifts": {
    "1": {
      "day": 1,
      "month_name": "ΟΚΤΩΒΡΙΟΥ",
      "weekday": "Τετάρτη",
      "attendings": ["Name1", "Name2"],
      "major_shift": "ResidentName",
      "minor_shift": "ResidentName",
      "tep_cardiologist": "CardioName"
    }
  }
}
```

Both files are git-ignored and regenerated as needed.

## External Dependencies

### Critical Libraries
- **tkinter**: GUI framework (built-in with Python)
- **pdfplumber**: PDF table extraction (core functionality)
- **python-docx**: DOCX parsing for shift schedules
- **beautifulsoup4 + lxml**: HTML parsing for file discovery
- **schedule**: Task scheduling (CLI app)
- **requests**: HTTP requests

### Legacy Support
- **olefile**: Old DOC format support (limited functionality)
- **pypdf2**: PDF utilities (backup)

## Extending the Application

### Adding New Hospitals
1. Update `HOSPITAL_NAMES` dict in `moh_scraper.py:36-61`
2. Add abbreviation → full name mapping
3. Test with actual MOH PDF to verify abbreviation format

### Adding New Specialties
1. Update `SPECIALTY_NAMES` dict in `moh_scraper.py:64-93`
2. Add bilingual mapping
3. Ensure Greek specialty name matches MOH PDF format exactly

### Supporting New Cities
Create new scraper class inheriting base logic:
- Keep MOH file discovery logic
- Adjust URL to city-specific MOH page
- Update hospital name mappings for that city

### Adding Hospital Metadata (Phone, Address)
MOH PDFs don't include contact info. Options:
1. Maintain separate mapping dict in `moh_scraper.py`
2. Create JSON config file with hospital metadata
3. Fetch from secondary source and merge data

### Adding New Shift Types
To add new shift categories (e.g., "Night Shift"):

1. Update `DailyShift` dataclass in `shift_parser.py:20-40`
2. Add new column parsing in `_parse_resident_table()` method
3. Update `update_shift_display()` in `cardiology_display.py:635-762` to show new field
4. Add field to edit dialog in `edit_shifts()` method

### Supporting Multiple Departments
To extend shift system beyond cardiology:

1. Create new shift parser subclass or parameterize existing one
2. Add department selector to GUI
3. Maintain separate cache files per department
4. Update file naming convention to include department

## Common Issues

### "No file found for date"
- MOH publishes files at 08:00 but may have delays
- File naming might have changed (check actual links)
- Weekend/holiday schedules may not be published

### PDF Parsing Returns Empty
- Check if MOH changed PDF table structure
- Verify header detection logic finds "Κλινικές"
- Inspect raw table extraction with debug print

### Hospital Names Not Normalized
- Check if abbreviation exists in `HOSPITAL_NAMES` dict
- MOH may introduce new abbreviations - add them to mapping
- Verify text extraction isn't adding/removing characters

### Encoding Issues
- Always use UTF-8 encoding
- Check terminal locale supports Greek characters
- JSON export requires `ensure_ascii=False`

### Shifts Not Displaying
- Verify `shifts_cache.json` exists and is valid
- Check month/year in cache matches current date
- Click "Φόρτωση Αρχείου" to reload DOCX file
- Verify DOCX file has exactly 2 tables with correct structure

### DOCX Parsing Fails
- Verify file has exactly 2 tables (check with `len(doc.tables)`)
- Ensure month name appears in document paragraphs
- Check table structure matches expected format
- Verify Greek text encoding is UTF-8

### Edited Shifts Don't Persist
- Check write permissions for `shifts_cache.json`
- Verify application has write access to working directory
- Check console for error messages during save
- Ensure `save_to_json()` is called after edits

### GUI Doesn't Display
- Verify tkinter is installed (built-in with most Python installations)
- Check if DISPLAY environment variable is set (Linux)
- Try running from terminal to see error messages
- Test with `python3 -m tkinter` to verify tkinter works

## Python Environment

This project uses a virtual environment located in the project directory:
- **bin/**, **lib/**, **include/** - Virtual environment files
- **pyvenv.cfg** - Virtual environment configuration

Always activate before running:
```bash
source bin/activate
```

## Additional Documentation

For comprehensive information about the shift management system:
- **SHIFT_FEATURES.md** - Complete guide to doctor shift features
  - Usage instructions
  - File format requirements
  - Troubleshooting guide
  - Future enhancement ideas
