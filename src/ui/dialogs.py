from PyQt5.QtCore import QRegExp, QObject, QEvent
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QDialog, QWidget

from ui.create_project_ui import Ui_CreateProjectDialog
from ui.edit_project_ui import Ui_EditProjectDialog
from utils import utils


class CreateProjectDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._build_ui()
        # Run the .setupUi() method to show the GUI
        self.ui.setupUi(self)

        self.ui.hourlyRate.setValidator(QRegExpValidator(QRegExp('[0-9]+')))

    def _build_ui(self):
        self.ui = Ui_CreateProjectDialog()

    def set_values(self, name: str, hourly_rate: int):
        self.ui.projectName.setText(name)
        self.ui.hourlyRate.setText(str(hourly_rate))

    def get_project_name(self) -> str:
        return self.ui.projectName.text()

    def get_hourly_rate(self) -> str:
        return self.ui.hourlyRate.text()

    def done(self, result: int):
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


class EditProjectDialog(CreateProjectDialog):

    def _build_ui(self):
        self.ui = Ui_EditProjectDialog()

    def get_seconds(self) -> int:
        return utils.hms_to_seconds(
            int(self.ui.elapsedHours.text()),
            int(self.ui.elapsedMinutes.text()),
            int(self.ui.elapsedSeconds.text()),
        )

    def set_seconds(self, elapsed_seconds: int):
        h, m, s = utils.seconds_to_hms(elapsed_seconds)
        self.ui.elapsedHours.setText(str(h))
        self.ui.elapsedMinutes.setText(str(m))
        self.ui.elapsedSeconds.setText(str(s))
