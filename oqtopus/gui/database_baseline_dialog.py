# -----------------------------------------------------------
#
# Profile
# Copyright (C) 2025  Damiano Lombardi
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

import re
import tempfile

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout

from ..libs.pgserviceparser.gui.message_bar import MessageBar
from ..libs.pum.pum_config import PumConfig
from ..libs.pum.schema_migrations import SchemaMigrations
from ..utils.plugin_utils import PluginUtils, logger
from ..utils.qt_utils import OverrideCursor

DIALOG_UI = PluginUtils.get_ui_class("database_baseline_dialog.ui")


class DatabaseBaselineDialog(QDialog, DIALOG_UI):

    # In-memory session defaults (not persisted across sessions)
    _session_defaults = {
        "module": "",
        "version": "",
        "schema": "public",
    }

    def __init__(self, connection, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.__connection = connection

        # Message bar at top of dialog
        self.__message_bar = MessageBar(self)
        placeholder_layout = QVBoxLayout(self.messageBar_placeholder)
        placeholder_layout.setContentsMargins(0, 0, 0, 0)
        placeholder_layout.addWidget(self.__message_bar)

        # Restore session defaults
        self.module_lineEdit.setText(self._session_defaults["module"])
        self.version_lineEdit.setText(self._session_defaults["version"])
        self.schema_lineEdit.setText(self._session_defaults["schema"])

        self.buttonBox.accepted.connect(self._accept)

    def _accept(self):
        module_name = self.module_lineEdit.text().strip()
        version = self.version_lineEdit.text().strip()
        schema = self.schema_lineEdit.text().strip() or "public"

        if not module_name:
            self.__message_bar.pushError(self.tr("Please enter a module name."))
            return

        if not version:
            self.__message_bar.pushError(self.tr("Please enter a version."))
            return

        # Validate version format
        if not re.match(r"^\d+\.\d+(\.\d+)?$", version):
            self.__message_bar.pushError(
                self.tr("Invalid version format. Must be x.y or x.y.z (e.g. 1.0.0).")
            )
            return

        try:
            with OverrideCursor(Qt.CursorShape.WaitCursor):
                # Create a minimal PumConfig without a config file
                with tempfile.TemporaryDirectory() as tmpdir:
                    pum_config = PumConfig(
                        base_path=tmpdir,
                        validate=False,
                        pum={"module": module_name, "migration_table_schema": schema},
                    )

                    schema_migrations = SchemaMigrations(config=pum_config)

                    # Create the migration table if it doesn't exist
                    if not schema_migrations.exists(self.__connection):
                        schema_migrations.create(self.__connection, commit=False)

                    schema_migrations.set_baseline(
                        connection=self.__connection,
                        version=version,
                        commit=True,
                    )

        except Exception as e:
            errorText = self.tr(f"Error setting baseline:\n{e}")
            logger.error(errorText)
            self.__message_bar.pushError(errorText)
            return

        # Save values for next time during this session
        DatabaseBaselineDialog._session_defaults["module"] = module_name
        DatabaseBaselineDialog._session_defaults["version"] = version
        DatabaseBaselineDialog._session_defaults["schema"] = schema

        super().accept()
