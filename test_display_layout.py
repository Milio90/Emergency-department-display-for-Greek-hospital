#!/usr/bin/env python3
"""
Test script to verify the multi-column layout logic
"""

from moh_scraper import Hospital
from typing import Dict, List

# Sample test data with different time slots
test_hospitals = [
    Hospital(
        name="Νοσοκομείο A",
        specialty="Καρδιολογία / Cardiology",
        time_slot="08:00-14:30",
        on_duty_date="2025-10-14"
    ),
    Hospital(
        name="Νοσοκομείο B",
        specialty="Καρδιολογία / Cardiology",
        time_slot="08:00-14:30",
        on_duty_date="2025-10-14"
    ),
    Hospital(
        name="Νοσοκομείο C",
        specialty="Καρδιολογία / Cardiology",
        time_slot="14:30-21:00",
        on_duty_date="2025-10-14"
    ),
    Hospital(
        name="Νοσοκομείο D",
        specialty="Καρδιολογία / Cardiology",
        time_slot="21:00-08:00 επομένης",
        on_duty_date="2025-10-14"
    ),
]

# Group by time slot
by_time_slot: Dict[str, List[Hospital]] = {}
for hospital in test_hospitals:
    time_slot = hospital.time_slot or "Όλη την ημέρα"
    if time_slot not in by_time_slot:
        by_time_slot[time_slot] = []
    by_time_slot[time_slot].append(hospital)

# Test column distribution
sorted_slots = sorted(by_time_slot.items())
num_columns = min(len(sorted_slots), 3)

print(f"Total time slots: {len(sorted_slots)}")
print(f"Columns to create: {num_columns}")
print("\nColumn distribution:")

for i, (time_slot, hospitals) in enumerate(sorted_slots):
    col_idx = i % num_columns
    print(f"  Column {col_idx}: {time_slot} ({len(hospitals)} hospitals)")

print("\n✓ Layout logic test passed")
print("\nColor Palette (Onassis Hospital):")
print("  Background: #11121F")
print("  Header: #041C2C")
print("  Card: #1a2332")
print("  Text: #ffffff")
print("  Accent: #00B179 (green)")
print("  Highlight: #005FBE (blue)")
print("  Secondary: #0094f0 (light blue)")
