import sys

try:
    from qgis.PyQt.QtWidgets import QApplication
except ImportError:
    from PyQt5.QtWidgets import QApplication  # Or PyQt6 if your project uses it

from oqtopus.core.modules_registry import ModulesRegistry
from oqtopus.gui.main_dialog import MainDialog


def main():
    app = QApplication(sys.argv)
    modules_registry = ModulesRegistry()
    dialog = MainDialog(modules_registry)
    dialog.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
