# Usage Guide - Athens Hospital Duty Display

## Quick Start

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run the program
python3 athens_hospitals.py
```

The program will:
1. Automatically fetch today's hospital duty schedule from the Ministry of Health
2. Display it in a formatted, easy-to-read layout
3. Save the data to `hospitals_on_duty.json`
4. Keep running and update automatically at 08:00 every day

## Using the Scraper Module Separately

You can use the scraper module independently:

```python
from moh_scraper import MOHHospitalScraper
from datetime import date

# Create scraper instance
scraper = MOHHospitalScraper()

# Get today's schedule
hospitals = scraper.get_today_schedule()

# Get schedule for a specific date
hospitals = scraper.get_schedule_for_date(date(2025, 10, 14))

# List available files
files = scraper.get_available_files()
for text, fdl, file_type in files[:10]:
    print(f"{file_type}: {text}")

# Display results
for hospital in hospitals:
    print(f"{hospital.name} - {hospital.specialty}")
    print(f"  Time: {hospital.time_slot}")
```

## Understanding the Output

### Time Slots

The PDF files organize hospitals by time slots:

- **08:00-14:30** - Morning shift
- **08:00-16:00** - Extended morning shift
- **08:00-23:00** - Day shift
- **14:30-08:00 επομένης** - Afternoon/night shift (until next morning)
- **08:00-08:00 επομένης** - 24-hour duty

### Specialty Groups

Hospitals are grouped by medical specialty:

- Παθολογία / Internal Medicine
- Καρδιολογία / Cardiology
- Χειρουργική / Surgery
- Ορθοπεδική / Orthopedics
- Παιδιατρική / Pediatrics
- Μαιευτική-Γυναικολογία / Obstetrics-Gynecology
- And 20+ more specialties

### Reading the Display

```
┌─ Καρδιολογία / Cardiology ─────────────────────────────────────────
│
│  1. Γενικό Νοσοκομείο Αθηνών «Ο Ευαγγελισμός»
│     🕐 Ωράριο: 14:30-08:00 επομένης
│
│  2. Πανεπιστημιακό Γενικό Νοσοκομείο «Αττικόν»
│     🕐 Ωράριο: 08:00-08:00 επομένης
└────────────────────────────────────────────────────────────────────
```

This shows:
- Specialty name (bilingual)
- Hospital name
- Time slot they're on duty

## Command Line Options

The program runs continuously by default. To run it once and exit:

1. Edit `athens_hospitals.py`
2. Comment out the scheduling section at the bottom
3. Keep only:

```python
if __name__ == "__main__":
    service = AthensHospitalService()
    service.update_data()
    service.display_hospitals()
    service.save_to_json()
```

## Running as a Service

### Using systemd (Linux)

Create `/etc/systemd/system/athens-hospitals.service`:

```ini
[Unit]
Description=Athens Hospital Duty Display
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/OCSC TEP display
ExecStart=/usr/bin/python3 /path/to/OCSC TEP display/athens_hospitals.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable athens-hospitals
sudo systemctl start athens-hospitals
sudo systemctl status athens-hospitals
```

### Using cron (Alternative)

Run once daily at 08:00:

```bash
crontab -e
```

Add:
```
0 8 * * * cd /path/to/OCSC\ TEP\ display && /usr/bin/python3 athens_hospitals.py
```

## Integrating with Other Applications

### JSON Output

The program saves data to `hospitals_on_duty.json`:

```json
{
  "last_update": "2025-10-14T20:57:46.123456",
  "hospitals": [
    {
      "name": "Γενικό Νοσοκομείο Αθηνών «Ο Ευαγγελισμός»",
      "specialty": "Καρδιολογία / Cardiology",
      "time_slot": "14:30-08:00 επομένης",
      "on_duty_date": "2025-10-14",
      "address": "",
      "phone": "",
      "area": ""
    }
  ]
}
```

You can read this file from other applications.

### Using as a Library

```python
from athens_hospitals import AthensHospitalService

service = AthensHospitalService()
service.update_data()

# Get all hospitals
hospitals = service.hospitals

# Search by specialty
cardiology = service.search_by_specialty("Καρδιολογία")

# Search by area
downtown = service.search_by_area("Κέντρο")
```

## Tips

1. **First run takes longer** - The program downloads the PDF file
2. **Cached data** - Subsequent runs are faster as data is cached
3. **Daily updates** - The Ministry publishes new files each day at 08:00
4. **Fallback data** - If internet is down, sample data is shown
5. **Multiple runs** - Safe to run multiple times; data is refreshed

## Getting Help

- Check logs for error messages
- Verify internet connection
- Ensure Ministry of Health website is accessible
- Check that PDF files are available for the current date
- Report issues with specific error messages
