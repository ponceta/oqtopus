import logging

from qgis.PyQt.QtWidgets import QApplication, QStyle, QTreeWidgetItem, QWidget

from ..utils.plugin_utils import LoggingBridge, PluginUtils

DIALOG_UI = PluginUtils.get_ui_class("logs_widget.ui")


class LogsWidget(QWidget, DIALOG_UI):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        self.loggingBridge = LoggingBridge(
            level=logging.NOTSET, excluded_modules=["urllib3.connectionpool"]
        )
        self.loggingBridge.loggedLine.connect(self.__logged_line)
        logging.getLogger().addHandler(self.loggingBridge)

        self.logs_openFile_toolButton.setIcon(
            QApplication.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        )
        self.logs_openFolder_toolButton.setIcon(
            QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon)
        )
        self.logs_clear_toolButton.setIcon(
            QApplication.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton)
        )

        self.logs_openFile_toolButton.clicked.connect(self.__logsOpenFileClicked)
        self.logs_openFolder_toolButton.clicked.connect(self.__logsOpenFolderClicked)
        self.logs_clear_toolButton.clicked.connect(self.__logsClearClicked)

    def close(self):
        # uninstall the logging bridge
        logging.getLogger().removeHandler(self.loggingBridge)

    def __logged_line(self, record, line):

        treeWidgetItem = QTreeWidgetItem([record.levelname, record.name, record.msg])

        self.logs_treeWidget.addTopLevelItem(treeWidgetItem)

        # Automatically scroll to the bottom of the logs
        scroll_bar = self.logs_treeWidget.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())

    def __logsOpenFileClicked(self):
        PluginUtils.open_log_file()

    def __logsOpenFolderClicked(self):
        PluginUtils.open_logs_folder()

    def __logsClearClicked(self):
        self.logs_treeWidget.clear()
