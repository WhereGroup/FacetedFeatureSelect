import os
from qgis.PyQt import uic, QtWidgets, QtCore
from PyQt5.QtWidgets import QComboBox
from qgis.core import QgsApplication

from .exprutils import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'facet_widget.ui'))

class FacetWidget(QtWidgets.QWidget, FORM_CLASS):
    toRemove = QtCore.pyqtSignal(QtWidgets.QWidget)
    inputChanged = QtCore.pyqtSignal(QtWidgets.QWidget)
    inputEmpty = QtCore.pyqtSignal(QtWidgets.QWidget)

    searchTerm: QLineEdit
    aggrTypeCb: QComboBox

    def __init__(self, parent=None, idx: int = None, field: QgsField = None):
        """Constructor."""
        super().__init__(parent)
        self.setupUi(self)
        #self._idx = idx
        self._field = field
        self.label.setText(self._field.name())
        self._lastValue: any = None
        #self._lastCaller: any = None
        #self._aggrExpr: QgsExpression = QgsExpression(ExprUtils.aggrExpr(self._field.name()))
        self._searchExpr: QgsExpression = None
        self.removeBtn.clicked.connect(self._toRemove)
        self.searchTerm.setClearButtonEnabled(True)
        self.searchTerm.editingFinished.connect(self.editingFinished)
        self.searchTerm.inputRejected.connect(self.inputRejected)
        self.searchTerm.returnPressed.connect(self.returnPressed)
        self.searchTerm.selectionChanged.connect(self.selectionChanged)
        self.aggrTypeCb.addItems(ExprUtils.listOps(self._field))
        self.aggrTypeCb.setCurrentIndex(0)
        self.aggrTypeCb.currentTextChanged.connect(self._initSearchExpr)
        self.searchTerm.textChanged.connect(self.textChanged)
        self.searchTerm.textEdited.connect(self.textEdited)
        self.searchTerm.inputRejected.connect(self.inputRejected)

    def _toRemove(self):
        # QgsMessageLog.logMessage("remove".format(), tag="FFS", level=Qgis.Info)
        self.toRemove.emit(self)

    def disable(self, disable: bool):
        if disable:
            self.aggrTypeCb.setEnabled(False)
            self.searchTerm.setEnabled(False)
        else:
            self.aggrTypeCb.setEnabled(True)
            self.searchTerm.setEnabled(True)

    def _initSearchExpr(self):
        self._searchExpr = ExprUtils.initSearchExpr(self._field, self.searchTerm, self.aggrTypeCb.currentText())

    def value(self):
        return self._lastValue

    def _changed(self, sender=None):
        if not self.isEnabled():
            return
        value = ExprUtils.value(self._field, self.searchTerm)
        if type(value) == bool:
            return

        if len(str(value)) > 0:
            self._lastValue = str(value)
            self.inputChanged.emit(self)
        else:
            self._lastValue = None
            self.inputEmpty.emit(self)

    def field(self):
        return self._field.name()
    #
    # def facetName(self):
    #     return self._field.name()


    def searchExpr(self):
        return self._searchExpr

    def clear(self):
        self.searchTerm.setCompleter(None)
        # self.aggrTypeCb.setDisabled(True)
        self.searchTerm.clear()

    def reset(self, layer: QgsVectorLayer):
        ExprUtils.initSearchField(self._field, self.searchTerm, layer, QLocale(QgsApplication.locale()))
        self._initSearchExpr()

    def editingFinished(self):
        # QgsMessageLog.logMessage("editingFinished", tag="FFS", level=Qgis.Info)
        self._changed("editingFinished")

    def returnPressed(self):
        # QgsMessageLog.logMessage("returnPressed", tag="FFS", level=Qgis.Info)
        self._changed("returnPressed")

    def selectionChanged(self):
        # QgsMessageLog.logMessage("selectionChanged", tag="FFS", level=Qgis.Info)
        self._changed("selectionChanged")

    def textChanged(self):
        # QgsMessageLog.logMessage("textChanged", tag="FFS", level=Qgis.Info)
        self._changed("textChanged")

    def textEdited(self, index):
        # QgsMessageLog.logMessage("textEdited", tag="FFS", level=Qgis.Info)
        self._changed("textEdited")

    def inputRejected(self):
        # QgsMessageLog.logMessage("inputRejected", tag="FFS", level=Qgis.Info)
        self._changed("inputRejected")
