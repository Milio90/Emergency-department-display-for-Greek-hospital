#!/usr/bin/env python3
"""
Ministry of Health Hospital Duty Scraper
Scrapes on-duty hospital schedules from official Greek government PDF/DOC files
"""

import re
import requests
import pdfplumber
import olefile
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import io


@dataclass
class Hospital:
    """Represents a hospital with its duty schedule"""
    name: str
    specialty: str
    time_slot: str  # e.g., "08:00-14:30", "14:30-08:00 επομένης"
    on_duty_date: str
    address: str = ""
    phone: str = ""
    area: str = ""


class MOHHospitalScraper:
    """Scraper for Ministry of Health hospital duty schedules"""

    BASE_URL = "https://www.moh.gov.gr/articles/citizen/efhmeries-nosokomeiwn/68-efhmeries-nosokomeiwn-attikhs"

    # Hospital abbreviation to full name mapping
    HOSPITAL_NAMES = {
        "ΕΥΑΓΓΕΛΙΣΜΟΣ": "Γενικό Νοσοκομείο Αθηνών «Ο Ευαγγελισμός»",
        "ΛΑΪΚΟ": "Γενικό Νοσοκομείο Αθηνών «Λαϊκό»",
        "ΕΛΠΙΣ": "Γενικό Νοσοκομείο Αθηνών «Ελπίς»",
        "ΑΓ. ΑΝΑΡΓΥΡΟΙ": "Γενικό Οικουμενικό Νοσοκομείο Κρατικό «Άγιοι Ανάργυροι»",
        "ΣΙΣΜΑΝΟΓΛΕΙΟ": "Γενικό Νοσοκομείο Αθηνών «Σισμανόγλειο»",
        "ΠΑΜΜΑΚΑΡΙΣΤΟΣ": "Γενικό Νοσοκομείο Αθηνών «Παμμακάριστος»",
        "ΑΤΤΙΚΟΝ": "Πανεπιστημιακό Γενικό Νοσοκομείο «Αττικόν»",
        "ΚΑΤ": "Γενικό Νοσοκομείο Αθηνών «ΚΑΤ»",
        "ΑΣΚΛΗΠΙΕΙΟ": "Γενικό Νοσοκομείο «Ασκληπιείο» Βούλας",
        "ΚΩΝ/ΠΟΥΛΕΙΟ": "Γενικό Νοσοκομείο Νέας Ιωνίας «Κωνσταντοπούλειο»",
        "ΠΕΙΡΑΙΑΣ": "Γενικό Νοσοκομείο Πειραιώς «Τζάνειο»",
        "ΑΛΕΞΑΝΔΡΑ": "Γενικό Νοσοκομείο Αθηνών «Αλεξάνδρα»",
        "ΑΡΕΤΑΙΕΙΟ": "Γενικό Νοσοκομείο Αθηνών «Αρεταίειο»",
        "ΕΛ. ΒΕΝΙΖΕΛΟΥ": "Γενικό Μαιευτικό «Ελένα Βενιζέλου»",
        "ΠΕΝΤΕΛΗΣ": "Γενικό Νοσοκομείο Παίδων «Πεντέλης»",
        "ΑΓΛ. ΚΥΡΙΑΚΟΥ": "Γενικό Νοσοκομείο Παίδων Αττικής «Αγλαΐα Κυριακού»",
        "ΣΩΤΗΡΙΑ": "Νοσοκομείο Θώρακος Αθηνών «Σωτηρία»",
        "ΙΠΠΟΚΡΑΤΕΙΟ": "Γενικό Νοσοκομείο Αθηνών «Ιπποκράτειο»",
        "ΔΡΟΜΟΚΑΪΤΕΙΟ": "Ψυχιατρικό Νοσοκομείο Αττικής «Δρομοκαΐτειο»",
        "Α. ΣΥΓΓΡΟΣ": "Νοσηλευτικό Δερματολογικό Νοσοκομείο Αθηνών «Ανδρέας Συγγρός»",
        "ΟΦΘΑΛΜΙΑΤΡΕΙΟ": "Νοσηλευτικό Οφθαλμιατρείο Αθηνών",
        "ΑΓ. ΣΑΒΒΑΣ": "Αντικαρκινικό-Ογκολογικό Νοσοκομείο Αθηνών «Άγιος Σάββας»",
        "Γ. ΓΕΝΝΗΜΑΤΑΣ": "Γενικό Νοσοκομείο Αθηνών «Γεώργιος Γεννηματάς»",
        "ΚΟΡΓ. ΜΠΕΝ. ΕΕΣ": "Γενικό Νοσοκομείο Αθηνών «Κοργιαλένειο-Μπενάκειο Ε.Ε.Σ.»",
    }

    # Specialty name normalization
    SPECIALTY_NAMES = {
        "Παθολογική": "Παθολογία / Internal Medicine",
        "Καρδιολογική": "Καρδιολογία / Cardiology",
        "Χειρουργική": "Χειρουργική / Surgery",
        "Αγγειοχειρ/κή": "Αγγειοχειρουργική / Vascular Surgery",
        "Αιματολογική": "Αιματολογία / Hematology",
        "Γαστρεντερ/γική": "Γαστρεντερολογία / Gastroenterology",
        "Γναθοχειρουργική": "Γναθοχειρουργική / Maxillofacial Surgery",
        "Δερματολογική": "Δερματολογία / Dermatology",
        "Ενδοκρινολογική": "Ενδοκρινολογία / Endocrinology",
        "Θωρακοχειρ/γική": "Θωρακοχειρουργική / Thoracic Surgery",
        "Καρδιοχειρ/κή": "Καρδιοχειρουργική / Cardiac Surgery",
        "Νευρολογική": "Νευρολογία / Neurology",
        "Νευροχειρουργική": "Νευροχειρουργική / Neurosurgery",
        "Νεφρολογική": "Νεφρολογία / Nephrology",
        "Ογκολογική": "Ογκολογία / Oncology",
        "Οδοντιατρική": "Οδοντιατρική / Dentistry",
        "Ορθοπαιδική": "Ορθοπεδική / Orthopedics",
        "Ουρολογική": "Ουρολογία / Urology",
        "Οφθαλμολογική": "Οφθαλμολογία / Ophthalmology",
        "Πνευμονολογική": "Πνευμονολογία / Pulmonology",
        "Πλαστ. Χειρουργική": "Πλαστική Χειρουργική / Plastic Surgery",
        "Ρευματολογική": "Ρευματολογία / Rheumatology",
        "Ψυχιατρική": "Ψυχιατρική / Psychiatry",
        "Ω.Ρ.Λ.": "Ωτορινολαρυγγολογία / ENT",
        "Γυναικολογική": "Γυναικολογία / Gynecology",
        "Μαιευτική": "Μαιευτική / Obstetrics",
        "Παιδιατρικό": "Παιδιατρική / Pediatrics",
        "Παιδοψυχιατρική": "Παιδοψυχιατρική / Child Psychiatry",
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })

    def get_available_files(self, days_back: int = 7) -> List[Tuple[str, str, str]]:
        """
        Get list of available PDF/DOC files for recent dates
        Returns: List of (date_text, pdf_fdl, doc_fdl)
        """
        try:
            response = self.session.get(self.BASE_URL)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            files = []
            links = soup.find_all('a', href=True)

            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)

                if 'fdl=' in href and ('2025' in text or '2024' in text):
                    # Extract fdl number
                    fdl_match = re.search(r'fdl=(\d+)', href)
                    if fdl_match:
                        fdl = fdl_match.group(1)
                        # Check if PDF or DOC based on text
                        if '.pdf' in text.lower():
                            file_type = 'pdf'
                        else:
                            file_type = 'doc'

                        files.append((text, fdl, file_type))

            return files

        except Exception as e:
            print(f"Error fetching file list: {e}")
            return []

    def download_file(self, fdl: str) -> Optional[bytes]:
        """Download a file by its fdl parameter"""
        try:
            url = f"{self.BASE_URL}?fdl={fdl}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Error downloading file {fdl}: {e}")
            return None

    def parse_pdf(self, pdf_content: bytes, duty_date: str) -> List[Hospital]:
        """Parse PDF file and extract hospital duty information"""
        hospitals = []

        try:
            with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
                for page in pdf.pages:
                    # Extract tables
                    tables = page.extract_tables()

                    for table in tables:
                        if not table or len(table) < 2:
                            continue

                        # Find header row to identify columns
                        header_row = None
                        for i, row in enumerate(table[:5]):  # Check first 5 rows instead of 3
                            if row and 'Κλινικές' in str(row):
                                header_row = i
                                break

                        if header_row is None:
                            continue

                        # Parse each row after header
                        for row in table[header_row + 1:]:
                            if not row or len(row) < 2:
                                continue

                            specialty = row[0].strip() if row[0] else ""
                            if not specialty or specialty == "Κλινικές":
                                continue

                            # Normalize specialty name
                            specialty_display = self.SPECIALTY_NAMES.get(
                                specialty, specialty
                            )

                            # Extract hospitals from different time slots
                            # Columns: [Specialty, 08:00-14:30, 08:00-16:00, 08:00-23:00, 14:30-08:00, 08:00-08:00]
                            time_slots = [
                                ("08:00-14:30", 1),
                                ("08:00-16:00", 2),
                                ("08:00-23:00", 3),
                                ("14:30-08:00 επομένης", 4),
                                ("08:00-08:00 επομένης", 5),
                            ]

                            for time_label, col_idx in time_slots:
                                if col_idx < len(row):
                                    cell_text = row[col_idx]
                                    if cell_text:
                                        # Extract hospital names from cell
                                        hospital_names = self._extract_hospital_names(
                                            cell_text
                                        )

                                        for hosp_name in hospital_names:
                                            hospitals.append(
                                                Hospital(
                                                    name=hosp_name,
                                                    specialty=specialty_display,
                                                    time_slot=time_label,
                                                    on_duty_date=duty_date,
                                                )
                                            )

        except Exception as e:
            print(f"Error parsing PDF: {e}")

        return hospitals

    def parse_doc(self, doc_content: bytes, duty_date: str) -> List[Hospital]:
        """Parse old DOC file and extract hospital duty information"""
        hospitals = []

        try:
            # Use olefile to read old .doc format
            ole = olefile.OleFileIO(doc_content)

            # Extract text from WordDocument stream
            if ole.exists('WordDocument'):
                word_stream = ole.openstream('WordDocument')
                # This is a simplified approach - old DOC format is complex
                # For production, consider using libreoffice --convert-to or similar
                print("DOC parsing: Old format detected, attempting text extraction")

                # For now, return empty list - DOC parsing requires more complex handling
                # Alternative: Convert DOC to PDF first using external tool

        except Exception as e:
            print(f"Error parsing DOC: {e}")

        return hospitals

    def _extract_hospital_names(self, text: str) -> List[str]:
        """Extract hospital names from cell text"""
        if not text or text.strip() == "":
            return []

        # Split by newlines and common separators
        lines = re.split(r'\n|Γ\.Ν\.', text)
        hospital_names = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Prepend Γ.Ν. if it was split
            if not line.startswith('Γ.') and not line.startswith('Π.') and not line.startswith('Ν.'):
                line = 'Γ.Ν.' + line

            # Check if this contains a known hospital abbreviation
            for abbr, full_name in self.HOSPITAL_NAMES.items():
                if abbr in line:
                    hospital_names.append(full_name)
                    break
            else:
                # If no match, use the text as-is (cleaned)
                if 'Γ.Ν.' in line or 'Π.Γ.Ν.' in line or 'Ν.' in line:
                    hospital_names.append(line)

        return hospital_names

    def get_today_schedule(self) -> List[Hospital]:
        """Get today's hospital duty schedule"""
        return self.get_schedule_for_date(date.today())

    def get_schedule_for_date(self, target_date: date) -> List[Hospital]:
        """Get hospital duty schedule for a specific date"""
        # Format date to match file names
        # Files are named like "ΤΡΙΤΗ 14 ΟΚΤΩΒΡΙΟΥ 2025"
        greek_months = {
            1: "ΙΑΝΟΥΑΡΙΟΥ", 2: "ΦΕΒΡΟΥΑΡΙΟΥ", 3: "ΜΑΡΤΙΟΥ",
            4: "ΑΠΡΙΛΙΟΥ", 5: "ΜΑΪΟΥ", 6: "ΙΟΥΝΙΟΥ",
            7: "ΙΟΥΛΙΟΥ", 8: "ΑΥΓΟΥΣΤΟΥ", 9: "ΣΕΠΤΕΜΒΡΙΟΥ",
            10: "ΟΚΤΩΒΡΙΟΥ", 11: "ΝΟΕΜΒΡΙΟΥ", 12: "ΔΕΚΕΜΒΡΙΟΥ"
        }

        date_str = f"{target_date.day} {greek_months[target_date.month]} {target_date.year}"

        # Get available files
        files = self.get_available_files()

        # Find matching file
        matching_file = None
        for file_text, fdl, file_type in files:
            if date_str in file_text:
                matching_file = (fdl, file_type)
                break

        if not matching_file:
            print(f"No file found for date: {target_date}")
            return []

        fdl, file_type = matching_file

        # Download file
        content = self.download_file(fdl)
        if not content:
            return []

        # Parse based on file type
        if file_type == 'pdf':
            return self.parse_pdf(content, target_date.isoformat())
        else:
            return self.parse_doc(content, target_date.isoformat())


if __name__ == "__main__":
    # Test the scraper
    scraper = MOHHospitalScraper()

    print("Fetching available files...")
    files = scraper.get_available_files()
    print(f"Found {len(files)} files")

    if files:
        print("\nRecent files:")
        for text, fdl, ftype in files[:5]:
            print(f"  [{ftype.upper()}] {text[:60]}... (fdl={fdl})")

    print("\n" + "="*70)
    print("Fetching today's hospital schedule...")
    print("="*70 + "\n")

    hospitals = scraper.get_today_schedule()

    if hospitals:
        print(f"Found {len(hospitals)} hospital duty entries\n")

        # Group by specialty
        by_specialty = {}
        for h in hospitals:
            if h.specialty not in by_specialty:
                by_specialty[h.specialty] = []
            by_specialty[h.specialty].append(h)

        for specialty, hosp_list in sorted(by_specialty.items()):
            print(f"\n{specialty}")
            print("-" * 60)
            for h in hosp_list:
                print(f"  • {h.name}")
                print(f"    Ωράριο: {h.time_slot}")
    else:
        print("No hospital data found for today")
