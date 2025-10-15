# Athens On-Duty Hospitals Display

A Python program that displays on-duty hospitals in Athens, Greece for different medical specialties. The data automatically updates daily at 08:00 by scraping official Greek Ministry of Health PDF files.

## Features

- 📊 Displays on-duty hospitals grouped by medical specialty
- 🕐 Automatic daily updates at 08:00
- 📄 **Automatic scraping from official Ministry of Health PDF/DOC files**
- ⏰ Shows time slots for each hospital (morning, afternoon, 24-hour)
- 🔍 Search hospitals by specialty or area
- 💾 Saves data to JSON format
- 🇬🇷 Bilingual display (Greek/English)
- ✅ Real-time data from official government sources

## Installation

### Option 1: Windows Executable (Recommended for End Users)

Download the pre-built Windows executable:

1. Go to the [Releases](../../releases) page or [Actions](../../actions) tab
2. Download `HospitalOnDutyDisplay.exe`
3. Run the executable - no Python installation required!

The executable is a standalone application that includes all dependencies.

### Option 2: Python Installation (For Development)

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install requests beautifulsoup4 schedule lxml
```

## Usage

### Basic Usage

Run the program to display current on-duty hospitals:

```bash
python3 athens_hospitals.py
```

The program will:
1. Fetch the latest hospital data
2. Display hospitals grouped by specialty
3. Save data to `hospitals_on_duty.json`
4. Keep running and automatically update at 08:00 daily

### Output Example

```
======================================================================
  ΝΟΣΟΚΟΜΕΙΑ ΕΦΗΜΕΡΙΑΣ ΑΘΗΝΩΝ / ATHENS ON-DUTY HOSPITALS
  Tuesday, 14 October 2025
  Τελευταία ενημέρωση: 08:00:15
======================================================================

┌─ Γενική Ιατρική / General Medicine ───────────────────────────────
│
│  1. Γενικό Νοσοκομείο Αθηνών «Ιπποκράτειο»
│     📍 Βασ. Σοφίας 114, Αθήνα
│     📞 213 2088000
│     🏘️  Κέντρο Αθήνας
└────────────────────────────────────────────────────────────────────

┌─ Καρδιολογία / Cardiology ────────────────────────────────────────
│
│  1. Γενικό Νοσοκομείο Αθηνών «Ο Ευαγγελισμός»
│     📍 Υψηλάντου 45-47, Αθήνα
│     📞 213 2041000
│     🏘️  Κολωνάκι
└────────────────────────────────────────────────────────────────────

======================================================================
ℹ️  Για επείγοντα περιστατικά καλέστε: 166 (ΕΚΑΒ) ή 112
   For emergencies call: 166 (EKAB ambulance) or 112
