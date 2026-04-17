"""Standalone-mode shim.

When oqtopus is imported outside of QGIS (e.g. from ``oqtopus/oqtopus.py``),
the real ``qgis.PyQt`` package is not available. Importing this module
installs fake ``qgis`` / ``qgis.PyQt.*`` entries in ``sys.modules`` that
forward to PyQt6 (preferred) or PyQt5.

This module must NOT be imported from ``oqtopus/__init__.py`` so that the
QGIS plugin import path stays minimal and always exposes ``classFactory``.
"""

import sys
import types

if "qgis" not in sys.modules:
    try:
        pyqt_core = __import__("PyQt6.QtCore", fromlist=[""])
        pyqt_gui = __import__("PyQt6.QtGui", fromlist=[""])
        pyqt_network = __import__("PyQt6.QtNetwork", fromlist=[""])
        pyqt_widgets = __import__("PyQt6.QtWidgets", fromlist=[""])
        pyqt_uic = __import__("PyQt6.uic", fromlist=[""])
    except ModuleNotFoundError:
        pyqt_core = __import__("PyQt5.QtCore", fromlist=[""])
        pyqt_gui = __import__("PyQt5.QtGui", fromlist=[""])
        pyqt_network = __import__("PyQt5.QtNetwork", fromlist=[""])
        pyqt_widgets = __import__("PyQt5.QtWidgets", fromlist=[""])
        pyqt_uic = __import__("PyQt5.uic", fromlist=[""])

    qgis = types.ModuleType("qgis")
    pyqt = types.ModuleType("qgis.PyQt")
    pyqt.QtCore = pyqt_core
    pyqt.QtGui = pyqt_gui
    pyqt.QtNetwork = pyqt_network
    pyqt.QtWidgets = pyqt_widgets
    pyqt.uic = pyqt_uic

    qgis.PyQt = pyqt
    sys.modules["qgis"] = qgis
    sys.modules["qgis.PyQt"] = pyqt
    sys.modules["qgis.PyQt.QtCore"] = pyqt_core
    sys.modules["qgis.PyQt.QtGui"] = pyqt_gui
    sys.modules["qgis.PyQt.QtNetwork"] = pyqt_network
    sys.modules["qgis.PyQt.QtWidgets"] = pyqt_widgets
    sys.modules["qgis.PyQt.uic"] = pyqt_uic
