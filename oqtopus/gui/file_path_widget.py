"""Cross-platform file path widget.

Uses QgsFileWidget when running inside QGIS, falls back to a
QLineEdit + browse button for standalone mode.
"""

try:
    from qgis.gui import QgsFileWidget
except ImportError:
    QgsFileWidget = None

from qgis.PyQt.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLineEdit,
    QToolButton,
    QWidget,
)


class FilePathWidget(QWidget):
    """A file path selector widget that works in both QGIS and standalone."""

    class StorageMode:
        GetFile = "get_file"
        SaveFile = "save_file"
        GetDirectory = "get_directory"

    def __init__(self, parent=None, storage_mode=None, filter_string=""):
        super().__init__(parent)
        self.__filter = filter_string
        self.__storage_mode = storage_mode or self.StorageMode.GetFile

        if QgsFileWidget is not None:
            self.__qgs_widget = QgsFileWidget(self)
            qgs_mode = {
                self.StorageMode.GetFile: QgsFileWidget.StorageMode.GetFile,
                self.StorageMode.SaveFile: QgsFileWidget.StorageMode.SaveFile,
                self.StorageMode.GetDirectory: QgsFileWidget.StorageMode.GetDirectory,
            }[self.__storage_mode]
            self.__qgs_widget.setStorageMode(qgs_mode)
            if filter_string:
                self.__qgs_widget.setFilter(filter_string)
            layout = QHBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.__qgs_widget)
        else:
            self.__qgs_widget = None
            layout = QHBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            self.__line_edit = QLineEdit(self)
            self.__browse_button = QToolButton(self)
            self.__browse_button.setText("…")
            self.__browse_button.clicked.connect(self.__browse)
            layout.addWidget(self.__line_edit)
            layout.addWidget(self.__browse_button)

    def filePath(self) -> str:
        if self.__qgs_widget is not None:
            return self.__qgs_widget.filePath()
        return self.__line_edit.text()

    def setFilePath(self, path: str):
        if self.__qgs_widget is not None:
            self.__qgs_widget.setFilePath(path)
        else:
            self.__line_edit.setText(path)

    def __browse(self):
        if self.__storage_mode == self.StorageMode.SaveFile:
            path, _ = QFileDialog.getSaveFileName(self, self.tr("Select file"), "", self.__filter)
        elif self.__storage_mode == self.StorageMode.GetDirectory:
            path = QFileDialog.getExistingDirectory(self, self.tr("Select directory"))
        else:
            path, _ = QFileDialog.getOpenFileName(self, self.tr("Select file"), "", self.__filter)
        if path:
            self.__line_edit.setText(path)
