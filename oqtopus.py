import os
import sys
import types

# Create fake qgis.PyQt modules that point to PyQt5 modules
try:
    pyqt_widgets = __import__("PyQt6.QtWidgets", fromlist=[""])
    pyqt_core = __import__("PyQt6.QtCore", fromlist=[""])
    pyqt_gui = __import__("PyQt6.QtGui", fromlist=[""])
    pyqt_uic = __import__("PyQt6.uic", fromlist=[""])
except ModuleNotFoundError:
    pyqt_widgets = __import__("PyQt5.QtWidgets", fromlist=[""])
    pyqt_core = __import__("PyQt5.QtCore", fromlist=[""])
    pyqt_gui = __import__("PyQt5.QtGui", fromlist=[""])
    pyqt_uic = __import__("PyQt5.uic", fromlist=[""])

# Create the qgis, qgis.PyQt, and submodules in sys.modules
qgis = types.ModuleType("qgis")
pyqt = types.ModuleType("qgis.PyQt")
pyqt.QtWidgets = pyqt_widgets
pyqt.QtCore = pyqt_core
pyqt.QtGui = pyqt_gui
pyqt.uic = pyqt_uic

qgis.PyQt = pyqt
sys.modules["qgis"] = qgis
sys.modules["qgis.PyQt"] = pyqt
sys.modules["qgis.PyQt.QtWidgets"] = pyqt_widgets
sys.modules["qgis.PyQt.QtCore"] = pyqt_core
sys.modules["qgis.PyQt.QtGui"] = pyqt_gui
sys.modules["qgis.PyQt.uic"] = pyqt_uic

from qgis.PyQt.QtGui import QIcon  # noqa: E402

from oqtopus.core.modules_config import load_modules_from_conf  # noqa: E402
from oqtopus.gui.main_dialog import MainDialog  # noqa: E402
from oqtopus.utils.plugin_utils import PluginUtils  # noqa: E402


def main():
    app = pyqt_widgets.QApplication(sys.argv)
    icon = QIcon("oqtopus/icons/oqtopus-logo.png")
    app.setWindowIcon(icon)

    PluginUtils.init_logger()

    conf_path = os.path.join(os.path.dirname(__file__), "oqtopus/default_config.conf")
    modules_config = load_modules_from_conf(conf_path)

    dialog = MainDialog(modules_config)
    dialog.setWindowIcon(icon)
    dialog.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
