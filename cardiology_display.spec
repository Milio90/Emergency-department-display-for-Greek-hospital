# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Hospital On-Duty Display
Creates a standalone Windows executable
"""

block_cipher = None

a = Analysis(
    ['cardiology_display.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('onasseio_logo.png', '.'),  # Include logo in root of bundle
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkcalendar',
        'pdfplumber',
        'docx',
        'bs4',
        'lxml',
        'requests',
        'datetime',
        'json',
        'unicodedata',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='HospitalOnDutyDisplay',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False to hide console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add an .ico file path here if you have an icon
    version=None,  # You can add version info file here
)
