import os
import sys
import types

from PyQt5.QtGui import QIcon

# Create fake qgis.PyQt modules that point to PyQt5 modules
pyqt5_widgets = __import__("PyQt5.QtWidgets", fromlist=[""])
pyqt5_core = __import__("PyQt5.QtCore", fromlist=[""])
pyqt5_gui = __import__("PyQt5.QtGui", fromlist=[""])
pyqt5_uic = __import__("PyQt5.uic", fromlist=[""])

# Create the qgis, qgis.PyQt, and submodules in sys.modules
qgis = types.ModuleType("qgis")
pyqt = types.ModuleType("qgis.PyQt")
pyqt.QtWidgets = pyqt5_widgets
pyqt.QtCore = pyqt5_core
pyqt.QtGui = pyqt5_gui
pyqt.uic = pyqt5_uic

qgis.PyQt = pyqt
sys.modules["qgis"] = qgis
sys.modules["qgis.PyQt"] = pyqt
sys.modules["qgis.PyQt.QtWidgets"] = pyqt5_widgets
sys.modules["qgis.PyQt.QtCore"] = pyqt5_core
sys.modules["qgis.PyQt.QtGui"] = pyqt5_gui
sys.modules["qgis.PyQt.uic"] = pyqt5_uic

from oqtopus.core.modules_config import load_modules_from_conf  # noqa: E402
from oqtopus.gui.main_dialog import MainDialog  # noqa: E402


def main():
    app = pyqt5_widgets.QApplication(sys.argv)
    icon = QIcon("oqtopus/icons/oqtopus-logo.png")
    app.setWindowIcon(icon)

    conf_path = os.path.join(os.path.dirname(__file__), "oqtopus/default_config.conf")
    modules_config = load_modules_from_conf(conf_path)

    dialog = MainDialog(modules_config)
    dialog.setWindowIcon(icon)
    dialog.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
