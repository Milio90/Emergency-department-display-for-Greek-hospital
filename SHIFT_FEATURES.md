# Doctor Shift Display Features

## Overview

The cardiology display application now includes a comprehensive doctor shift management system that displays daily shifts for attending cardiologists and residents at the bottom of the GUI.

## Features

### 1. Automatic Shift Display
- Displays today's shifts in a dedicated section at the bottom of the screen
- Shows four types of shifts:
  - **Επιμελητές** (Attending Cardiologists)
  - **Μεγάλη Εφημερία** (Major 24-hour Shift)
  - **Μικρή Εφημερία** (Minor 24-hour Shift)
  - **Καρδιολόγος ΤΕΠ** (TEP Cardiologist 12-hour Shift)

### 2. Monthly File Management
- Prompts user to load a monthly shift file on first launch
- Validates that the file matches the current month and year
- Caches shift data for quick loading on subsequent launches
- Allows manual file loading at any time via "Φόρτωση Αρχείου" button

### 3. Month Validation
When loading a shift file, the system:
- Extracts month and year from the DOCX file
- Compares with current date
- Warns user if file is for a different month
- Allows user to proceed or cancel

### 4. Real-Time Editing
- "Επεξεργασία" button opens an edit dialog
- User can modify shift assignments for today
- Changes are saved to cache immediately
- Display updates automatically after saving
- Useful for last-minute schedule changes

### 5. Persistent Storage
- Shifts are cached in `shifts_cache.json`
- Cache is automatically loaded on application start
- No need to reload the DOCX file every time
- Cache is updated when:
  - New DOCX file is loaded
  - User edits shift information

## File Format Requirements

### DOCX Structure

The monthly shift file must contain **two tables**:

#### Table 1: Attending Cardiologists
```
| Day | Month    | Weekday  | Names              |
|-----|----------|----------|--------------------|
| 01  | ΟΚΤΩΒΡΙΟΥ| Τετάρτη  | Καρυοφύλλης        |
|     |          |          | Τσιάπρας*          |
```

- Column 0: Day number (01-31)
- Column 1: Month name in Greek (genitive case)
- Column 2: Weekday in Greek
- Column 3: Names (one per line, asterisk for readiness)

#### Table 2: Residents
```
| Day | Month    | Weekday | Major Shift | Minor Shift | TEP        |
|-----|----------|---------|-------------|-------------|------------|
| 01  | ΟΚΤΩΒΡΙΟΥ| Τετάρτη | Μακρής      | Ζυγούρη     | Παπαπέτρου |
```

- Column 0: Day number (01-31)
- Column 1: Month name in Greek (genitive case)
- Column 2: Weekday in Greek
- Column 3: Major shift doctor name
- Column 4: Minor shift doctor name
- Column 5: TEP cardiologist name

### File Naming Convention

Suggested format: `ΕΦΗΜΕΡΙΕΣ [MONTH] [YEAR].docx`

Example: `ΕΦΗΜΕΡΙΕΣ ΟΚΤΩΒΡΙΟΣ 2025.docx`

## Usage Guide

### Initial Setup

1. **Launch the application**
   ```bash
   python3 cardiology_display.py
   ```

2. **Load shift file when prompted**
   - Dialog will appear asking if you want to load the shift file
   - Click "Yes" to open file browser
   - Navigate to your monthly DOCX file
   - Select and open the file

3. **Verify the shift display**
   - Check the bottom section for today's shifts
   - Verify all fields are populated correctly

### Updating Shifts

1. **Click "Επεξεργασία" button** in the shift section

2. **Edit fields as needed:**
   - Επιμελητές: Comma-separated list of attending names
   - Μεγάλη Εφημερία: Single resident name
   - Μικρή Εφημερία: Single resident name
   - Καρδιολόγος ΤΕΠ: Single cardiologist name

3. **Click "Αποθήκευση"** to save changes

4. **Display updates immediately**

### Loading New Monthly File

1. **Click "Φόρτωση Αρχείου"** button

2. **Select the new month's DOCX file**

3. **System validates the month/year**
   - If correct: File loads immediately
   - If mismatch: User gets warning dialog with option to proceed

4. **Cache is updated** with new data

## Technical Details

### Module: shift_parser.py

**Key Components:**

