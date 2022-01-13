import os
from contextlib import contextmanager
from qgis.PyQt import uic, QtCore
from qgis.PyQt.QtWidgets import QApplication, QWidget
from qgis.core import QgsVectorLayer, QgsField

from .facetedsearch import FacetedSearch
from .facet_widget import FacetWidget


@contextmanager
def waitCursor():
    try:
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        yield
    except Exception as ex:
        raise ex
    finally:
        QApplication.restoreOverrideCursor()


FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'facetedsearch_widget.ui'))


class FacetedSearchWidget(QWidget, FORM_CLASS):
    resetSearch = QtCore.pyqtSignal()
    populateSearch = QtCore.pyqtSignal()

    container: QWidget

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.setupUi(self)
        self._layer: QgsVectorLayer = None
        self.facetedSearch: FacetedSearch = FacetedSearch()

    def setLayer(self, layer: QgsVectorLayer):
        self._layer = layer
        self.removeAllFacets()

    def removeAllFacets(self):
        for idx in reversed(range(self.container.layout().count())):
            item = self.container.layout().itemAt(idx)
            if item is not None:
                self._removeFacet(item.widget())

    def _removeFacet(self, widget: QWidget):
        self.container.layout().removeWidget(widget);
        widget.setParent(None)
        self.resetFacetedSearch()

    def _attributeForName(self, name: str):
        field: QgsField
        for field in self._layer.fields():
            if field.name() == name:
                return field
        return None

    def addFacet(self, fieldName: str):
        field: QgsField = self._attributeForName(fieldName)
        idx = self.container.layout().count()
        widget = FacetWidget(self.container, idx, field)
        widget.layout().setContentsMargins(0,0,0,0)
        self.container.layout().addWidget(widget)
        # widget.setEnabled(False)
        widget.inputChanged.connect(self._facetInputChanged)
        widget.inputEmpty.connect(self._facetInputEmpty)
        widget.toRemove.connect(self._removeFacet)
        self.resetFacetedSearch()

    def _facetInputChanged(self, widget: FacetWidget):
        idx = self._idxForWidget(widget)
        if idx is None:
            return
        with waitCursor():
            self.facetedSearch.search(idx)
            self._populateFeatures(idx)

    def _facetInputEmpty(self, widget: FacetWidget):
        idx = self._idxForWidget(widget)
        if idx is None:
            return
        with waitCursor():
            self.facetedSearch.search(idx)
            self._resetFeatures(idx)

    def _idxForWidget(self, widget: FacetWidget):
        for idx in range(0, self.container.layout().count(), 1):
            fw: FacetWidget = self.container.layout().itemAt(idx).widget()
            if fw == widget:
                return idx
        return None

    def resetFacetedSearch(self):
        self.facetedSearch.setLayer(self._layer)
        widgets = []
        for idx in range(0, self.container.layout().count(), 1):
            widgets.append(self.container.layout().itemAt(idx).widget())
        self.facetedSearch.setWidgets(widgets)
        self.resetSearch.emit()

    def _populateFeatures(self, idx):
        if idx == self.container.layout().count() - 1:
            self.populateSearch.emit()
        else:
            self.resetSearch.emit()

    def _resetFeatures(self, idx):
        if idx > 0 and idx == self.container.layout().count() - 1:
            self.populateSearch.emit()
        else:
            self.resetSearch.emit()
