from abc import ABC
from qgis.core import QgsVectorLayer, QgsExpression
from .facet_widget import FacetWidget


class FacetedSearch(ABC):

    def __init__(self):
        self._widgets = []
        self._layer: QgsVectorLayer = None

    def setLayer(self, layer: QgsVectorLayer):
        self._layer = layer
        self._widgets = []

    def setWidgets(self, widgets: []):
        self._widgets = widgets
        self._disableSelectWidgets(0)
        if self._layer.subsetString():
            self._layer.setSubsetString("")
        if len(self._widgets) > -1:
            self._enableSelectWidget(0)

    def _enableSelectWidget(self, idx: int):
        if idx < len(self._widgets):
            widget: FacetWidget = self._widgets[idx]
            widget.disable(False)
            widget.reset(self._layer)

    def _disableSelectWidgets(self, start: int):
        for idx in range(start, len(self._widgets), 1):
            fw: FacetWidget = self._widgets[idx]
            fw.disable(True)
            fw.clear()

    def search(self, idx: int):
        self._disableSelectWidgets(idx + 1)
        subset: str = self._subsetFor(idx)
        self._layer.setSubsetString(subset)
        self._enableSelectWidget(idx + 1)

    def _subsetFor(self, idx: int):
        subsets = []
        for i in range(0, idx + 1, 1):
            widget: FacetWidget = self._widgets[i]
            if widget.value() is None or widget.value() == "":
                break
            searchExpr: QgsExpression = widget.searchExpr().expression()
            newExpr = QgsExpression(searchExpr.replace("[%{}%]".format(widget.field()), widget.value()))
            expr: str = "({})".format(newExpr.expression())
            subsets.append(expr)
        return " and ".join(subsets)
