# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

block_cipher = None

qt_binaries = []
qt_plugins = []

if sys.platform == 'win32':
    site_packages = [p for p in sys.path if 'site-packages' in p][0]
    qt_path = os.path.join(site_packages, 'PyQt6', 'Qt6')
    binaries_path = os.path.join(qt_path, 'bin')
    plugins_path = os.path.join(qt_path, 'plugins')
    
    required_dlls = [
        'Qt6Core.dll',
        'Qt6Gui.dll',
        'Qt6Widgets.dll',
        'Qt6PrintSupport.dll'
    ]
    
    for dll in required_dlls:
        dll_path = os.path.join(binaries_path, dll)
        if os.path.exists(dll_path):
            qt_binaries.append((dll_path, '.'))

    required_plugins = {
        'platforms': ['qwindows.dll'],
        'styles': ['qwindowsvistastyle.dll']
    }
    
    for plugin_type, plugin_files in required_plugins.items():
        plugin_dir = os.path.join(plugins_path, plugin_type)
        if os.path.exists(plugin_dir):
            for file in plugin_files:
                plugin_path = os.path.join(plugin_dir, file)
                if os.path.exists(plugin_path):
                    qt_plugins.append((plugin_path, os.path.join('PyQt6', 'Qt6', 'plugins', plugin_type)))

excludes = [
    'PyQt6.QtNetwork',
    'PyQt6.Qt3D*',
    'PyQt6.QtBluetooth',
    'PyQt6.QtDBus',
    'PyQt6.QtDesigner',
    'PyQt6.QtHelp',
    'PyQt6.QtLocation',
    'PyQt6.QtMultimedia',
    'PyQt6.QtNfc',
    'PyQt6.QtOpenGL',
    'PyQt6.QtPositioning',
    'PyQt6.QtQml',
    'PyQt6.QtQuick',
    'PyQt6.QtSensors',
    'PyQt6.QtSerialPort',
    'PyQt6.QtSql',
    'PyQt6.QtSvg',
    'PyQt6.QtTest',
    'PyQt6.QtWebChannel',
    'PyQt6.QtWebEngine',
    'PyQt6.QtWebSockets',
    'PyQt6.QtXml'
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=qt_binaries,
    datas=qt_plugins,
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtPrintSupport',
        'PyQt6.sip',
        'numpy',
        'pandas',
        'matplotlib',
        'sklearn',
        'matplotlib.backends.backend_qt5agg'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['qt_runtime_hook.py'],
    excludes=excludes,
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
