# Quick Start Guide

## Installation (One-time)

```bash
cd "/home/dimitris/Έγγραφα/OCSC TEP display"
pip3 install -r requirements.txt
```

## Run the Program

```bash
python3 athens_hospitals.py
```

That's it! The program will:
1. Fetch today's hospital schedule from Ministry of Health
2. Display all on-duty hospitals grouped by specialty
3. Show time slots for each hospital
4. Save data to `hospitals_on_duty.json`
5. Keep running and auto-update at 08:00 daily

## Stop the Program

Press `Ctrl+C`

## What You'll See

```
============================================================
Ενημέρωση δεδομένων... / Updating data...
Ώρα: 14/10/2025 20:57:40
============================================================

  Fetching from Ministry of Health official files...
  ✓ Successfully fetched 150 entries from MOH
✓ Δεδομένα ενημερώθηκαν επιτυχώς! / Data updated successfully!
  Βρέθηκαν 150 νοσοκομεία εφημερίας
  Found 150 hospitals on duty

======================================================================
  ΝΟΣΟΚΟΜΕΙΑ ΕΦΗΜΕΡΙΑΣ ΑΘΗΝΩΝ / ATHENS ON-DUTY HOSPITALS
  Tuesday, 14 October 2025
  Τελευταία ενημέρωση: 20:57:46
======================================================================

┌─ Καρδιολογία / Cardiology ─────────────────────────────────────────
│
│  1. Γενικό Νοσοκομείο Αθηνών «Ο Ευαγγελισμός»
│     🕐 Ωράριο: 14:30-08:00 επομένης
│
│  2. Πανεπιστημιακό Γενικό Νοσοκομείο «Αττικόν»
│     🕐 Ωράριο: 08:00-08:00 επομένης
└────────────────────────────────────────────────────────────────────
...
```

## Files Created

- `hospitals_on_duty.json` - Hospital data in JSON format

## Emergency Numbers

- **166** - ΕΚΑΒ (Greek Ambulance)
- **112** - EU Emergency Number

## Data Source

Official Greek Ministry of Health:
https://www.moh.gov.gr/articles/citizen/efhmeries-nosokomeiwn/68-efhmeries-nosokomeiwn-attikhs

## More Info

- See `README.md` for detailed documentation
- See `USAGE.md` for advanced usage
- See `PROJECT_SUMMARY.md` for technical overview
