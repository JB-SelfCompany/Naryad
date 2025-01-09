import os
import sys

if sys.platform == 'win32':
    if hasattr(sys, '_MEIPASS'):
        os.environ['QT_PLUGIN_PATH'] = os.path.join(sys._MEIPASS, 'PyQt6', 'Qt6', 'plugins')
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(sys._MEIPASS, 'PyQt6', 'Qt6', 'plugins', 'platforms')
        qt_path = os.path.join(sys._MEIPASS)
        if qt_path not in os.environ['PATH']:
            os.environ['PATH'] = qt_path + os.pathsep + os.environ['PATH']