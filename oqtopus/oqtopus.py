import sys
from pathlib import Path

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QApplication

# Install the standalone ``qgis.PyQt`` shim before importing anything that
# depends on ``qgis.PyQt`` (this is a no-op when running inside QGIS).
from . import _qgis_shim  # noqa: F401
from .gui.main_dialog import MainDialog
from .utils.plugin_utils import PluginUtils


def main():
    app = QApplication(sys.argv)
    icon = QIcon("oqtopus/icons/oqtopus-logo.png")
    app.setWindowIcon(icon)

    PluginUtils.init_logger()

    conf_path = Path(__file__).parent / "default_config.yaml"

    dialog = MainDialog(modules_config_path=conf_path)
    dialog.setWindowIcon(icon)
    dialog.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
