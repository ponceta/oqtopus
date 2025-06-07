from qgis.PyQt.QtWidgets import QDialog

from ..utils.plugin_utils import PluginUtils

DIALOG_UI = PluginUtils.get_ui_class("settings_dialog.ui")


class SettingsDialog(QDialog, DIALOG_UI):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.githubToken_lineEdit.setText(PluginUtils.get_github_token())

    def accept(self):
        PluginUtils.set_github_token(self.githubToken_lineEdit.text())
        super().accept()
