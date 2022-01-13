import os

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog
from qgis.core import QgsVectorLayer

from .layerselection_widget import LayerSelectionWidget
from .facetedsearch_widget import FacetedSearchWidget
from .featureselection_widget import FeatureSelectionWidget

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'facetedfeatureselect_dialog.ui'))


class FacetedFeatureSelectDialog(QDialog, FORM_CLASS):
    layerSelection: LayerSelectionWidget
    facetContainer: FacetedSearchWidget
    featureSelection: FeatureSelectionWidget

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.setupUi(self)
        self._layer = None

        self.layerSelection = LayerSelectionWidget(self)
        self.layerSelection.layerChanged.connect(self._setLayer)
        self.layerSelection.addFacet.connect(self._addFacet)
        self.layerSelection.removeAllFacets.connect(self._removeAllFacets)
        self.layout().addWidget(self.layerSelection)

        self.facetContainer = FacetedSearchWidget()
        self.layout().addWidget(self.facetContainer)
        self.facetContainer.resetSearch.connect(self._removeFeatures)
        self.facetContainer.populateSearch.connect(self._populateFeatures)

        self.featureSelection = FeatureSelectionWidget(self)
        self.layout().addWidget(self.featureSelection)

    def initSelection(self):
        if self._layer is not None:
            self.featureSelection.remove_all_from_selection()

    def _setLayer(self, layer: QgsVectorLayer = None):
        if layer is None:
            return
        self._layer = layer
        self.facetContainer.setLayer(layer)
        self.featureSelection.setLayer(layer)

    def _removeAllFacets(self):
        self.facetContainer.removeAllFacets()

    def _addFacet(self, field: str):
        self.facetContainer.addFacet(field)

    def _populateFeatures(self):
        self.featureSelection.populateFeatures()

    def _removeFeatures(self):
        self.featureSelection.removeFeatures()