======================================================================
```

## Data Sources

The program fetches data from official sources:

1. **Ministry of Health Official PDF Files** - Primary source (https://www.moh.gov.gr)
   - Automatically downloads daily PDF files
   - Parses structured tables with hospital duty schedules
   - Includes all time slots (08:00-14:30, 14:30-08:00, 24-hour)
2. **Sample data** - Fallback if official source is unavailable

### How It Works

The program uses the `moh_scraper.py` module to:

1. Connect to the official Ministry of Health website
2. Find the PDF file for the current date
3. Download the PDF (files are published daily)
4. Parse the tables containing hospital duty schedules
5. Extract hospital names, specialties, and time slots
6. Display the information in a formatted view

### Data Structure

The PDF files contain tables with:
- **Columns**: Different time slots (morning, afternoon, evening, 24-hour)
- **Rows**: Medical specialties
- **Cells**: Hospital names on duty for that specialty and time slot

### Supported File Formats

- ✅ **PDF files** - Fully supported with table extraction
- ⚠️ **DOC files** - Basic support (old Microsoft Word format)

## Configuration

### Change Update Time

Edit the schedule in `main()` function:

```python
# Change from 08:00 to another time (e.g., 07:30)
schedule.every().day.at("07:30").do(service.update_data)
```

### Add Custom Hospitals

Modify the `_get_sample_data()` method to include additional hospitals:

```python
Hospital(
    name="Your Hospital Name",
    specialty="Specialty",
    address="Address",
    phone="Phone Number",
    area="Area",
    on_duty_date=today
)
```

## Medical Specialties Covered

- Γενική Ιατρική / General Medicine
- Χειρουργική / Surgery
- Καρδιολογία / Cardiology
- Μαιευτική - Γυναικολογία / Obstetrics - Gynecology
- Παιδιατρική / Pediatrics
- Ορθοπεδική / Orthopedics
- Τραυματολογία / Trauma
- Πνευμονολογία / Pulmonology
- Ψυχιατρική / Psychiatry

## Emergency Contacts

- **166** - EKAB (National Centre for Emergency Care)
- **112** - EU Emergency Number
- **14944** - Hospital Duty Information Line

## Files

- `cardiology_display.py` - Main GUI application
- `athens_hospitals.py` - CLI program with display and scheduling
- `moh_scraper.py` - Ministry of Health PDF scraper module
- `shift_parser.py` - Doctor shift schedule parser
- `requirements.txt` - Python dependencies
- `cardiology_display.spec` - PyInstaller build configuration
- `build_windows.bat` - Windows build script
- `hospitals_on_duty.json` - Generated data file (created after first run)
- `shifts_cache.json` - Cached shift schedules
- `BUILD.md` - Detailed build instructions
- `README.md` - This file

## Project Structure

```
.
├── athens_hospitals.py    # Main display program with scheduling
├── moh_scraper.py         # PDF/DOC scraper for Ministry of Health
├── requirements.txt       # Python package dependencies
├── README.md             # Documentation
└── hospitals_on_duty.json # Generated data cache (after first run)
```

## Technical Details

### PDF Parsing

The scraper uses `pdfplumber` library to:
- Extract tables from PDF files
- Identify column headers for time slots
- Parse hospital names from table cells
- Normalize hospital abbreviations to full names
- Map specialty names to bilingual format

### Scraper Module (`moh_scraper.py`)

Key classes and methods:

- `MOHHospitalScraper` - Main scraper class
  - `get_available_files()` - Lists all available PDF/DOC files
  - `download_file(fdl)` - Downloads file by its ID
  - `parse_pdf(content, date)` - Parses PDF and extracts hospital data
  - `get_today_schedule()` - Gets current day's schedule
  - `get_schedule_for_date(date)` - Gets schedule for specific date

### Hospital Name Mapping

The scraper includes comprehensive mappings for:
- Hospital abbreviations (e.g., "ΚΑΤ" → "Γενικό Νοσοκομείο Αθηνών «ΚΑΤ»")
- Specialty names (Greek and English bilingual)
- Time slot formats

## Troubleshooting

### No Data Available

If the program can't fetch data from Ministry of Health:
- Check internet connection
- Verify the Ministry of Health website is accessible: https://www.moh.gov.gr
- Check if a PDF file exists for today's date on the website
- The program will automatically fall back to sample data

### PDF Parsing Errors

If you encounter PDF parsing issues:
- Check that `pdfplumber` is installed: `pip install pdfplumber`
- Verify the PDF file format hasn't changed on the MOH website
- Check the scraper logs for detailed error messages

### Wrong Date

If the program shows the wrong day's schedule:
- The Ministry publishes files with Greek date names
- Ensure your system timezone is set correctly
- Check that the date matching logic in `moh_scraper.py` is working

## License

This program is provided as-is for educational and practical use.

## Building Windows Executable

To build the Windows executable yourself:

### Quick Build (Windows)

```cmd
build_windows.bat
```

### Manual Build

```cmd
pip install -r requirements.txt
pyinstaller cardiology_display.spec
```

The executable will be created in the `dist/` folder.

For detailed instructions, see [BUILD.md](BUILD.md).

### Automated Builds

This project uses GitHub Actions to automatically build Windows executables on every push. Check the [Actions](../../actions) tab to download the latest build.

## Contributing

To improve this program:
1. Add official government API integration
2. Implement better error handling
3. ✅ GUI interface - **Completed!**
4. Support more cities beyond Athens
5. Add notifications system
6. ✅ Windows executable distribution - **Completed!**

## Notes

- Hospital duty schedules typically change daily at 08:00
- Always call 166 or 112 for emergencies
- This program provides information only - verify with hospitals directly
- Data accuracy depends on the source
