# Cardiology Display for Emergency Department

GUI application designed for displaying on-duty cardiology hospitals at Onassis Hospital Emergency Department.

## Features

- **Fullscreen Display** - Optimized for monitor display in emergency departments
- **Cardiology Focus** - Shows only cardiology hospitals on duty
- **Auto-Refresh** - Updates data every 30 minutes automatically
- **Time Slot Grouping** - Hospitals grouped by their duty time slots
- **Large, Readable Text** - Designed for viewing from a distance
- **Dark Theme** - Professional dark blue theme with high contrast
- **Emergency Info** - Prominent emergency contact numbers (166, 112)
- **Bilingual** - Greek and English display

## Installation

The cardiology display uses the same dependencies as the main application:

```bash
pip install -r requirements.txt
```

Tkinter is included with Python 3, but on some Linux systems you may need:

```bash
sudo apt-get install python3-tk
```

## Running the Display

### Basic Usage

```bash
python3 cardiology_display.py
```

The application will:
1. Open in fullscreen mode
2. Fetch current cardiology hospital data from Ministry of Health
3. Display hospitals grouped by time slot
4. Auto-refresh every 30 minutes

### Keyboard Controls

- **F11** - Toggle fullscreen mode on/off
- **ESC** - Exit fullscreen mode (for testing)
- **Mouse wheel** - Scroll through hospitals (if many are listed)

### Running on Startup (Linux)

To run the display automatically when the system boots:

1. Create a desktop entry:

```bash
nano ~/.config/autostart/cardiology-display.desktop
```

2. Add the following content (adjust paths as needed):

```ini
[Desktop Entry]
Type=Application
Name=Cardiology Display
Exec=/usr/bin/python3 "/home/dimitris/Έγγραφα/OCSC TEP display/cardiology_display.py"
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
```

3. Make it executable:

```bash
chmod +x ~/.config/autostart/cardiology-display.desktop
```

## Display Layout

### Header
- Main title: "ΝΟΣΟΚΟΜΕΙΑ ΕΦΗΜΕΡΙΑΣ - ΚΑΡΔΙΟΛΟΓΙΑ"
- Subtitle: "Cardiology Hospitals On Duty"
- Current date and time (Greek format)
- Last update time

### Content Area
Hospitals are displayed in large cards, grouped by time slot:

- **🕐 08:00-14:30** - Morning shift hospitals
- **🕐 14:30-08:00 επομένης** - Afternoon/Evening shift
- **🕐 08:00-08:00 επομένης** - 24-hour duty

Each card shows:
- Hospital name (large, bold text)
- Address (if available)
- Phone number (if available)
- Area/location (if available)

### Footer
Emergency contact information in both Greek and English.

## Color Scheme

The display uses a professional dark theme:

- **Background**: Dark blue (#1a1a2e)
- **Headers**: Darker blue (#16213e)
- **Cards**: Medium blue (#0f3460)
- **Text**: Light gray (#eaeaea)
- **Highlights**: Cyan (#00d4ff)
- **Emergency Info**: Red accent (#e94560)

## Configuration

### Changing Auto-Refresh Interval

Edit `cardiology_display.py` line 43:

```python
# Default: 30 minutes (1800000 milliseconds)
self.auto_refresh_interval = 1800000

# Example: 15 minutes
self.auto_refresh_interval = 900000

# Example: 1 hour
self.auto_refresh_interval = 3600000
```

### Changing Displayed Specialty

To show a different specialty (e.g., Orthopedics instead of Cardiology):

Edit `cardiology_display.py` line 135-136:

```python
# For Orthopedics
if "ορθοπεδ" in h.specialty.lower() or "orthoped" in h.specialty.lower()

# For Pediatrics
if "παιδιατρ" in h.specialty.lower() or "pediatr" in h.specialty.lower()
```

Also update the title in line 67-68.

### Font Sizes

Current font sizes (optimized for 1920x1080 or larger):
- **Title**: 42pt bold
- **Subtitle**: 24pt
- **Hospital name**: 32pt bold
- **Details**: 22pt
- **Footer**: 20pt bold

To adjust, edit the `tkfont.Font(size=XX)` values in `cardiology_display.py`.

## Testing

Test data loading without opening the GUI:

```bash
python3 test_cardiology_display.py
```

This will show:
- Total hospitals fetched
- Number of cardiology hospitals
- List of all cardiology hospitals with details

## Troubleshooting

### No Data Displayed

If the display shows "No data available":

1. **Check internet connection** - The scraper needs to access moh.gov.gr
2. **Run test script**: `python3 test_cardiology_display.py`
3. **Check cached data**: Look for `hospitals_on_duty.json` in the directory
4. **Run main scraper**: `python3 moh_scraper.py` to test data fetching

### GUI Doesn't Open

1. **Check Tkinter installation**:
   ```bash
   python3 -c "import tkinter; print('Tkinter OK')"
   ```

2. **Install if missing**:
   ```bash
   sudo apt-get install python3-tk
   ```

3. **Check DISPLAY environment variable** (for remote/SSH sessions):
   ```bash
   echo $DISPLAY
   ```

### Display Too Small/Large

Adjust font sizes in `cardiology_display.py`:
- Lines 67-68: Title fonts
- Line 77: DateTime font
- Line 196: Time slot header font
- Line 238: Hospital name font
- Line 249: Detail font

### Auto-Refresh Not Working

Check console output for error messages. The display prints status messages:
```
[AUTO-REFRESH] Triggered automatic data refresh
```

## Data Source

The display fetches data from:
- **Primary**: Ministry of Health official PDF files (moh.gov.gr)
- **Fallback**: Cached JSON file (`hospitals_on_duty.json`)

Data updates occur:
- **On startup**: Immediate fetch
- **Auto-refresh**: Every 30 minutes
- **Manual refresh**: Restart the application

## For Onassis Hospital

This display is specifically designed for the Emergency Department at Onassis Cardiac Surgery Center. It shows all cardiology hospitals on duty in Athens, helping emergency staff quickly identify where to refer or transfer patients requiring specialized cardiac care.

### Recommended Setup

1. **Dedicated monitor** - Connect to a wall-mounted display
2. **Auto-start** - Configure to launch on system boot
3. **Hide cursor** - Use `unclutter` to hide mouse cursor:
   ```bash
   sudo apt-get install unclutter
   unclutter -idle 0.1 &
   ```

4. **Prevent screen sleep** - Disable power management for the display
5. **Network reliability** - Ensure stable internet connection

## Support

For issues or questions:
- Check `README.md` for general project information
- Review `CLAUDE.md` for technical architecture
- Test with `test_cardiology_display.py` for debugging
