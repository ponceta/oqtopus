import os
import shutil

from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox, QWidget

from ..core.module_package import ModulePackage
from ..utils.plugin_utils import PluginUtils
from ..utils.qt_utils import CriticalMessageBox, QtUtils

DIALOG_UI = PluginUtils.get_ui_class("project_widget.ui")


class ProjectWidget(QWidget, DIALOG_UI):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        self.project_install_pushButton.clicked.connect(self.__projectInstallClicked)
        self.project_seeChangelog_pushButton.clicked.connect(self.__projectSeeChangelogClicked)

        self.__current_module_package = None

    def setModulePackage(self, module_package: ModulePackage):
        self.__current_module_package = module_package
        self.__packagePrepareGetProjectFilename()

    def __packagePrepareGetProjectFilename(self):
        asset_project = self.__current_module_package.asset_project
        if asset_project is None:
            self.project_info_label.setText(
                self.tr("No project asset available for this module version.")
            )
            QtUtils.setForegroundColor(self.project_info_label, PluginUtils.COLOR_WARNING)
            QtUtils.setFontItalic(self.project_info_label, True)
            return

        # Search for QGIS project file in self.__package_dir
        project_file_dir = os.path.join(asset_project.package_dir, "project")

        # Check if the directory exists
        if not os.path.exists(project_file_dir):
            self.project_info_label.setText(
                self.tr(f"Project directory '{project_file_dir}' does not exist.")
            )
            QtUtils.setForegroundColor(self.project_info_label, PluginUtils.COLOR_WARNING)
            QtUtils.setFontItalic(self.project_info_label, True)
            return

        self.__project_file = None
        for root, dirs, files in os.walk(project_file_dir):
            for file in files:
                if file.endswith(".qgz") or file.endswith(".qgs"):
                    self.__project_file = os.path.join(root, file)
                    break

            if self.__project_file:
                break

        if self.__project_file is None:
            self.project_info_label.setText(
                self.tr(f"No QGIS project file (.qgz or .qgs) found into {project_file_dir}."),
            )
            QtUtils.setForegroundColor(self.project_info_label, PluginUtils.COLOR_WARNING)
            QtUtils.setFontItalic(self.db_database_label, True)
            return

        self.project_info_label.setText(
            self.tr(self.__project_file),
        )
        QtUtils.setForegroundColor(self.project_info_label, PluginUtils.COLOR_GREEN)
        QtUtils.setFontItalic(self.db_database_label, False)

    def __projectInstallClicked(self):

        if self.__current_module_package is None:
            QMessageBox.warning(
                self,
                self.tr("Error"),
                self.tr("Please select a module and version first."),
            )
            return

        if self.module_package_comboBox.currentData() is None:
            QMessageBox.warning(
                self,
                self.tr("Error"),
                self.tr("Please select a module version first."),
            )
            return

        asset_project = self.module_package_comboBox.currentData().asset_project
        if asset_project is None:
            QMessageBox.warning(
                self,
                self.tr("Error"),
                self.tr("No project asset available for this module version."),
            )
            return

        package_dir = asset_project.package_dir
        if package_dir is None:
            CriticalMessageBox(
                self.tr("Error"), self.tr("No valid package directory available."), None, self
            ).exec()
            return

        # Search for QGIS project file in package_dir
        project_file_dir = os.path.join(package_dir, "project")

        # Check if the directory exists
        if not os.path.exists(project_file_dir):
            CriticalMessageBox(
                self.tr("Error"),
                self.tr(f"Project directory '{project_file_dir}' does not exist."),
                None,
                self,
            ).exec()
            return

        self.__project_file = None
        for root, dirs, files in os.walk(project_file_dir):
            print(f"Searching for QGIS project file in {root}: {files}")
            for file in files:
                if file.endswith(".qgz") or file.endswith(".qgs"):
                    self.__project_file = os.path.join(root, file)
                    break

            if self.__project_file:
                break

        if self.__project_file is None:
            CriticalMessageBox(
                self.tr("Error"),
                self.tr(f"No QGIS project file (.qgz or .qgs) found into {project_file_dir}."),
                None,
                self,
            ).exec()
            return

        install_destination = QFileDialog.getExistingDirectory(
            self,
            self.tr("Select installation directory"),
            "",
            QFileDialog.Option.ShowDirsOnly,
        )

        if not install_destination:
            return

        # Copy the project file to the selected directory
        try:
            shutil.copy(self.__project_file, install_destination)
            QMessageBox.information(
                self,
                self.tr("Project installed"),
                self.tr(
                    f"Project file '{self.__project_file}' has been copied to '{install_destination}'."
                ),
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr(f"Failed to copy project file: {e}"),
            )
            return

    def __projectSeeChangelogClicked(self):
        self.__seeChangeLogClicked()
