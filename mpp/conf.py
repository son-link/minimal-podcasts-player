from PyQt5 import QtWidgets
from configparser import ConfigParser
from .ui import Ui_config
from .utils import getAppDataDir, isLinux
from os import path, execl
from qt_material import apply_stylesheet, list_themes
from PyQt5.QtGui import QIcon
import sys

config_dir = getAppDataDir()
default_theme = 'system'
if not isLinux():
    default_theme = 'default'


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
            'theme': default_theme
        }
        parser.set('mpp', 'update_on_init', '1')
        parser.set('mpp', 'download_folder', download_dir)
        parser.set('mpp', 'theme', default_theme)
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
        self.current_theme = self.conf['theme']

        if self.conf['update_on_init']:
            self.ui.cbUpdateInit.setChecked(True)
        else:
            self.ui.cbUpdateInit.setChecked(False)

        self.ui.downFolderEdit.setText(self.conf['download_folder'])

        if isLinux():
            self.ui.themeLabel.setHidden(True)
            self.ui.themeSelector.setHidden(True)
        else:
            themes = ['default'] + list_themes()
            for theme in themes:
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

        theme = self.ui.themeSelector.currentText()
        if theme == 'system' and self.current_theme != 'system':
            execl(sys.executable, sys.executable, *sys.argv)

        return getConf()

    def changeTheme(self, i):
        theme = self.ui.themeSelector.currentText()
        apply_stylesheet(self.parent, theme=theme)
        if theme.find('light') != -1:
            QIcon.setThemeName('mpp')
        else:
            QIcon.setThemeName('mpp-dark')

        self.parent.repaint()

    def resetConf(self):
        theme = self.conf['theme']
        apply_stylesheet(self.parent, theme=theme)
