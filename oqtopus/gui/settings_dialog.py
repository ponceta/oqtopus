from qgis.PyQt.QtWidgets import QDialog

from ..utils.plugin_utils import PluginUtils

DIALOG_UI = PluginUtils.get_ui_class("settings_dialog.ui")


class SettingsDialog(QDialog, DIALOG_UI):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.githubToken_lineEdit.setText(PluginUtils.get_github_token())
        self.githubToken_lineEdit.setToolTip(
            "<b>GitHub Access Token</b><br>"
            "A personal access token is required to access private repositories or to increase API rate limits.<br><br>"
            "To generate a token:<br>"
            "1. Go to <a href='https://github.com/settings/tokens'>GitHub Personal Access Tokens</a>.<br>"
            "2. Click <b>Generate new token</b>.<br>"
            "3. Select the <code>repo</code> scope for most operations.<br>"
            "4. Copy and paste the generated token here."
        )
        self.githubToken_label.setToolTip(self.githubToken_lineEdit.toolTip())

    def accept(self):
        PluginUtils.set_github_token(self.githubToken_lineEdit.text())
        super().accept()
