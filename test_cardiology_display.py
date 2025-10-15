#!/usr/bin/env python3
"""
Test script for cardiology display - verifies data loading without GUI
"""

from moh_scraper import MOHHospitalScraper
from datetime import datetime

def test_cardiology_data():
    """Test fetching cardiology hospital data"""
    print("\n" + "="*60)
    print("Testing Cardiology Display Data")
    print("="*60 + "\n")

    scraper = MOHHospitalScraper()

    print("Fetching today's hospital schedule...")
    all_hospitals = scraper.get_today_schedule()

    print(f"Total hospitals found: {len(all_hospitals)}\n")

    # Filter for cardiology
    cardiology_hospitals = [
        h for h in all_hospitals
        if "καρδιολογ" in h.specialty.lower() or "cardio" in h.specialty.lower()
    ]

    print(f"Cardiology hospitals found: {len(cardiology_hospitals)}\n")

    if cardiology_hospitals:
        print("=" * 60)
        print("CARDIOLOGY HOSPITALS ON DUTY")
        print("=" * 60 + "\n")

        for i, hospital in enumerate(cardiology_hospitals, 1):
            print(f"{i}. {hospital.name}")
            print(f"   Time slot: {hospital.time_slot}")
            if hospital.address:
                print(f"   Address: {hospital.address}")
            if hospital.phone:
                print(f"   Phone: {hospital.phone}")
            if hospital.area:
                print(f"   Area: {hospital.area}")
            print()

        print("=" * 60)
        print("✓ Test successful - cardiology data ready for display")
        print("=" * 60)
    else:
        print("⚠️  No cardiology hospitals found in today's schedule")
        print("    This might be because:")
        print("    - The MOH website is not accessible")
        print("    - No cardiology hospitals are on duty today")
        print("    - The scraper needs to be updated")

if __name__ == "__main__":
    test_cardiology_data()
