# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all submodules for packages with dynamic imports
hiddenimports = [
    # Standard library
    'html',
    'html.parser',
    'tkinter',
    'email',
    'mailbox',
    'csv',
    'io',
    'tempfile',
    'threading',
    'pathlib',
    'datetime',
    'base64',
    # Namespace packages and setuptools dependencies
    'jaraco',
    'pkg_resources',
    'setuptools',
]

# Add all submodules from third-party packages
for package in ['xhtml2pdf', 'reportlab', 'pypdf', 'PIL', 'bleach', 'docx', 'openpyxl']:
    hiddenimports.extend(collect_submodules(package))

a = Analysis(
    ['src/gui.py'],
    pathex=[],
    binaries=[],
    datas=[('src', 'src')],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='mbox-to-pdf',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='mbox-to-pdf.app',
    icon=None,
    bundle_identifier='com.example.mbox-to-pdf',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
    },
)