- `DailyShift` dataclass: Represents a single day's shift assignments
- `ShiftParser` class: Parses DOCX files and manages shift data

**Key Methods:**

- `parse()`: Extracts shift data from DOCX tables
- `get_shift_for_date(date)`: Returns shift for specific date
- `validate_month_year(month, year)`: Validates file matches expected month
- `update_shift(day, field, value)`: Updates a specific shift field
- `save_to_json()`: Saves shifts to cache
- `load_from_json()`: Loads shifts from cache

### Integration in cardiology_display.py

**New Methods:**

- `create_shift_section()`: Creates GUI section for shifts
- `load_or_prompt_shift_file()`: Handles initial file loading
- `prompt_for_shift_file()`: Shows file selection dialog
- `load_shift_file()`: Processes selected DOCX file
- `update_shift_display()`: Updates GUI with shift information
- `edit_shifts()`: Opens edit dialog

**Auto-refresh:**

The `auto_refresh()` method now also calls `update_shift_display()` to ensure shifts are updated every 30 minutes along with hospital data.

## Cache File Format

`shifts_cache.json` structure:

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
      "attendings": ["Καρυοφύλλης", "Τσιάπρας"],
      "major_shift": "Μακρής",
      "minor_shift": "Ζυγούρη",
      "tep_cardiologist": "Παπαπέτρου"
    }
  }
}
```

## Troubleshooting

### Problem: Shifts don't appear

**Solution:**
1. Check if shift file was loaded successfully
2. Verify today's date exists in the DOCX file
3. Click "Φόρτωση Αρχείου" to reload

### Problem: Wrong month data displayed

**Solution:**
1. Delete `shifts_cache.json` file
2. Restart application
3. Load correct month's DOCX file

### Problem: DOCX file won't parse

**Solution:**
1. Verify file has exactly 2 tables
2. Check table structure matches requirements
3. Ensure Greek text encoding is correct (UTF-8)
4. Verify month name appears in document

### Problem: Edit changes don't save

**Solution:**
1. Check file permissions for `shifts_cache.json`
2. Verify application has write access to directory
3. Check console for error messages

## Example Workflow

### Monthly Update Process

**Beginning of new month:**

1. Receive new shift schedule DOCX file
2. Open cardiology display application
3. Click "Φόρτωση Αρχείου"
4. Select new month's file
5. Confirm month validation dialog
6. Verify today's shifts display correctly

**During the month:**

- Application loads shifts from cache automatically
- No need to reload file daily
- Use "Επεξεργασία" for last-minute changes
- Changes persist across application restarts

## GUI Layout

```
┌─────────────────────────────────────────────────────┐
│  Header: ΝΟΣΟΚΟΜΕΙΑ ΕΦΗΜΕΡΙΑΣ - ΚΑΡΔΙΟΛΟΓΙΑ        │
│  Date/Time          Specialty Selector [▼]          │
├─────────────────────────────────────────────────────┤
│                                                      │
│  [Hospital Cards - Scrollable Section]              │
│                                                      │
│                                                      │
├─────────────────────────────────────────────────────┤
│  ΕΦΗΜΕΡΙΕΣ ΚΑΡΔΙΟΛΟΓΙΚΟΥ ΤΟΜΕΑ - ΣΗΜΕΡΑ            │
│                    [Φόρτωση Αρχείου] [Επεξεργασία] │
│                                                      │
│  Επιμελητές:           Name1, Name2                 │
│  Μεγάλη Εφημερία:      ResidentName                 │
│  Μικρή Εφημερία:       ResidentName                 │
│  Καρδιολόγος ΤΕΠ:      CardioName                   │
└─────────────────────────────────────────────────────┘
```

## Future Enhancements

Possible improvements for future versions:

1. **Weekly View**: Display shifts for entire week
2. **Shift Swapping**: Built-in interface for trading shifts
3. **Notification System**: Alert when shifts change
4. **Contact Integration**: Click name to see contact info
5. **Export Options**: Generate PDF reports of monthly shifts
6. **Multi-department Support**: Extend to other departments
7. **Cloud Sync**: Sync shifts across multiple displays
8. **Mobile App**: Companion mobile application

## Support

For issues or questions:
- Check CLAUDE.md for project architecture details
- Review this document for usage guidance
- Verify DOCX file format matches specifications
- Check console output for error messages
