### 0.1.1

* Fixed a bug when the next button was not deactivated at the end of the playback queue.
* Now you can change between the Qt-Material themes. For the moment I haven't been able to change one of them to the system one without having to restart the program.
* Now you can add a podcast on Ivoox by entering its address, for example: https://www.ivoox.com/podcast-salmorejo-geek_sq_f1206500_1.html
* Clean code.

### 0.2.0

* Now when sending HTTP requests to the feeds a valid User Agent is sent in the header, because some websites may return the error code 403, mainly because the one sent by default the server detects it as a bot which does not support. This solved this issue: https://github.com/son-link/minimal-podcasts-player/issues/1
* Add some icons.
* Now the icons change on change theme between light and dark palettes.
* Other minos changes.

### 0.3.0

* Fix a error on generate the default app config.
* Drop the theme selector and qt-material as dependence. The AppIMage and Windows now use the Fusion theme.
* The mpp and mpp-dark icons have been removed, now the Windows icons and the AppImage use a customized version of the [KDE's Breeze icon theme](https://github.com/KDE/breeze-icons).
* A submenu has been added in the podcast listing with an option: unsubscribe from the podcast you click on.
* The episode download system has begun to be implemented. **Note**: at the moment only one download at a time.
* New functions have been added within utils:
	* isWindons: return True is the applications runs under Windows.
	* isBSD: return True is the applications runs under FreeBSD (not tested on other BSD-based systems).
	* downloadCover: Download the Podcast's cover.
	* coverExist: Check if the cover exists, is not, download it again.

* A two new fields, **coverUrl** and **filename**, has been added to the podcasts and episodes tables respectively in the database:
  * coverUrl: The url of the podcast's cover, in case it is necessary to download it again in the future (for example the cache has been cleared).
  * filename: The path to the audio if downloaded, to play it instead of streaming it.

**NOTE:** Because of these 2 new columns it is necessary to update the database, so the program takes a little longer to start, depending on the number of podcasts you have subscribed to.

* Now is posible download the episodes and added two news options for this.
* Other minor changes, corrections and performance.

### 0.3.1

* Solved some problems when clicking the add podcast button and the field is empty, the url is not valid or it is valid but does not contain an RSS Feed.
* Remove the ? button in the window title on Add Podcast and Configure dialogs.
* slightly increased the text size in the title of the podcast and the episode being played back.
* The positions of the volume and options menu buttons have been exchanged.
* Add some translations.
* Thanks to David Linares, member of SystemInside's Telegram group for report the bug and provide several ideas.

### 0.4.0

* New player layout.
* Add option in episodes list for add more downloads.
* Replace illegal characters in filename on downloads.
* Added pagination
* You can change track on queue with double click.
* You can now start playing an episode by double clicking on the listing.
* Remove episode info when changing episodes.

### 0.4.1

* Added a system tray icon, their menu and show/hide the main window.
* Now when closing the main window, a dialog will be displayed to confirm the closure, minimice it to the system tray icon or cancel the closure. Within the options you can disable this dialog.
* Add two new icons and some translations.
* Several modifications to make the code more readable and several comments added and modified.
* Add About dialog.
