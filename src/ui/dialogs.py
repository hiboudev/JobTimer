from PyQt5.QtCore import QRegExp, QObject, QEvent
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QDialog, QWidget
from PyQt5 import QtWidgets

from ui.create_project_ui import Ui_CreateProjectDialog


class CreateProjectDialog(QDialog):
    """Employee dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Create an instance of the GUI
        self.ui = Ui_CreateProjectDialog()
        # Run the .setupUi() method to show the GUI
        self.ui.setupUi(self)

        # self.ui.buttonBox.accepted.setEnabled(False)

        # btn_ok = self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        # btn_ok.setEnabled(False)

        self.ui.hourlyRate.setValidator(QRegExpValidator(QRegExp('[0-9]+')))

    def set_values(self, name: str, hourly_rate: int):
        self.ui.projectName.setText(name)
        self.ui.hourlyRate.setText(str(hourly_rate))

    def get_project_name(self) -> str:
        return self.ui.projectName.text()

    def get_hourly_rate(self) -> str:
        return self.ui.hourlyRate.text()

    def done(self, result):
        if not result:
            super().done(result)
            return

        if not self.ui.projectName.text():
            self.show_error(self.ui.projectName)
            return

        if not self.ui.hourlyRate.text():
            self.show_error(self.ui.hourlyRate)
            return

        super().done(result)

    def show_error(self, widget: QWidget):
        widget.setStyleSheet("background-color: red")
        widget.installEventFilter(self)

    def eventFilter(self, widget: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.FocusIn:
            widget.setStyleSheet("")

        return super().eventFilter(widget, event)
