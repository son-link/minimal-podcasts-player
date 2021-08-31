from PyQt5 import QtWidgets
from configparser import ConfigParser
from .ui import Ui_config
from .utils import getAppDataDir
from os import path
from PyQt5.QtCore import QCoreApplication, Qt

config_dir = getAppDataDir()
_translate = QCoreApplication.translate


def getConf():
    """Get and return the configuration"""
    config_file = config_dir + 'mpp.ini'
    config = {}

    # First check if the config file exists
    if path.exists(config_file):
        parser = ConfigParser()
        parser.read(config_file)
        for name, value in parser.items('mpp'):
            if name == 'update_on_init':
                value = parser.getboolean('mpp', 'update_on_init')
            if name == 'rename_download':
                value = parser.getboolean('mpp', 'rename_download')
            if name == 'disable_quit_dialog':
                value = parser.getboolean('mpp', 'disable_quit_dialog')
            if name == 'episodes_per_page':
                value = parser.getint('mpp', 'episodes_per_page')
            config[name] = value
        if 'disable_quit_dialog' not in config:
            config['disable_quit_dialog'] = False
        if 'episodes_per_page' not in config:
            config['episodes_per_page'] = 20
    else:
        # If not create a new config file
        home = path.expanduser('~')
        download_dir = path.join(home, 'Downloads')
        parser = ConfigParser()
        parser.add_section('mpp')
        config = {
            'update_on_init': 1,
            'rename_download': 0,
            'download_folder': download_dir,
            'disable_quit_dialog': 0,
            'episodes_per_page': 20
        }
        parser.set('mpp', 'update_on_init', '1')
        parser.set('mpp', 'rename_download', '0')
        parser.set('mpp', 'download_folder', download_dir)
        parser.set('mpp', 'disable_quit_dialog', '0')
        parser.set('mpp', 'episodes_per_page', '20')
        with open(config_dir + 'mpp.ini', 'w') as configfile:
            parser.write(configfile)

    return config


class configDialog(QtWidgets.QDialog):
    """Show the config dialog"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        # Create an instance of the GUI
        self.ui = Ui_config.Ui_configDialog()
        # Run the .setupUi() method to show the GUI
        self.ui.setupUi(self)
        self.setWindowFlags(
            Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowTitleHint
        )

        self.ui.buttonBox.accepted.connect(self.saveConf)
        self.ui.selDownFolder.clicked.connect(self.selDownFolder)

        self.conf = getConf()

        if self.conf['update_on_init']:
            self.ui.cbUpdateInit.setChecked(True)
        else:
            self.ui.cbUpdateInit.setChecked(False)

        if 'rename_download' in self.conf and self.conf['rename_download']:
            self.ui.cbRenameDown.setChecked(True)
        else:
            self.ui.cbRenameDown.setChecked(False)

        if ('disable_quit_dialog' in self.conf and
                self.conf['disable_quit_dialog']):
            self.ui.cbDisableClose.setChecked(True)
        else:
            self.ui.cbDisableClose.setChecked(False)

        if 'episodes_per_page' in self.conf and self.conf['episodes_per_page']:
            self.ui.spinEpisPerPage.setValue(self.conf['episodes_per_page'])

        self.ui.downFolderEdit.setText(self.conf['download_folder'])

    def saveConf(self):
        """Save the config"""
        update_on_init = '0'
        rename_download = '0'
        disable_quit_dialog = '0'
        if self.ui.cbUpdateInit.isChecked():
            update_on_init = '1'

        if self.ui.cbRenameDown.isChecked():
            rename_download = '1'

        if self.ui.cbDisableClose.isChecked():
            disable_quit_dialog = '1'

        parser = ConfigParser()
        parser.add_section('mpp')
        parser.set('mpp', 'update_on_init', update_on_init)
        parser.set('mpp', 'rename_download', rename_download)
        parser.set('mpp', 'download_folder', self.ui.downFolderEdit.text())
        parser.set('mpp', 'disable_quit_dialog', disable_quit_dialog)
        parser.set('mpp', 'episodes_per_page', str(self.ui.spinEpisPerPage.value()))
        with open(config_dir + 'mpp.ini', 'w') as configfile:
            parser.write(configfile)

        return getConf()

    def selDownFolder(self):
        """Show the open file dialog for select the download folder"""
        folder = str(
            QtWidgets.QFileDialog.getExistingDirectory(
                self,
                _translate('MainWindow', 'Select downloads folder')
            )
        )
        if folder:
            self.ui.downFolderEdit.setText(folder)
