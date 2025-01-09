# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

block_cipher = None

qt_data = collect_data_files('PyQt6')
matplotlib_data = collect_data_files('matplotlib')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=qt_data + matplotlib_data,
    hiddenimports=[
        'PyQt6.QtPrintSupport',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.sip',
        'numpy',
        'pandas',
        'matplotlib',
        'sklearn',
        'matplotlib.backends.backend_qt5agg'
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
    name='naryad',
    debug=False,
    strip=False,
    upx=True,
    console=True,
    runtime_tmpdir=None,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)