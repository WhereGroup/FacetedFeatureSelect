import os

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QListWidget, QListWidgetItem, QPushButton
from qgis.gui import QgsFieldComboBox
from qgis.core import QgsApplication, QgsVectorLayer, QgsFeatureIterator

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'featureselection_widget.ui'))


class FeatureSelectionWidget(QtWidgets.QWidget, FORM_CLASS):
    selectAllBtn: QPushButton
    featureLabelCb: QgsFieldComboBox
    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.setupUi(self)
        self._layer: QgsVectorLayer = None
        self._featureLabel = None
        self.selectAllBtn.setAutoDefault(False)
        self.selectSingleBtn.setAutoDefault(False)
        self.unselectSingleBtn.setAutoDefault(False)
        self.unselectAllBtn.setAutoDefault(False)
        self.featureLabelCb.fieldChanged.connect(self._layerFieldChanged)
        self.selectAllBtn.clicked.connect(self.move_all_to_selection)
        self.selectSingleBtn.clicked.connect(self.move_selected_to_selection)
        self.unselectSingleBtn.clicked.connect(self.remove_selected_from_selection)
        self.unselectAllBtn.clicked.connect(self.remove_all_from_selection)

    def setLayer(self, layer: QgsVectorLayer = None):
        self._layer = layer
        self.featureLabelCb.setLayer(layer);
        if self._layer is None:
            self.featureLabelCb.clear()
            self.featureLabelCb.setDisabled(True)
            self._featureLabel = None
        else:
            self.featureLabelCb.setDisabled(False)
            self.featureLabelCb.setCurrentIndex(0)
            self._featureLabel = self.featureLabelCb.currentField()

    def _layerFieldChanged(self, label: str):
        self._featureLabel = label
        self.rename_items(self._layer, self._featureLabel, self.availableFeaturesLw)
        self.rename_items(self._layer, self._featureLabel, self.selectedFeaturesLw)

    def removeMarked(self):
        self.select_features_on_canvas([])

    def removeFeatures(self):
        self.availableFeaturesLw.clear()
        self.selectedFeaturesLw.clear()

    def populateFeatures(self):
        """Populates the features list from the faceted layer.

        If more than 1000 features are currently visible, the list is truncated
        and a placeholder "..." is appended to ensure performance.
        """
        self.availableFeaturesLw.clear()
        self.selectedFeaturesLw.clear()
        features: QgsFeatureIterator = self._layer.getFeatures()
        too_many_hits = False
        NUM_MAX_HITS = 1000
        if features:
            # safe_disconnect(self.dlg.lw_available.itemSelectionChanged, self.highlight_features)
            for i, feature in enumerate(features):
                item = QListWidgetItem()  # necessary for adding data to the items
                item.setText("{}".format(feature[self._featureLabel]))
                item.setData(Qt.UserRole, feature.id())  # whatever the UserRole is...
                self.availableFeaturesLw.addItem(item)
                if i == NUM_MAX_HITS:  # TODO make proper "constant" and put it somewhere else
                    too_many_hits = True
                    break
            self.availableFeaturesLw.sortItems()
            if too_many_hits:
                placeholder_item = QListWidgetItem(f"... (more than {NUM_MAX_HITS}, please further narrow your filter)")
                placeholder_item.setFlags(placeholder_item.flags() & ~Qt.ItemIsEnabled)
                self.availableFeaturesLw.addItem(placeholder_item)
        else:
            self.removeFeatures()

    def move_all_to_selection(self):
        """Moves *all* available Features into selection."""
        self.move_all_items(self.availableFeaturesLw, self.selectedFeaturesLw)
        self.select_features_on_canvas(self.selected_features_ids())

    def move_selected_to_selection(self):
        """Moves all *selected* available Features into selection."""
        self.move_selected_items(self.availableFeaturesLw, self.selectedFeaturesLw)
        self.select_features_on_canvas(self.selected_features_ids())

    def remove_all_from_selection(self):
        """Removes *all* Features from current selection."""
        self.move_all_items(self.selectedFeaturesLw, self.availableFeaturesLw)
        self._layer.removeSelection()

    def remove_selected_from_selection(self):
        """Removes all *selected* Features from current selection."""
        self.move_selected_items(self.selectedFeaturesLw, self.availableFeaturesLw)
        self.select_features_on_canvas(self.selected_features_ids())

    @staticmethod
    def rename_items(layer: QgsVectorLayer, field: str, listWidget: QListWidget):
        # dirty solution ?
        list = []
        for idx in reversed(range(listWidget.count())):
            item: QListWidgetItem = listWidget.takeItem(idx)
            feature = layer.getFeature(item.data(Qt.UserRole))
            item.setText("{}".format(feature[field]))
            list.append(item)
        listWidget.clear()
        for item in reversed(list):
            listWidget.addItem(item)

    @staticmethod
    def move_all_items(listWidget_a, listWidget_b):
        """Moves all items from one ListWidget to another.

        Args:
            listWidget_a: The originating ListWidget
            listWidget_b: The target ListWidget
        """
        # via https://stackoverflow.com/questions/9713298/pyqt4-move-items-from-one-qlistwidget-to-another
        # sort rows in descending order in order to compensate shifting due to takeItem
        # this also applies to the other methods in this context
        for row in reversed(range(listWidget_a.count())):
            listWidget_b.addItem(listWidget_a.takeItem(row))
        listWidget_b.sortItems()

        # force update, otherwise sometimes it took SECONDS, at least in 3.4
        # FIXME investigate reason and implement proper fix
        QgsApplication.processEvents()

    @staticmethod
    def move_selected_items(listWidget_a, listWidget_b):
        """Moves selected items from one ListWidget to another.

        Args:
            listWidget_a: The originating ListWidget
            listWidget_b: The target ListWidget
        """
        rows = sorted([index.row() for index in listWidget_a.selectedIndexes()], reverse=True)
        for row in rows:
            listWidget_b.addItem(listWidget_a.takeItem(row))
        listWidget_b.sortItems()

        # force update, otherwise sometimes it took SECONDS, at least in 3.4
        # FIXME investigate reason and implement proper fix
        QgsApplication.processEvents()

    def selected_features_ids(self):
        """Returns the IDs of the features currently selected by the user.

        Returns:
            A list of feature IDs
        """
        ids = []
        for row in range(self.selectedFeaturesLw.count()):
            item = self.selectedFeaturesLw.item(row)
            ids.append(item.data(Qt.UserRole))
        return ids

    def select_features_on_canvas(self, ids):
        """Select the features referenced by the supplied IDs on the canvas."""
        # only remove selection if exists, potentially saves a costly redraw
        if self._layer.selectedFeatures():
            self._layer.removeSelection()
        self._layer.select(ids)