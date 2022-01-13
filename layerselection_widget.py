import os
from contextlib import contextmanager
from qgis.PyQt import uic, QtCore
from qgis.PyQt.QtWidgets import QApplication, QWidget, QGroupBox, QPushButton
from qgis.gui import QgsMapLayerComboBox, QgsFieldComboBox
from qgis.core import Qgis, QgsMapLayer, QgsMapLayerProxyModel, QgsProject, QgsVectorLayer, QgsAggregateCalculator, \
    QgsVectorLayerUtils, QgsExpression
from qgis.utils import iface, QgsMessageLog

from .exprutils import ExprUtils


@contextmanager
def waitCursor():
    try:
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        yield
    except Exception as ex:
        raise ex
    finally:
        QApplication.restoreOverrideCursor()


FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'layerselection_widget.ui'))


class LayerSelectionWidget(QWidget, FORM_CLASS):
    addFacet = QtCore.pyqtSignal(str)
    removeAllFacets = QtCore.pyqtSignal()
    layerChanged = QtCore.pyqtSignal(QgsVectorLayer)

    mapVlayerCb: QgsMapLayerComboBox
    addFacetBtn: QPushButton
    layerFieldsCb: QgsFieldComboBox

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.setupUi(self)
        self._initConnections()
        self._layer: QgsVectorLayer = None
        self._disableComponents(True)
        self.layerFieldsCb.setFilters(ExprUtils.supportedTypes())

    def _initConnections(self):
        self.mapVlayersCb.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.mapVlayersCb.setCurrentIndex(-1)  # TODO bringt nix :(
        self.mapVlayersCb.layerChanged.connect(self._layerChanged)
        self.mapVlayersCb.activated.connect(self._layerActivated)
        self.layerFieldsCb.fieldChanged.connect(self._layerFieldChanged)
        self.addFacetBtn.clicked.connect(self._addFacet)
        self.removeAllBtn.clicked.connect(self._removeAllFacets)
        inst: QgsProject = QgsProject.instance()
        inst.layerRemoved.connect(self._layerRemoved)

    def layer(self):
        return self._layer

    def _disableComponents(self, disabled: bool):
        if disabled:
            self.layerFieldsCb.clear()
            self.addFacetBtn.setDisabled(True)
            self.layerFieldsCb.setDisabled(True)
            self.removeAllBtn.setDisabled(True)
        else:
            # self.addFacetBtn.setDisabled(False)
            self.layerFieldsCb.setDisabled(False)
            self.layerFieldsCb.clear()

    def _layerFieldChanged(self, field: str):
        if field != "":
            self.addFacetBtn.setDisabled(False)
            self.removeAllBtn.setDisabled(False)
        else:
            self.addFacetBtn.setDisabled(True)
            self.removeAllBtn.setDisabled(True)

    def _layerRemoved(self, layerId):
        try:
            if self._layer.id() == layerId:  # layer removed
                self._layer = None
                self.layerChanged.emit(self._layer)
                self._disableComponents(True)
        except:  # removed
            self._layer = None
            self.layerChanged.emit(self._layer)
            self._disableComponents(True)

    def _layerActivated(self, idx):
        layer: QgsVectorLayer = self.mapVlayersCb.currentLayer()
        if self._layer != layer:
            self._layer = layer
            self.layerChanged.emit(self._layer)
            iface.setActiveLayer(layer)
            self._disableComponents(False)
            self.layerFieldsCb.setLayer(layer)

    def _layerChanged(self, layer: QgsMapLayer):
        if self._layer != layer:
            self._layer = layer
            self.layerChanged.emit(self._layer)
            self._disableComponents(False)
            self.layerFieldsCb.setLayer(layer)

    def _addFacet(self):
        with waitCursor():
            self.addFacet.emit(self.layerFieldsCb.currentField())

    def _removeAllFacets(self):
        with waitCursor():
            self.removeAllFacets.emit()