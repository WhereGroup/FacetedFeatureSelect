import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'start_confirm_dialog.ui'))


class StartConfirmDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.setupUi(self)