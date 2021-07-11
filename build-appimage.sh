#!/usr/bin/env bash

# Remove AppDir
rm -r AppDir

# Grab AppImageTools
wget -nc "https://raw.githubusercontent.com/TheAssassin/linuxdeploy-plugin-conda/master/linuxdeploy-plugin-conda.sh"
wget -nc "https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage"
wget -nc "https://github.com/AppImage/AppImageKit/releases/download/12/appimagetool-x86_64.AppImage"
chmod +x linuxdeploy-x86_64.AppImage linuxdeploy-plugin-conda.sh appimagetool-x86_64.AppImage

# Install App

# Set Environment
export CONDA_CHANNELS='local;conda-forge'
export PIP_REQUIREMENTS='pyqt5 podcastparser .'
export PIP_WORKDIR="$REPO_ROOT"
export VERSION=0.3.1

# Deploy
./linuxdeploy-x86_64.AppImage \
   --appdir AppDir \
    -i bin/io.sonlink.mpp.png \
    -d bin/io.sonlink.mpp.desktop \
    --plugin conda \
    --custom-apprun bin/AppRun.sh \
    --output appimage
