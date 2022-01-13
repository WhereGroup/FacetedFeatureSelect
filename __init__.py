# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Faceted Feature Select
                                 A QGIS plugin
 A user-definable faceted feature selection form
                             -------------------
        begin                : 2021-03-03
        copyright            : (C) by WhereGroup GmbH
                               Johannes Kröger, Paul Schmidt
        email                : johannes.kroeger@wheregroup.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load FacetedFeatureSelect class from file facetedfeatureselect.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """

    from .facetedfeatureselect import FacetedFeatureSelect
    return FacetedFeatureSelect(iface)
