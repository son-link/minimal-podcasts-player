from PyQt5 import QtWidgets
from configparser import ConfigParser
from .ui import Ui_config
from .utils import getAppDataDir
from os import path
from qt_material import apply_stylesheet, list_themes
from PyQt5.QtGui import QIcon

config_dir = getAppDataDir()


def getConf():
    config_file = config_dir + 'mpp.ini'
    config = {}

    # Firts check if the config file exists
    if path.exists(config_file):
        parser = ConfigParser()
        parser.read(config_file)
        for name, value in parser.items('mpp'):
            if name == 'update_on_init':
                value = parser.getboolean('mpp', 'update_on_init')
            config[name] = value

    else:
        # If not create a new config file
        home = path.expanduser('~')
        download_dir = path.join(home, 'Downloads')
        parser = ConfigParser()
        parser.add_section('mpp')
        config = {
            'update_on_init': 1,
            'download_folder': download_dir,
            'theme': 'default'
        }
        parser.set('mpp', 'update_on_init', '1')
        parser.set('mpp', 'download_folder', download_dir)
        with open(config_dir + 'mpp.ini', 'w') as configfile:
            parser.write(configfile)

    return config


class configDialog(QtWidgets.QDialog):
    """Employee dialog."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        # Create an instance of the GUI
        self.ui = Ui_config.Ui_configDialog()
        # Run the .setupUi() method to show the GUI
        self.ui.setupUi(self)

        self.ui.buttonBox.accepted.connect(self.saveConf)
        self.ui.buttonBox.rejected.connect(self.resetConf)

        self.conf = getConf()

        if self.conf['update_on_init']:
            self.ui.cbUpdateInit.setChecked(True)
        else:
            self.ui.cbUpdateInit.setChecked(False)

        self.ui.downFolderEdit.setText(self.conf['download_folder'])

        for theme in ['default'] + list_themes():
            self.ui.themeSelector.addItem(theme)

        self.ui.themeSelector.setCurrentText(self.conf['theme'])
        self.ui.themeSelector.currentIndexChanged.connect(self.changeTheme)

    def saveConf(self):
        update_on_init = '0'
        if self.ui.cbUpdateInit.isChecked():
            update_on_init = '1'

        parser = ConfigParser()
        parser.add_section('mpp')
        parser.set('mpp', 'update_on_init', update_on_init)
        parser.set('mpp', 'download_folder', self.ui.downFolderEdit.text())
        parser.set('mpp', 'theme', self.ui.themeSelector.currentText())
        with open(config_dir + 'mpp.ini', 'w') as configfile:
            parser.write(configfile)

        return getConf()

    def changeTheme(self, i):
        theme = self.ui.themeSelector.currentText()
        apply_stylesheet(self.parent, theme=theme)
        if theme.find('dark') != -1:
            QIcon.setThemeName('mpp-dark')
        else:
            QIcon.setThemeName('mpp')

        self.parent.repaint()

    def resetConf(self):
        theme = self.conf['theme']
        apply_stylesheet(self.parent, theme=theme)
