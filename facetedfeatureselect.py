import os.path
from qgis.core import QgsProject
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.PyQt.QtCore import QT_VERSION_STR

# Initialize Qt resources from file resources.py
from .resources import *

from .facetedfeatureselect_dialog import *
from .start_confirm_dialog import StartConfirmDialog


class FacetedFeatureSelect:
    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'FacetedFeatureSelect_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Faceted Feature Select')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        # noinspection PyMethodMayBeStatic

    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Faceted Feature Select', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = ':/plugins/flurstueckssuche/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Faceted Feature Select'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&Faceted Feature Select'),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        # quick and dirty Qt version check
        if QT_VERSION_STR < "5.12":
            QMessageBox.warning(
                self.iface.mainWindow(),
                'Unsupported Qt Version',
                f"The Faceted Feature Select Plugin requires Qt version 5.12 or later. Your Qt is {QT_VERSION_STR}.",
                QMessageBox.Ok
            )
            return

        # Check selections
        selected = False
        for layerName in QgsProject.instance().mapLayers():
            layer = QgsProject.instance().mapLayer(layerName)
            if isinstance(layer, QgsVectorLayer) and len(layer.selectedFeatures()) > 0:
                selected = True
                break
        if selected:
            dlg = StartConfirmDialog()
            dlg.setWindowTitle("!!!")
            # dlg.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            if dlg.exec_():
                for layerName in QgsProject.instance().mapLayers():
                    layer = QgsProject.instance().mapLayer(layerName)
                    if isinstance(layer, QgsVectorLayer) and len(layer.selectedFeatures()) > 0:
                        layer.removeSelection()
                self._start()
        else:
            self._start()

    def _start(self):
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = FacetedFeatureSelectDialog()

        self.dlg.show()
        self.dlg.initSelection()

