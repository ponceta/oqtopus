# -----------------------------------------------------------
#
# Profile
# Copyright (C) 2025  Denis Rouzaud
# -----------------------------------------------------------
#
# licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, print to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# ---------------------------------------------------------------------

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout

from ..libs.pgserviceparser.gui.message_bar import MessageBar
from ..libs.pum.dumper import Dumper
from ..utils.pg_utils import find_pg_executable
from ..utils.plugin_utils import PluginUtils, logger
from ..utils.qt_utils import OverrideCursor
from .file_path_widget import FilePathWidget

DIALOG_UI = PluginUtils.get_ui_class("database_restore_dialog.ui")


class DatabaseRestoreDialog(QDialog, DIALOG_UI):

    _session_defaults = {
        "file_path": "",
        "exclude_schemas": "",
    }

    def __init__(self, service_name, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.__service_name = service_name

        # Message bar
        self.__message_bar = MessageBar(self)
        placeholder_layout = QVBoxLayout(self.messageBar_placeholder)
        placeholder_layout.setContentsMargins(0, 0, 0, 0)
        placeholder_layout.addWidget(self.__message_bar)

        # File path widget
        self.__file_path_widget = FilePathWidget(
            parent=self,
            storage_mode=FilePathWidget.StorageMode.GetFile,
            filter_string=self.tr("Dump files (*.dump *.backup *.sql);;All files (*)"),
        )
        file_placeholder_layout = QVBoxLayout(self.filePath_placeholder)
        file_placeholder_layout.setContentsMargins(0, 0, 0, 0)
        file_placeholder_layout.addWidget(self.__file_path_widget)

        # Restore session defaults
        self.__file_path_widget.setFilePath(self._session_defaults["file_path"])
        self.excludeSchemas_lineEdit.setText(self._session_defaults["exclude_schemas"])

        self.buttonBox.accepted.connect(self._accept)

    def _accept(self):
        file_path = self.__file_path_widget.filePath().strip()
        if not file_path:
            self.__message_bar.pushError(self.tr("Please select a dump file."))
            return

        exclude_schemas = [
            s.strip() for s in self.excludeSchemas_lineEdit.text().split(",") if s.strip()
        ]

        try:
            with OverrideCursor(Qt.CursorShape.WaitCursor):
                dumper = Dumper(
                    pg_connection=self.__service_name,
                    dump_path=file_path,
                )
                dumper.pg_restore(
                    pg_restore_exe=find_pg_executable("pg_restore"),
                    exclude_schema=exclude_schemas or None,
                )
        except Exception as e:
            errorText = self.tr(f"Error restoring database:\n{e}")
            logger.error(errorText)
            self.__message_bar.pushError(errorText)
            return

        # Save session defaults
        DatabaseRestoreDialog._session_defaults["file_path"] = file_path
        DatabaseRestoreDialog._session_defaults["exclude_schemas"] = (
            self.excludeSchemas_lineEdit.text()
        )

        super().accept()
