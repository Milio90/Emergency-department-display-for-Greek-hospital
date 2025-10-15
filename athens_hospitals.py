#!/usr/bin/env python3
"""
Athens On-Duty Hospitals Display
Displays on-duty hospitals for different medical specialties in Athens, Greece
Updates daily at 08:00
"""

import datetime
import time
import json
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup
import schedule
from moh_scraper import MOHHospitalScraper, Hospital as MOHHospital


@dataclass
class Hospital:
    """Represents a hospital with its details"""
    name: str
    specialty: str
    address: str
    phone: str
    area: str
    on_duty_date: str
    time_slot: str = ""


class AthensHospitalService:
    """Service to fetch and display on-duty hospitals in Athens"""

    def __init__(self):
        self.hospitals: List[Hospital] = []
        self.last_update: Optional[datetime.datetime] = None
        self.moh_scraper = MOHHospitalScraper()

    def fetch_hospital_data(self) -> List[Hospital]:
        """
        Fetch on-duty hospital data from available sources

        Priority:
        1. Official Ministry of Health PDF/DOC files
        2. Fallback to sample data for demonstration
        """

        # Method 1: Try to fetch from Ministry of Health official files
        try:
            print("  Fetching from Ministry of Health official files...")
            moh_hospitals = self.moh_scraper.get_today_schedule()
            if moh_hospitals:
                print(f"  ✓ Successfully fetched {len(moh_hospitals)} entries from MOH")
                # Convert MOH Hospital objects to local Hospital objects
                hospitals = []
                for moh_h in moh_hospitals:
                    hospitals.append(Hospital(
                        name=moh_h.name,
                        specialty=moh_h.specialty,
                        address=moh_h.address or "",
                        phone=moh_h.phone or "",
                        area=moh_h.area or "",
                        on_duty_date=moh_h.on_duty_date,
                        time_slot=moh_h.time_slot
                    ))
                return hospitals
        except Exception as e:
            print(f"  ✗ Error fetching from Ministry of Health: {e}")

        # Fallback: Return sample data for demonstration
        print("  Using sample data as fallback...")
        return self._get_sample_data()

    def _fetch_from_xo_gr(self) -> List[Hospital]:
        """Fetch data from xo.gr"""
        url = "https://www.xo.gr/hospitals-on-duty/athens/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        hospitals = []

        # Parse hospital data from HTML (structure depends on actual website)
        # This is a template - adjust selectors based on actual HTML structure
        hospital_elements = soup.find_all('div', class_='hospital-item')

        for element in hospital_elements:
            try:
                hospital = Hospital(
                    name=element.find('h3').text.strip(),
                    specialty=element.find('span', class_='specialty').text.strip(),
                    address=element.find('span', class_='address').text.strip(),
                    phone=element.find('span', class_='phone').text.strip(),
                    area=element.find('span', class_='area').text.strip(),
                    on_duty_date=datetime.date.today().isoformat()
                )
                hospitals.append(hospital)
            except Exception as e:
                print(f"Error parsing hospital element: {e}")
                continue

        return hospitals

    def _fetch_from_vrisko(self) -> List[Hospital]:
        """Fetch data from vrisko.gr"""
        url = "https://www.vrisko.gr/en/hospital-duties/athens/all-clinics/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        hospitals = []

        # Parse hospital data (adjust based on actual structure)
        # This is a template

        return hospitals

    def _get_sample_data(self) -> List[Hospital]:
        """Return sample hospital data for demonstration"""
        today = datetime.date.today().isoformat()

        return [
            Hospital(
                name="Γενικό Νοσοκομείο Αθηνών «Ιπποκράτειο»",
                specialty="Γενική Ιατρική / General Medicine",
                address="Βασ. Σοφίας 114, Αθήνα",
                phone="213 2088000",
                area="Κέντρο Αθήνας",
                on_duty_date=today
            ),
            Hospital(
                name="Γενικό Νοσοκομείο Αθηνών «Λαϊκό»",
                specialty="Χειρουργική / Surgery",
                address="Αγίου Θωμά 17, Γουδή",
                phone="213 2061000",
                area="Γουδή",
                on_duty_date=today
            ),
            Hospital(
                name="Γενικό Νοσοκομείο Αθηνών «Ο Ευαγγελισμός»",
                specialty="Καρδιολογία / Cardiology",
                address="Υψηλάντου 45-47, Αθήνα",
                phone="213 2041000",
                area="Κολωνάκι",
                on_duty_date=today
            ),
            Hospital(
                name="Γενικό Νοσοκομείο Αθηνών «Αλεξάνδρα»",
                specialty="Μαιευτική - Γυναικολογία / Obstetrics - Gynecology",
                address="Βασ. Σοφίας 80, Αθήνα",
                phone="213 3162000",
                area="Κέντρο Αθήνας",
                on_duty_date=today
            ),
            Hospital(
                name="Παίδων «Αγία Σοφία»",
                specialty="Παιδιατρική / Pediatrics",
                address="Θηβών & Παπαδιαμαντοπούλου, Γουδή",
                phone="213 2013000",
                area="Γουδή",
                on_duty_date=today
            ),
            Hospital(
                name="Αττικό Νοσοκομείο",
                specialty="Ορθοπεδική / Orthopedics",
                address="Ρίμινι 1, Χαϊδάρι",
                phone="210 5831000",
                area="Χαϊδάρι",
                on_duty_date=today
            ),
            Hospital(
                name="ΚΑΤ - Γενικό Νοσοκομείο Αττικής",
                specialty="Τραυματολογία / Trauma",
                address="Νίκης 2, Κηφισιά",
                phone="213 2086000",
                area="Κηφισιά",
                on_duty_date=today
            ),
            Hospital(
                name="«Σωτηρία» - Νοσοκομείο Θώρακος Αθηνών",
                specialty="Πνευμονολογία / Pulmonology",
                address="Μεσογείων 152, Αθήνα",
                phone="213 2057000",
                area="Αμπελόκηποι",
                on_duty_date=today
            ),
            Hospital(
                name="Ψυχιατρικό Νοσοκομείο Αττικής",
                specialty="Ψυχιατρική / Psychiatry",
                address="Ρίμινι & Χαϊδαρίου, Χαϊδάρι",
                phone="213 2047000",
                area="Χαϊδάρι",
                on_duty_date=today
            ),
        ]

    def update_data(self):
        """Update hospital data"""
        print(f"\n{'='*60}")
        print(f"Ενημέρωση δεδομένων...")
        print(f"Ώρα: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*60}\n")

        self.hospitals = self.fetch_hospital_data()
        self.last_update = datetime.datetime.now()

        print(f"✓ Δεδομένα ενημερώθηκαν επιτυχώς!")
        print(f"  Βρέθηκαν {len(self.hospitals)} νοσοκομεία εφημερίας\n")

    def display_hospitals(self):
        """Display all on-duty hospitals grouped by specialty"""
        if not self.hospitals:
            print("Δεν υπάρχουν διαθέσιμα δεδομένα")
            return

        print(f"\n{'='*70}")
        print(f"  ΝΟΣΟΚΟΜΕΙΑ ΕΦΗΜΕΡΙΑΣ ΑΘΗΝΩΝ")
        print(f"  {datetime.date.today().strftime('%A, %d %B %Y')}")
        if self.last_update:
            print(f"  Τελευταία ενημέρωση: {self.last_update.strftime('%H:%M:%S')}")
        print(f"{'='*70}\n")

        # Group hospitals by specialty
        by_specialty: Dict[str, List[Hospital]] = {}
        for hospital in self.hospitals:
            if hospital.specialty not in by_specialty:
                by_specialty[hospital.specialty] = []
            by_specialty[hospital.specialty].append(hospital)

        # Display grouped hospitals
        for specialty, hospitals in sorted(by_specialty.items()):
            print(f"\n┌─ {specialty} {'─' * (65 - len(specialty))}")
            for i, hospital in enumerate(hospitals, 1):
                print(f"│")
                print(f"│  {i}. {hospital.name}")
                if hospital.time_slot:
                    print(f"│     🕐 Ωράριο: {hospital.time_slot}")
                if hospital.address:
                    print(f"│     📍 {hospital.address}")
                if hospital.phone:
                    print(f"│     📞 {hospital.phone}")
                if hospital.area:
                    print(f"│     🏘️  {hospital.area}")
            print(f"└{'─' * 68}")

        print(f"\n{'='*70}\n")

    def search_by_specialty(self, specialty_keyword: str) -> List[Hospital]:
        """Search hospitals by specialty keyword"""
        return [
            h for h in self.hospitals
            if specialty_keyword.lower() in h.specialty.lower()
        ]

    def search_by_area(self, area_keyword: str) -> List[Hospital]:
        """Search hospitals by area"""
        return [
            h for h in self.hospitals
            if area_keyword.lower() in h.area.lower()
        ]

    def save_to_json(self, filename: str = "hospitals_on_duty.json"):
        """Save current hospital data to JSON file"""
        data = {
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'hospitals': [asdict(h) for h in self.hospitals]
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✓ Δεδομένα αποθηκεύτηκαν στο {filename}")


def main():
    """Main function to run the hospital display service"""
    service = AthensHospitalService()

    # Initial data fetch and display
    service.update_data()
    service.display_hospitals()

    # Save to JSON file
    service.save_to_json()

    # Schedule daily update at 08:00
    schedule.every().day.at("08:00").do(service.update_data)
    schedule.every().day.at("08:00").do(service.display_hospitals)
    schedule.every().day.at("08:00").do(service.save_to_json)

    print("\n🕐 Υπηρεσία ξεκίνησε - θα ενημερώνεται καθημερινά στις 08:00")
    print("   Πατήστε Ctrl+C για έξοδο\n")

    # Keep the program running and check schedule
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n\n✓ Η υπηρεσία τερματίστηκε")


if __name__ == "__main__":
    main()
