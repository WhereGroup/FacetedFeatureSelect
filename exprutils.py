from abc import ABC
from qgis.core import QgsVectorLayer, QgsExpression, QgsField, QgsFieldProxyModel
from PyQt5.QtCore import Qt, QVariant, QLocale
from PyQt5.QtWidgets import QLineEdit, QCompleter
from PyQt5.QtGui import QDoubleValidator

# operators
OP_CONTAINS = "Contains"
OP_STARTSWITH = "Starts with"
OP_ENDSWITH = "Ends with"
OP_EQUALS = "Equals"
OP_NEQUALS = "Not equals"
OP_LT = "<"
OP_GT = ">"
OP_LTE = "<="
OP_GTE = ">="
OP_EQ = "="
OP_NEQ = "!="
OP_SUBSTR = "Substr"


class ExprUtils(ABC):

    @staticmethod
    def isFieldNumeric(field: QgsField):
        if field.type() == QgsFieldProxyModel.Numeric or field.type() == QgsFieldProxyModel.Int or field.type() == QgsFieldProxyModel.Double or field.type() == QgsFieldProxyModel.LongLong:
            return True
        else:
            return False

    @staticmethod
    def isFieldString(field: QgsField):
        if field.type() == QVariant.String:
            return True
        else:
            return False

    @staticmethod
    def supportedTypes():
        return QgsFieldProxyModel.Numeric | QgsFieldProxyModel.Int | QgsFieldProxyModel.Double | QgsFieldProxyModel.LongLong | QgsFieldProxyModel.String

    @staticmethod
    def aggrExpr(field: str, useOrderBy: bool = True):
        """This is for the list of feature ids/names/whatever in the result view?"""
        #return f'array_distinct("{field}")'  # nope, reicht nicht... da kommt nur der wert von einem feature...

        if useOrderBy:
            return "array_distinct(array_agg(\"{}\", order_by := \"{}\"))".format(field, field)
        else:
            return "array_distinct(array_agg(\"{}\"))".format(field)

    @staticmethod
    def listOps(field: QgsField):
        if ExprUtils.isFieldNumeric(field):
            return [OP_EQ, OP_NEQ, OP_LT, OP_LTE, OP_GT, OP_GTE]
        elif ExprUtils.isFieldString(field):
            return [OP_CONTAINS, OP_EQUALS, OP_NEQUALS, OP_STARTSWITH, OP_ENDSWITH]
        else:
            raise Exception()

    @staticmethod
    def searchExpr(operator: str, field: QgsField):
        expr = ""
        sens = Qt.CaseInsensitive;
        mode = Qt.MatchContains
        if operator == OP_STARTSWITH:
            mode = Qt.MatchStartsWith
            expr = "\"{}\" LIKE '[%{}%]%'"
        elif operator == OP_CONTAINS:
            expr = "\"{}\" LIKE '%[%{}%]%'"
        elif operator == OP_ENDSWITH:
            mode = Qt.MatchEndsWith
            expr = "\"{}\" LIKE '%[%{}%]'"
        elif operator == OP_EQUALS:
            mode = Qt.MatchExactly
            expr = "\"{}\"='[%{}%]'"
        elif operator == OP_NEQUALS:
            mode = Qt.MatchExactly
            expr = "\"{}\"!='[%{}%]'"
        elif operator == OP_EQ:
            expr = "\"{}\"=[%{}%]"
        elif operator == OP_NEQ:
            expr = "\"{}\"!=[%{}%]"
        elif operator == OP_LT:
            expr = "\"{}\"<[%{}%]"
        elif operator == OP_LTE:
            expr = "\"{}\"<=[%{}%]"
        elif operator == OP_GT:
            expr = "\"{}\">[%{}%]"
        elif operator == OP_GTE:
            expr = "\"{}\">=[%{}%]"
        else:
            raise Exception()
        return (sens, mode, QgsExpression(expr.format(field.name(), field.name())))

    @staticmethod
    def mapList(field: QgsField, list: list):
        """Convert values in list to str (if not string already)?"""
        if field.type() != QgsFieldProxyModel.String:
            return map(lambda x: str(x), list)
        return list

    @staticmethod
    def initSearchField(field: QgsField, search: QLineEdit, layer: QgsVectorLayer, locale: QLocale):
        """Prepares the validator (for numeric fields) or the auto completer (for string fields).

        For validation a maximum of 1000 match suggestions are provided to ensure performance.
        """
        if ExprUtils.isFieldNumeric(field):
            qdv = QDoubleValidator()
            search.setLocale(locale)
            qdv.setLocale(locale)
            qdv.setNotation(QDoubleValidator.StandardNotation)
            search.setValidator(qdv)
        elif ExprUtils.isFieldString(field):
                #list = QgsVectorLayerUtils.getValues(layer, aggrExpr)  # # array_distinct(array_agg("identifier", order_by := "identifier") -> Tuple[List[Any], bool]

                # viel schneller als die expression
                field_index = layer.fields().indexOf(f"{field.name()}")
                unique_values = sorted(layer.uniqueValues(field_index))

                NUM_MAX_HITS = 1000  # TODO make proper "constant" and put it somewhere else
                if unique_values:
                    if len(unique_values) > NUM_MAX_HITS:
                        pass  # not creating an autocompleter
                    else:
                        completer = QCompleter(ExprUtils.mapList(field, unique_values))
                        search.setCompleter(completer)
        else:
            raise Exception()

    @staticmethod
    def initSearchExpr(field: QgsField, search: QLineEdit, operator: str):
        if ExprUtils.isFieldNumeric(field):
            sens, mode, expr = ExprUtils.searchExpr(operator, field)
            return expr
        elif ExprUtils.isFieldString(field):
            sens, mode, expr = ExprUtils.searchExpr(operator, field)
            if search.completer() is not None:
                search.completer().setCaseSensitivity(sens)
                search.completer().setFilterMode(mode)
            return expr
        else:
            raise Exception()

    @staticmethod
    def value(field: QgsField, search: QLineEdit):
        if ExprUtils.isFieldNumeric(field):
            doubleVal, isDouble = search.locale().toDouble(search.text())
            if isDouble:
                return doubleVal
            else:
                return False
        elif ExprUtils.isFieldString(field):
            return search.text()
        else:
            raise Exception()
