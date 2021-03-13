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