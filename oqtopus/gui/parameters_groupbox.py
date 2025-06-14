import logging

from pum import ParameterDefinition, ParameterType
from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QWidget,
)

logger = logging.getLogger(__name__)


class ParameterWidget(QWidget):
    def __init__(self, parameter_definition: ParameterDefinition, parent):
        QWidget.__init__(self, parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.value = None
        self.__valueChanged = False

        if parameter_definition.type != ParameterType.BOOLEAN:
            self.layout.addWidget(QLabel(parameter_definition.name, self))

        if parameter_definition.type == ParameterType.BOOLEAN:
            self.widget = QCheckBox(parameter_definition.name, self)
            self.widget.setChecked(parameter_definition.default)
            self.widget.checked.connect(self.__valueChanged)
            self.layout.addWidget(self.widget)
            self.value = lambda: self.widget.isChecked()
        elif parameter_definition.type in (
            ParameterType.DECIMAL,
            ParameterType.INTEGER,
            ParameterType.TEXT,
        ):
            self.widget = QLineEdit(self)
            self.widget.setPlaceholderText(parameter_definition.default.as_string())
            self.layout.addWidget(self.widget)
            if parameter_definition.type == ParameterType.INTEGER:
                self.value = lambda: int(self.widget.text())
            elif parameter_definition.type == ParameterType.DECIMAL:
                self.value = lambda: float(self.widget.text())
            else:
                self.value = lambda: self.widget.text()

    def valueSet(self):
        """
        Returns True if the value of the widget is set, False otherwise.
        This is used to determine if the parameter has been modified by the user.
        """
        if self.widget is None:
            return False

        if isinstance(self.widget, QCheckBox):
            return self.__valueChanged

        if isinstance(self.widget, QLineEdit):
            return bool(self.widget.text().strip())

        return False

    def __valueChanged(self):
        """
        This method is called when the value of the widget is changed for QCheckBox.
        It sets the __valueChanged flag to True, indicating that the value has been modified.
        """
        self.__valueChanged = True


class ParametersGroupBox(QGroupBox):
    def __init__(self, parent):
        QGroupBox.__init__(self, parent)
        self.parameter_widgets = {}

    def setParameters(self, parameters: list[ParameterDefinition]):
        logger.info("Setting parameters in ParametersGroupBox (%s)", len(parameters))
        self.clean()
        self.parameters = parameters
        # Remove all widgets from the parameters_group_box layout
        for parameter in parameters:
            pw = ParameterWidget(parameter, self)
            self.layout().addWidget(pw)
            self.parameter_widgets[parameter.name] = pw

    def parameters_values(self):
        values = {}
        for parameter in self.parameters:
            if self.parameter_widgets[parameter.name].valueSet():
                values[parameter.name] = self.parameter_widgets[parameter.name].value()
            else:
                if parameter.type == ParameterType.BOOLEAN:
                    values[parameter.name] = bool(parameter.default.as_string())
                elif parameter.type == ParameterType.INTEGER:
                    values[parameter.name] = int(parameter.default.as_string())
                elif parameter.type == ParameterType.DECIMAL:
                    values[parameter.name] = float(parameter.default.as_string())
                # else:
                #     values[parameter.name] = parameter.default
        return values

    def clean(self):
        for widget in self.parameter_widgets.values():
            widget.deleteLater()
        self.parameter_widgets = {}
