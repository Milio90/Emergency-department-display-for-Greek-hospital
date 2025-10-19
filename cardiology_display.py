#!/usr/bin/env python3
"""
Hospitals On-Duty Display
GUI application for displaying hospitals on duty by specialty
Designed for Emergency Department monitors at Onassis Hospital
"""

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter.simpledialog import Dialog
from tkcalendar import Calendar
from PIL import Image, ImageTk
from datetime import datetime, date, timedelta
import json
import os
import unicodedata
from typing import List, Dict, Optional
from moh_scraper import MOHHospitalScraper, Hospital
from shift_parser import ShiftParser, DailyShift


class HospitalDisplayGUI:
    """GUI application for displaying on-duty hospitals by specialty"""

    @staticmethod
    def remove_accents(text: str) -> str:
        """Remove accent marks from Greek text"""
        # Normalize to NFD (decomposed form) where accents are separate
        nfd = unicodedata.normalize('NFD', text)
        # Filter out combining characters (accents)
        return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')

    def __init__(self, root):
        self.root = root
        self.root.title("Νοσοκομεία Εφημερίας")

        # Make window fullscreen
        self.root.attributes('-fullscreen', True)

        # Allow ESC key to exit fullscreen (for testing)
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        self.root.bind('<F11>', lambda e: self.root.attributes('-fullscreen', True))

        # Set background color - Light theme
        self.bg_color = "#FFFFFF"  # White background
        self.header_color = "#F5F7FA"  # Light gray for header
        self.card_color = "#F8F9FA"  # Light gray for cards
        self.text_color = "#212529"  # Dark text for readability
        self.accent_color = "#00B179"  # Green accent (Onassis)
        self.highlight_color = "#005FBE"  # Primary blue (Onassis)
        self.secondary_blue = "#0094f0"  # Lighter blue accent

        self.root.configure(bg=self.bg_color)

        # Initialize scraper
        self.scraper = MOHHospitalScraper()
        self.all_hospitals: List[Hospital] = []
        self.filtered_hospitals: List[Hospital] = []
        self.selected_specialty = "Καρδιολογία"  # Default specialty
        self.available_specialties: List[str] = []

        # Shift management
        self.shift_parser: Optional[ShiftParser] = None
        self.current_shift: Optional[DailyShift] = None
        self.shift_cache_file = "shifts_cache.json"

        # Date navigation
        self.selected_date = date.today()

        # Create UI
        self.create_ui()

        # Load or prompt for shift file
        self.load_or_prompt_shift_file()

        # Initial data fetch
        self.refresh_data()

        # Schedule daily refresh at 08:00
        self.schedule_daily_refresh()

    def create_ui(self):
        """Create the user interface"""

        # Header frame
        header_frame = tk.Frame(self.root, bg=self.header_color, height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)

        # Load and display logo in upper left corner
        try:
            logo_path = os.path.join(os.path.dirname(__file__), "onasseio_logo.png")
            logo_image = Image.open(logo_path)
            # Resize logo to fit in header (max height 70px to leave margin)
            logo_height = 70
            aspect_ratio = logo_image.width / logo_image.height
            logo_width = int(logo_height * aspect_ratio)
            logo_image = logo_image.resize((logo_width, logo_height), Image.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)

            logo_label = tk.Label(
                header_frame,
                image=self.logo_photo,
                bg=self.header_color
            )
            logo_label.pack(side=tk.LEFT, padx=10, pady=5)
        except Exception as e:
            print(f"⚠ Αδυναμία φόρτωσης λογότυπου: {e}")

        # Title
        title_font = tkfont.Font(family="Arial", size=24, weight="bold")
        self.title_label = tk.Label(
            header_frame,
            text="ΝΟΣΟΚΟΜΕΙΑ ΕΦΗΜΕΡΙΑΣ - ΚΑΡΔΙΟΛΟΓΙΑ",
            font=title_font,
            bg=self.header_color,
            fg=self.highlight_color
        )
        self.title_label.pack(pady=5)


        # Specialty selector and date/time frame
        control_frame = tk.Frame(self.root, bg=self.bg_color, height=50)
        control_frame.pack(fill=tk.X, padx=20, pady=5)

        # Left side: Date navigation controls
        date_nav_frame = tk.Frame(control_frame, bg=self.bg_color)
        date_nav_frame.pack(side=tk.LEFT)

        # Previous day button
        prev_btn = tk.Button(
            date_nav_frame,
            text="◄ Προηγούμενη",
            command=self.previous_day,
            bg=self.highlight_color,
            fg="white",
            font=tkfont.Font(family="Arial", size=10),
            relief=tk.FLAT,
            padx=10,
            pady=5
        )
        prev_btn.pack(side=tk.LEFT, padx=2)

        # Calendar button
        cal_btn = tk.Button(
            date_nav_frame,
            text="📅 Επιλογή Ημερομηνίας",
            command=self.open_calendar,
            bg=self.secondary_blue,
            fg="white",
            font=tkfont.Font(family="Arial", size=10),
            relief=tk.FLAT,
            padx=10,
            pady=5
        )
        cal_btn.pack(side=tk.LEFT, padx=2)

        # Next day button
        next_btn = tk.Button(
            date_nav_frame,
            text="Επόμενη ►",
            command=self.next_day,
            bg=self.highlight_color,
            fg="white",
            font=tkfont.Font(family="Arial", size=10),
            relief=tk.FLAT,
            padx=10,
            pady=5
        )
        next_btn.pack(side=tk.LEFT, padx=2)

        # Selected date display
        datetime_font = tkfont.Font(family="Arial", size=12, weight="bold")
        self.datetime_label = tk.Label(
            date_nav_frame,
            font=datetime_font,
            bg=self.bg_color,
            fg=self.text_color
        )
        self.datetime_label.pack(side=tk.LEFT, padx=15)

        # Right side: Specialty selector
        selector_frame = tk.Frame(control_frame, bg=self.bg_color)
        selector_frame.pack(side=tk.RIGHT, padx=10)

        selector_label = tk.Label(
            selector_frame,
            text="Ειδικότητα:",
            font=tkfont.Font(family="Arial", size=12),
            bg=self.bg_color,
            fg=self.text_color
        )
        selector_label.pack(side=tk.LEFT, padx=(0, 10))

        # Style for combobox
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Custom.TCombobox',
                       fieldbackground=self.card_color,
                       background=self.card_color,
                       foreground=self.text_color,
                       arrowcolor=self.highlight_color,
                       borderwidth=2,
                       relief='raised')

        self.specialty_var = tk.StringVar(value=self.selected_specialty)
        self.specialty_combo = ttk.Combobox(
            selector_frame,
            textvariable=self.specialty_var,
            font=tkfont.Font(family="Arial", size=12),
            width=30,
            state='readonly',
            style='Custom.TCombobox'
        )
        self.specialty_combo.pack(side=tk.LEFT)
        self.specialty_combo.bind('<<ComboboxSelected>>', self.on_specialty_changed)

        # Last update label (below specialty selector)
        update_frame = tk.Frame(self.root, bg=self.bg_color)
        update_frame.pack(fill=tk.X, padx=20, pady=(0, 5))

        self.update_label = tk.Label(
            update_frame,
            font=tkfont.Font(family="Arial", size=10),
            bg=self.bg_color,
            fg="#6C757D"  # Medium gray for subtle text
        )
        self.update_label.pack(side=tk.RIGHT, padx=20)

        # Main content frame with scrollbar
        content_container = tk.Frame(self.root, bg=self.bg_color)
        content_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 0))

        # Canvas for scrolling
        self.canvas = tk.Canvas(content_container, bg=self.bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(content_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg_color)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Enable mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        # Shift display section at bottom
        self.create_shift_section()


    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        if event.num == 5 or event.delta == -120:
            self.canvas.yview_scroll(1, "units")
        if event.num == 4 or event.delta == 120:
            self.canvas.yview_scroll(-1, "units")

    def update_datetime(self):
        """Update date display to show selected date"""
        # Greek day names
        greek_days = {
            0: "Δευτέρα",
            1: "Τρίτη",
            2: "Τετάρτη",
            3: "Πέμπτη",
            4: "Παρασκευή",
            5: "Σάββατο",
            6: "Κυριακή"
        }

        # Greek month names
        greek_months = {
            1: "Ιανουαρίου", 2: "Φεβρουαρίου", 3: "Μαρτίου",
            4: "Απριλίου", 5: "Μαΐου", 6: "Ιουνίου",
            7: "Ιουλίου", 8: "Αυγούστου", 9: "Σεπτεμβρίου",
            10: "Οκτωβρίου", 11: "Νοεμβρίου", 12: "Δεκεμβρίου"
        }

        day_name = greek_days[self.selected_date.weekday()]
        month_name = greek_months[self.selected_date.month]

        # Show if selected date is today
        today = date.today()
        if self.selected_date == today:
            date_str = f"{day_name}, {self.selected_date.day} {month_name} {self.selected_date.year} (Σήμερα)"
        else:
            date_str = f"{day_name}, {self.selected_date.day} {month_name} {self.selected_date.year}"

        self.datetime_label.config(text=date_str)

    def refresh_data(self):
        """Fetch and display fresh hospital data for the selected date"""
        print(f"\n{'='*60}")
        print(f"Ανανέωση δεδομένων νοσοκομείων...")
        print(f"Ημερομηνία: {self.selected_date.strftime('%Y-%m-%d')}")
        print(f"Ώρα: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        try:
            # Fetch schedule for selected date
            self.all_hospitals = self.scraper.get_schedule_for_date(self.selected_date)

            print(f"✓ Βρέθηκαν {len(self.all_hospitals)} νοσοκομεία εφημερίας")

            # Extract unique specialties
            self.extract_specialties()

            # Filter for selected specialty
            self.filter_by_specialty()

        except Exception as e:
            print(f"✗ Σφάλμα λήψης δεδομένων: {e}")
            # Try to load from cached JSON
            self.load_from_cache()

        # Update display
        self.display_hospitals()
        self.update_datetime()
        self.update_shift_display()

        # Update last refresh time
        self.update_label.config(
            text=f"Τελευταία ενημέρωση: {datetime.now().strftime('%H:%M')}"
        )

    def extract_specialties(self):
        """Extract unique specialties from hospital data and populate dropdown"""
        specialty_set = set()
        for hospital in self.all_hospitals:
            # Extract only Greek part of specialty (before " / ")
            specialty_greek = hospital.specialty.split(" / ")[0].strip()
            specialty_set.add(specialty_greek)

        self.available_specialties = sorted(list(specialty_set))

        # Add "Όλες οι ειδικότητες" option at the beginning
        self.available_specialties.insert(0, "Όλες οι ειδικότητες")

        # Update combobox values
        self.specialty_combo['values'] = self.available_specialties

        # Set default to Cardiology if available (always prioritize cardiology)
        cardiology_options = [s for s in self.available_specialties if "καρδιολογ" in s.lower()]
        if cardiology_options:
            self.selected_specialty = cardiology_options[0]
            self.specialty_var.set(self.selected_specialty)
        elif len(self.available_specialties) > 1:
            # If no cardiology, default to first real specialty (skip "Όλες")
            self.selected_specialty = self.available_specialties[1]
            self.specialty_var.set(self.selected_specialty)

    def filter_by_specialty(self):
        """Filter hospitals by selected specialty"""
        if self.selected_specialty == "Όλες οι ειδικότητες":
            self.filtered_hospitals = self.all_hospitals
        else:
            # Filter by matching Greek specialty name (which is at the beginning of the specialty string)
            self.filtered_hospitals = [
                h for h in self.all_hospitals
                if h.specialty.startswith(self.selected_specialty)
            ]

        print(f"  Φιλτράρισμα για: {self.selected_specialty}")
        print(f"  Βρέθηκαν {len(self.filtered_hospitals)} νοσοκομεία")

        # Update title
        if self.selected_specialty == "Όλες οι ειδικότητες":
            title_text = "ΝΟΣΟΚΟΜΕΙΑ ΕΦΗΜΕΡΙΑΣ"
        else:
            specialty_upper = self.remove_accents(self.selected_specialty.upper())
            title_text = f"ΝΟΣΟΚΟΜΕΙΑ ΕΦΗΜΕΡΙΑΣ - {specialty_upper}"
        self.title_label.config(text=title_text)

    def on_specialty_changed(self, event):
        """Handle specialty selection change"""
        self.selected_specialty = self.specialty_var.get()
        print(f"\nΑλλαγή ειδικότητας σε: {self.selected_specialty}")
        self.filter_by_specialty()
        self.display_hospitals()

    def load_from_cache(self):
        """Load hospital data from cached JSON file"""
        cache_file = "hospitals_on_duty.json"
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    hospitals_data = data.get('hospitals', [])

                    # Convert to Hospital objects
                    from dataclasses import dataclass
                    self.all_hospitals = []
                    for h_data in hospitals_data:
                        self.all_hospitals.append(Hospital(
                            name=h_data.get('name', ''),
                            specialty=h_data.get('specialty', ''),
                            time_slot=h_data.get('time_slot', ''),
                            on_duty_date=h_data.get('on_duty_date', ''),
                            address=h_data.get('address', ''),
                            phone=h_data.get('phone', ''),
                            area=h_data.get('area', '')
                        ))

                    print(f"✓ Φορτώθηκαν {len(self.all_hospitals)} νοσοκομεία από την προσωρινή μνήμη")

                    # Extract specialties and filter
                    self.extract_specialties()
                    self.filter_by_specialty()

            except Exception as e:
                print(f"✗ Σφάλμα φόρτωσης προσωρινής μνήμης: {e}")
                self.all_hospitals = []
                self.filtered_hospitals = []

    def display_hospitals(self):
        """Display hospital cards in the GUI - all time slots in one screen"""
        # Clear existing content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.filtered_hospitals:
            # No data available
            no_data_label = tk.Label(
                self.scrollable_frame,
                text="Δεν υπάρχουν διαθέσιμα δεδομένα",
                font=tkfont.Font(family="Arial", size=16),
                bg=self.bg_color,
                fg="#ADB5BD",  # Light gray for no-data state
                pady=50
            )
            no_data_label.pack(fill=tk.BOTH, expand=True)
            return

        # Group by time slot
        by_time_slot: Dict[str, List[Hospital]] = {}
        for hospital in self.filtered_hospitals:
            time_slot = hospital.time_slot or "Όλη την ημέρα"
            if time_slot not in by_time_slot:
                by_time_slot[time_slot] = []
            by_time_slot[time_slot].append(hospital)

        # Create grid layout to show all time slots side by side
        sorted_slots = sorted(by_time_slot.items())
        num_columns = min(len(sorted_slots), 3)  # Max 3 columns for readability

        # Create column frames
        columns = []
        for col_idx in range(num_columns):
            col_frame = tk.Frame(self.scrollable_frame, bg=self.bg_color)
            col_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            columns.append(col_frame)

        # Distribute time slots across columns
        for i, (time_slot, hospitals) in enumerate(sorted_slots):
            col_idx = i % num_columns
            column = columns[col_idx]

            # Time slot header
            slot_header = tk.Frame(column, bg=self.bg_color)
            slot_header.pack(fill=tk.X, pady=(10 if i >= num_columns else 0, 5))

            time_slot_label = tk.Label(
                slot_header,
                text=f"🕐 {time_slot}",
                font=tkfont.Font(family="Arial", size=14, weight="bold"),
                bg=self.bg_color,
                fg=self.highlight_color,
                anchor="w"
            )
            time_slot_label.pack(fill=tk.X, padx=5)

            # Hospital cards
            for hospital in hospitals:
                self.create_hospital_card(hospital, column)

    def create_hospital_card(self, hospital: Hospital, parent=None):
        """Create a card widget for a hospital"""
        if parent is None:
            parent = self.scrollable_frame

        # Card frame with Onassis-style border
        card = tk.Frame(
            parent,
            bg=self.highlight_color,  # Blue border
            relief=tk.FLAT,
            borderwidth=0
        )
        card.pack(fill=tk.X, padx=5, pady=3)

        # Inner card with padding for border effect
        inner_card = tk.Frame(
            card,
            bg=self.card_color
        )
        inner_card.pack(fill=tk.BOTH, padx=1, pady=1)

        # Inner padding frame
        inner = tk.Frame(inner_card, bg=self.card_color)
        inner.pack(fill=tk.BOTH, padx=8, pady=8)

        # Hospital name
        name_label = tk.Label(
            inner,
            text=hospital.name,
            font=tkfont.Font(family="Arial", size=11, weight="bold"),
            bg=self.card_color,
            fg=self.text_color,
            anchor="w",
            wraplength=400,
            justify=tk.LEFT
        )
        name_label.pack(fill=tk.X, pady=(0, 5))

        # Info frame for details
        info_frame = tk.Frame(inner, bg=self.card_color)
        info_frame.pack(fill=tk.X)

        detail_font = tkfont.Font(family="Arial", size=9)

        # Address
        if hospital.address:
            addr_label = tk.Label(
                info_frame,
                text=f"📍 {hospital.address}",
                font=detail_font,
                bg=self.card_color,
                fg="#495057",  # Darker gray for secondary text
                anchor="w"
            )
            addr_label.pack(fill=tk.X, pady=2)

        # Phone
        if hospital.phone:
            phone_label = tk.Label(
                info_frame,
                text=f"📞 {hospital.phone}",
                font=detail_font,
                bg=self.card_color,
                fg="#495057",  # Darker gray for secondary text
                anchor="w"
            )
            phone_label.pack(fill=tk.X, pady=2)

        # Area
        if hospital.area:
            area_label = tk.Label(
                info_frame,
                text=f"🏘️  {hospital.area}",
                font=detail_font,
                bg=self.card_color,
                fg="#495057",  # Darker gray for secondary text
                anchor="w"
            )
            area_label.pack(fill=tk.X, pady=2)

    def create_shift_section(self):
        """Create the shift display section at the bottom of the window"""
        # Separator line
        separator = tk.Frame(self.root, height=2, bg=self.highlight_color)
        separator.pack(fill=tk.X, padx=10, pady=(0, 5))

        # Shift section frame - increased height to show all shifts
        self.shift_frame = tk.Frame(self.root, bg=self.card_color, height=200)
        self.shift_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.shift_frame.pack_propagate(False)

        # Title row with file management button
        title_row = tk.Frame(self.shift_frame, bg=self.card_color)
        title_row.pack(fill=tk.X, padx=10, pady=5)

        self.shift_title = tk.Label(
            title_row,
            text="ΕΦΗΜΕΡΙΕΣ ΚΑΡΔΙΟΛΟΓΙΚΟΥ ΤΟΜΕΑ",
            font=tkfont.Font(family="Arial", size=14, weight="bold"),
            bg=self.card_color,
            fg=self.highlight_color
        )
        self.shift_title.pack(side=tk.LEFT)

        # Buttons frame
        buttons_frame = tk.Frame(title_row, bg=self.card_color)
        buttons_frame.pack(side=tk.RIGHT)

        # Load file button
        load_btn = tk.Button(
            buttons_frame,
            text="Φόρτωση Αρχείου",
            command=self.load_shift_file,
            bg=self.highlight_color,
            fg="white",
            font=tkfont.Font(family="Arial", size=10),
            relief=tk.FLAT,
            padx=10,
            pady=5
        )
        load_btn.pack(side=tk.LEFT, padx=5)

        # Edit button
        edit_btn = tk.Button(
            buttons_frame,
            text="Επεξεργασία",
            command=self.edit_shifts,
            bg=self.secondary_blue,
            fg="white",
            font=tkfont.Font(family="Arial", size=10),
            relief=tk.FLAT,
            padx=10,
            pady=5
        )
        edit_btn.pack(side=tk.LEFT, padx=5)

        # Shift details container
        self.shift_details_frame = tk.Frame(self.shift_frame, bg=self.card_color)
        self.shift_details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def load_or_prompt_shift_file(self):
        """Load shifts from cache or prompt user to select a file"""
        # Try to load from cache first
        parser = ShiftParser.load_from_json(self.shift_cache_file)

        if parser:
            # Check if cached data is for current month
            today = date.today()
            if parser.validate_month_year(today.month, today.year):
                self.shift_parser = parser
                self.update_shift_display()
                print("✓ Εφημερίες φορτώθηκαν από την προσωρινή μνήμη")
                return
            else:
                print(f"⚠ Οι αποθηκευμένες εφημερίες είναι για {parser.month_number}/{parser.year}")

        # Prompt user after GUI is ready
        self.root.after(1000, self.prompt_for_shift_file)

    def prompt_for_shift_file(self):
        """Prompt user to select a shift file"""
        today = date.today()
        greek_months_gen = {
            1: "Ιανουάριο", 2: "Φεβρουάριο", 3: "Μάρτιο",
            4: "Απρίλιο", 5: "Μάιο", 6: "Ιούνιο",
            7: "Ιούλιο", 8: "Αύγουστο", 9: "Σεπτέμβριο",
            10: "Οκτώβριο", 11: "Νοέμβριο", 12: "Δεκέμβριο"
        }

        response = messagebox.askyesno(
            "Φόρτωση Εφημεριών",
            f"Θέλετε να φορτώσετε το αρχείο εφημεριών για {greek_months_gen[today.month]} {today.year};\n\n"
            "Χωρίς αυτό το αρχείο, δεν θα εμφανίζονται οι εφημερίες γιατρών."
        )

        if response:
            self.load_shift_file()

    def load_shift_file(self):
        """Load shift schedule from DOCX file"""
        filepath = filedialog.askopenfilename(
            title="Επιλέξτε αρχείο εφημεριών",
            filetypes=[
                ("Word Documents", "*.docx"),
                ("All Files", "*.*")
            ],
            initialdir=os.path.expanduser("~/Έγγραφα")
        )

        if not filepath:
            return

        # Parse the file
        parser = ShiftParser(filepath)
        if not parser.parse():
            messagebox.showerror(
                "Σφάλμα",
                "Αδυναμία ανάλυσης του αρχείου εφημεριών.\n"
                "Παρακαλώ βεβαιωθείτε ότι το αρχείο έχει τη σωστή δομή."
            )
            return

        # Validate month and year
        today = date.today()
        if not parser.validate_month_year(today.month, today.year):
            greek_months = {
                1: "Ιανουάριος", 2: "Φεβρουάριος", 3: "Μάρτιος",
                4: "Απρίλιος", 5: "Μάιος", 6: "Ιούνιος",
                7: "Ιούλιος", 8: "Αύγουστος", 9: "Σεπτέμβριος",
                10: "Οκτώβριος", 11: "Νοέμβριος", 12: "Δεκέμβριος"
            }

            response = messagebox.askyesno(
                "Προειδοποίηση",
                f"Το αρχείο περιέχει εφημερίες για {greek_months[parser.month_number]} {parser.year}\n"
                f"αλλά είμαστε στον {greek_months[today.month]} {today.year}.\n\n"
                "Θέλετε να συνεχίσετε;"
            )

            if not response:
                return

        # Save to cache
        parser.save_to_json(self.shift_cache_file)

        # Update display
        self.shift_parser = parser
        self.update_shift_display()

        messagebox.showinfo(
            "Επιτυχία",
            f"Φορτώθηκαν εφημερίες για {parser.month_number}/{parser.year}\n"
            f"Σύνολο: {len(parser.shifts)} ημέρες"
        )

    def update_shift_display(self):
        """Update the shift display with information for the selected date"""
        # Clear existing content
        for widget in self.shift_details_frame.winfo_children():
            widget.destroy()

        if not self.shift_parser:
            # No shift data available
            no_data = tk.Label(
                self.shift_details_frame,
                text="Δεν έχουν φορτωθεί εφημερίες. Πατήστε 'Φόρτωση Αρχείου' για να επιλέξετε αρχείο.",
                font=tkfont.Font(family="Arial", size=11),
                bg=self.card_color,
                fg="#6C757D"
            )
            no_data.pack(expand=True)
            return

        # Get shift for selected date
        self.current_shift = self.shift_parser.get_shift_for_date(self.selected_date)

        if not self.current_shift:
            # No shift for selected date
            no_shift = tk.Label(
                self.shift_details_frame,
                text=f"Δεν βρέθηκαν εφημερίες για {self.selected_date.day}/{self.selected_date.month}/{self.selected_date.year}",
                font=tkfont.Font(family="Arial", size=11),
                bg=self.card_color,
                fg="#6C757D"
            )
            no_shift.pack(expand=True)
            return

        # Create grid layout for shift information
        grid_frame = tk.Frame(self.shift_details_frame, bg=self.card_color)
        grid_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        row = 0
        label_font = tkfont.Font(family="Arial", size=12, weight="bold")
        value_font = tkfont.Font(family="Arial", size=12)

        # Attending cardiologists
        tk.Label(
            grid_frame,
            text="Επιμελητές:",
            font=label_font,
            bg=self.card_color,
            fg=self.text_color,
            anchor="w"
        ).grid(row=row, column=0, sticky="w", padx=10, pady=3)

        attending_text = ", ".join(self.current_shift.attendings) if self.current_shift.attendings else "Κανένας"
        tk.Label(
            grid_frame,
            text=attending_text,
            font=value_font,
            bg=self.card_color,
            fg=self.text_color,
            anchor="w"
        ).grid(row=row, column=1, sticky="w", padx=10, pady=3)

        row += 1

        # Major shift (24h)
        if self.current_shift.major_shift:
            tk.Label(
                grid_frame,
                text="Μεγάλη Εφημερία (24ωρη):",
                font=label_font,
                bg=self.card_color,
                fg=self.text_color,
                anchor="w"
            ).grid(row=row, column=0, sticky="w", padx=10, pady=3)

            tk.Label(
                grid_frame,
                text=self.current_shift.major_shift,
                font=value_font,
                bg=self.card_color,
                fg=self.text_color,
                anchor="w"
            ).grid(row=row, column=1, sticky="w", padx=10, pady=3)

            row += 1

        # Minor shift (24h)
        if self.current_shift.minor_shift:
            tk.Label(
                grid_frame,
                text="Μικρή Εφημερία (24ωρη):",
                font=label_font,
                bg=self.card_color,
                fg=self.text_color,
                anchor="w"
            ).grid(row=row, column=0, sticky="w", padx=10, pady=3)

            tk.Label(
                grid_frame,
                text=self.current_shift.minor_shift,
                font=value_font,
                bg=self.card_color,
                fg=self.text_color,
                anchor="w"
            ).grid(row=row, column=1, sticky="w", padx=10, pady=3)

            row += 1

        # TEP cardiologist (12h)
        if self.current_shift.tep_cardiologist:
            tk.Label(
                grid_frame,
                text="Καρδιολόγος ΤΕΠ (12ωρη):",
                font=label_font,
                bg=self.card_color,
                fg=self.text_color,
                anchor="w"
            ).grid(row=row, column=0, sticky="w", padx=10, pady=3)

            tk.Label(
                grid_frame,
                text=self.current_shift.tep_cardiologist,
                font=value_font,
                bg=self.card_color,
                fg=self.text_color,
                anchor="w"
            ).grid(row=row, column=1, sticky="w", padx=10, pady=3)

            row += 1

        # Cardiac Surgeon 1
        if self.current_shift.senior_cardiac_surgeon:
            tk.Label(
                grid_frame,
                text="Καρδιοχειρουργός 1:",
                font=label_font,
                bg=self.card_color,
                fg=self.text_color,
                anchor="w"
            ).grid(row=row, column=0, sticky="w", padx=10, pady=3)

            tk.Label(
                grid_frame,
                text=self.current_shift.senior_cardiac_surgeon,
                font=value_font,
                bg=self.card_color,
                fg=self.text_color,
                anchor="w"
            ).grid(row=row, column=1, sticky="w", padx=10, pady=3)

            row += 1

        # Cardiac Surgeon 2
        if self.current_shift.junior_cardiac_surgeon:
            tk.Label(
                grid_frame,
                text="Καρδιοχειρουργός 2:",
                font=label_font,
                bg=self.card_color,
                fg=self.text_color,
                anchor="w"
            ).grid(row=row, column=0, sticky="w", padx=10, pady=3)

            tk.Label(
                grid_frame,
                text=self.current_shift.junior_cardiac_surgeon,
                font=value_font,
                bg=self.card_color,
                fg=self.text_color,
                anchor="w"
            ).grid(row=row, column=1, sticky="w", padx=10, pady=3)

            row += 1

        # Anesthesiologist 1
        if self.current_shift.anesthesiologist_1:
            tk.Label(
                grid_frame,
                text="Αναισθησιολόγος 1:",
                font=label_font,
                bg=self.card_color,
                fg=self.text_color,
                anchor="w"
            ).grid(row=row, column=0, sticky="w", padx=10, pady=3)

            tk.Label(
                grid_frame,
                text=self.current_shift.anesthesiologist_1,
                font=value_font,
                bg=self.card_color,
                fg=self.text_color,
                anchor="w"
            ).grid(row=row, column=1, sticky="w", padx=10, pady=3)

            row += 1

        # Anesthesiologist 2
        if self.current_shift.anesthesiologist_2:
            tk.Label(
                grid_frame,
                text="Αναισθησιολόγος 2:",
                font=label_font,
                bg=self.card_color,
                fg=self.text_color,
                anchor="w"
            ).grid(row=row, column=0, sticky="w", padx=10, pady=3)

            tk.Label(
                grid_frame,
                text=self.current_shift.anesthesiologist_2,
                font=value_font,
                bg=self.card_color,
                fg=self.text_color,
                anchor="w"
            ).grid(row=row, column=1, sticky="w", padx=10, pady=3)

            row += 1

        # Pediatric Cardiologist
        if self.current_shift.pediatric_cardiologist:
            tk.Label(
                grid_frame,
                text="Παιδοκαρδιολόγος:",
                font=label_font,
                bg=self.card_color,
                fg=self.text_color,
                anchor="w"
            ).grid(row=row, column=0, sticky="w", padx=10, pady=3)

            tk.Label(
                grid_frame,
                text=self.current_shift.pediatric_cardiologist,
                font=value_font,
                bg=self.card_color,
                fg=self.text_color,
                anchor="w"
            ).grid(row=row, column=1, sticky="w", padx=10, pady=3)

    def previous_day(self):
        """Navigate to previous day"""
        self.selected_date = self.selected_date - timedelta(days=1)
        print(f"\n← Μετάβαση στην προηγούμενη ημέρα: {self.selected_date.strftime('%Y-%m-%d')}")
        self.refresh_data()

    def next_day(self):
        """Navigate to next day"""
        self.selected_date = self.selected_date + timedelta(days=1)
        print(f"\n→ Μετάβαση στην επόμενη ημέρα: {self.selected_date.strftime('%Y-%m-%d')}")
        self.refresh_data()

    def open_calendar(self):
        """Open calendar dialog to select a date"""
        # Create calendar dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Επιλογή Ημερομηνίας")
        dialog.geometry("350x350")
        dialog.configure(bg=self.bg_color)

        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()

        # Title
        title = tk.Label(
            dialog,
            text="Επιλέξτε Ημερομηνία",
            font=tkfont.Font(family="Arial", size=14, weight="bold"),
            bg=self.bg_color,
            fg=self.highlight_color
        )
        title.pack(pady=10)

        # Calendar widget
        cal = Calendar(
            dialog,
            selectmode='day',
            year=self.selected_date.year,
            month=self.selected_date.month,
            day=self.selected_date.day,
            date_pattern='y-mm-dd',
            background=self.highlight_color,
            foreground='white',
            selectbackground=self.accent_color,
            selectforeground='white',
            headersbackground=self.secondary_blue,
            headersforeground='white',
            bordercolor=self.highlight_color,
            normalbackground=self.card_color,
            normalforeground=self.text_color,
            weekendbackground=self.card_color,
            weekendforeground=self.text_color,
            othermonthbackground=self.bg_color,
            othermonthforeground='#ADB5BD'
        )
        cal.pack(pady=10, padx=20)

        # Buttons
        button_frame = tk.Frame(dialog, bg=self.bg_color)
        button_frame.pack(pady=10)

        def select_date():
            """Handle date selection"""
            selected = cal.get_date()
            # Parse the date string (format: yyyy-mm-dd)
            self.selected_date = datetime.strptime(selected, '%Y-%m-%d').date()
            print(f"\n📅 Επιλέχθηκε ημερομηνία: {self.selected_date.strftime('%Y-%m-%d')}")
            dialog.destroy()
            self.refresh_data()

        select_btn = tk.Button(
            button_frame,
            text="Επιλογή",
            command=select_date,
            bg=self.accent_color,
            fg="white",
            font=tkfont.Font(family="Arial", size=11),
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        select_btn.pack(side=tk.LEFT, padx=5)

        today_btn = tk.Button(
            button_frame,
            text="Σήμερα",
            command=lambda: self.select_today(dialog),
            bg=self.secondary_blue,
            fg="white",
            font=tkfont.Font(family="Arial", size=11),
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        today_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = tk.Button(
            button_frame,
            text="Ακύρωση",
            command=dialog.destroy,
            bg="#6C757D",
            fg="white",
            font=tkfont.Font(family="Arial", size=11),
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def select_today(self, dialog=None):
        """Select today's date"""
        self.selected_date = date.today()
        print(f"\n📅 Επιλέχθηκε σημερινή ημερομηνία: {self.selected_date.strftime('%Y-%m-%d')}")
        if dialog:
            dialog.destroy()
        self.refresh_data()

    def edit_shifts(self):
        """Open dialog to edit shift information for the selected date"""
        if not self.shift_parser:
            messagebox.showwarning(
                "Προειδοποίηση",
                "Δεν έχουν φορτωθεί εφημερίες. Παρακαλώ φορτώστε πρώτα το αρχείο."
            )
            return

        if not self.current_shift:
            messagebox.showwarning(
                "Προειδοποίηση",
                "Δεν υπάρχουν εφημερίες για σήμερα στο φορτωμένο αρχείο."
            )
            return

        # Create edit dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Επεξεργασία Εφημεριών")
        dialog.geometry("500x600")
        dialog.configure(bg=self.bg_color)

        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()

        # Title
        title = tk.Label(
            dialog,
            text=f"Επεξεργασία Εφημεριών - {self.current_shift.day} {self.current_shift.month_name}",
            font=tkfont.Font(family="Arial", size=14, weight="bold"),
            bg=self.bg_color,
            fg=self.highlight_color
        )
        title.pack(pady=10)

        # Form frame
        form_frame = tk.Frame(dialog, bg=self.bg_color)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        label_font = tkfont.Font(family="Arial", size=11)
        entry_font = tkfont.Font(family="Arial", size=11)

        # Attending cardiologists
        tk.Label(
            form_frame,
            text="Επιμελητές (διαχωρισμός με κόμμα):",
            font=label_font,
            bg=self.bg_color
        ).grid(row=0, column=0, sticky="w", pady=5)

        attending_var = tk.StringVar(value=", ".join(self.current_shift.attendings))
        attending_entry = tk.Entry(
            form_frame,
            textvariable=attending_var,
            font=entry_font,
            width=40
        )
        attending_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=(10, 0))

        # Major shift
        tk.Label(
            form_frame,
            text="Μεγάλη Εφημερία (24ωρη):",
            font=label_font,
            bg=self.bg_color
        ).grid(row=1, column=0, sticky="w", pady=5)

        major_var = tk.StringVar(value=self.current_shift.major_shift or "")
        major_entry = tk.Entry(
            form_frame,
            textvariable=major_var,
            font=entry_font,
            width=40
        )
        major_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=(10, 0))

        # Minor shift
        tk.Label(
            form_frame,
            text="Μικρή Εφημερία (24ωρη):",
            font=label_font,
            bg=self.bg_color
        ).grid(row=2, column=0, sticky="w", pady=5)

        minor_var = tk.StringVar(value=self.current_shift.minor_shift or "")
        minor_entry = tk.Entry(
            form_frame,
            textvariable=minor_var,
            font=entry_font,
            width=40
        )
        minor_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=(10, 0))

        # TEP cardiologist
        tk.Label(
            form_frame,
            text="Καρδιολόγος ΤΕΠ (12ωρη):",
            font=label_font,
            bg=self.bg_color
        ).grid(row=3, column=0, sticky="w", pady=5)

        tep_var = tk.StringVar(value=self.current_shift.tep_cardiologist or "")
        tep_entry = tk.Entry(
            form_frame,
            textvariable=tep_var,
            font=entry_font,
            width=40
        )
        tep_entry.grid(row=3, column=1, sticky="ew", pady=5, padx=(10, 0))

        # Cardiac Surgeon 1
        tk.Label(
            form_frame,
            text="Καρδιοχειρουργός 1:",
            font=label_font,
            bg=self.bg_color
        ).grid(row=4, column=0, sticky="w", pady=5)

        senior_surgeon_var = tk.StringVar(value=self.current_shift.senior_cardiac_surgeon or "")
        senior_surgeon_entry = tk.Entry(
            form_frame,
            textvariable=senior_surgeon_var,
            font=entry_font,
            width=40
        )
        senior_surgeon_entry.grid(row=4, column=1, sticky="ew", pady=5, padx=(10, 0))

        # Cardiac Surgeon 2
        tk.Label(
            form_frame,
            text="Καρδιοχειρουργός 2:",
            font=label_font,
            bg=self.bg_color
        ).grid(row=5, column=0, sticky="w", pady=5)

        junior_surgeon_var = tk.StringVar(value=self.current_shift.junior_cardiac_surgeon or "")
        junior_surgeon_entry = tk.Entry(
            form_frame,
            textvariable=junior_surgeon_var,
            font=entry_font,
            width=40
        )
        junior_surgeon_entry.grid(row=5, column=1, sticky="ew", pady=5, padx=(10, 0))

        # Anesthesiologist 1
        tk.Label(
            form_frame,
            text="Αναισθησιολόγος 1:",
            font=label_font,
            bg=self.bg_color
        ).grid(row=6, column=0, sticky="w", pady=5)

        anesthesiologist_1_var = tk.StringVar(value=self.current_shift.anesthesiologist_1 or "")
        anesthesiologist_1_entry = tk.Entry(
            form_frame,
            textvariable=anesthesiologist_1_var,
            font=entry_font,
            width=40
        )
        anesthesiologist_1_entry.grid(row=6, column=1, sticky="ew", pady=5, padx=(10, 0))

        # Anesthesiologist 2
        tk.Label(
            form_frame,
            text="Αναισθησιολόγος 2:",
            font=label_font,
            bg=self.bg_color
        ).grid(row=7, column=0, sticky="w", pady=5)

        anesthesiologist_2_var = tk.StringVar(value=self.current_shift.anesthesiologist_2 or "")
        anesthesiologist_2_entry = tk.Entry(
            form_frame,
            textvariable=anesthesiologist_2_var,
            font=entry_font,
            width=40
        )
        anesthesiologist_2_entry.grid(row=7, column=1, sticky="ew", pady=5, padx=(10, 0))

        # Pediatric Cardiologist
        tk.Label(
            form_frame,
            text="Παιδοκαρδιολόγος:",
            font=label_font,
            bg=self.bg_color
        ).grid(row=8, column=0, sticky="w", pady=5)

        pediatric_cardiologist_var = tk.StringVar(value=self.current_shift.pediatric_cardiologist or "")
        pediatric_cardiologist_entry = tk.Entry(
            form_frame,
            textvariable=pediatric_cardiologist_var,
            font=entry_font,
            width=40
        )
        pediatric_cardiologist_entry.grid(row=8, column=1, sticky="ew", pady=5, padx=(10, 0))

        form_frame.columnconfigure(1, weight=1)

        # Buttons
        button_frame = tk.Frame(dialog, bg=self.bg_color)
        button_frame.pack(pady=10)

        def save_changes():
            """Save the edited shifts"""
            # Update parser for selected date
            self.shift_parser.update_shift(self.selected_date.day, 'attendings', attending_var.get())
            self.shift_parser.update_shift(self.selected_date.day, 'major_shift', major_var.get())
            self.shift_parser.update_shift(self.selected_date.day, 'minor_shift', minor_var.get())
            self.shift_parser.update_shift(self.selected_date.day, 'tep_cardiologist', tep_var.get())
            self.shift_parser.update_shift(self.selected_date.day, 'senior_cardiac_surgeon', senior_surgeon_var.get())
            self.shift_parser.update_shift(self.selected_date.day, 'junior_cardiac_surgeon', junior_surgeon_var.get())
            self.shift_parser.update_shift(self.selected_date.day, 'anesthesiologist_1', anesthesiologist_1_var.get())
            self.shift_parser.update_shift(self.selected_date.day, 'anesthesiologist_2', anesthesiologist_2_var.get())
            self.shift_parser.update_shift(self.selected_date.day, 'pediatric_cardiologist', pediatric_cardiologist_var.get())

            # Save to cache
            self.shift_parser.save_to_json(self.shift_cache_file)

            # Refresh display
            self.update_shift_display()

            messagebox.showinfo("Επιτυχία", "Οι αλλαγές αποθηκεύτηκαν επιτυχώς!")
            dialog.destroy()

        save_btn = tk.Button(
            button_frame,
            text="Αποθήκευση",
            command=save_changes,
            bg=self.accent_color,
            fg="white",
            font=tkfont.Font(family="Arial", size=11),
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        save_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = tk.Button(
            button_frame,
            text="Ακύρωση",
            command=dialog.destroy,
            bg="#6C757D",
            fg="white",
            font=tkfont.Font(family="Arial", size=11),
            relief=tk.FLAT,
            padx=20,
            pady=8
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def schedule_daily_refresh(self):
        """Schedule daily refresh at 08:00"""
        from datetime import datetime, timedelta

        now = datetime.now()

        # Calculate next 08:00
        target_time = now.replace(hour=8, minute=0, second=0, microsecond=0)

        # If 08:00 has already passed today, schedule for tomorrow
        if now >= target_time:
            target_time += timedelta(days=1)

        # Calculate milliseconds until target time
        time_until_refresh = (target_time - now).total_seconds() * 1000

        print(f"\n[ΠΡΟΓΡΑΜΜΑΤΙΣΜΟΣ] Επόμενη αυτόματη ανανέωση: {target_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Schedule the refresh
        self.root.after(int(time_until_refresh), self.auto_refresh)

    def auto_refresh(self):
        """Auto-refresh data at 08:00 and schedule next refresh"""
        print("\n[ΑΥΤΟΜΑΤΗ ΑΝΑΝΕΩΣΗ] Ενεργοποιήθηκε καθημερινή ανανέωση δεδομένων στις 08:00")

        # Reset to today's date when auto-refreshing
        self.selected_date = date.today()

        self.refresh_data()
        self.update_shift_display()

        # Schedule next daily refresh
        self.schedule_daily_refresh()


def main():
    """Main function to run the GUI application"""
    root = tk.Tk()
    app = HospitalDisplayGUI(root)

    print("\n" + "="*60)
    print("Εφαρμογή Νοσοκομείων Εφημερίας Ξεκίνησε")
    print("="*60)
    print("\nΧειριστήρια:")
    print("  • F11: Εναλλαγή πλήρους οθόνης")
    print("  • ESC: Έξοδος από πλήρη οθόνη")
    print("  • Αυτόματη ανανέωση: Καθημερινά στις 08:00")
    print("\n" + "="*60 + "\n")

    root.mainloop()


if __name__ == "__main__":
    main()
