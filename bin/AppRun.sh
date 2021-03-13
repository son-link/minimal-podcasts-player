#! /bin/bash

this_dir=$(dirname "$0")
export PATH="$PATH":"$this_dir"/usr/bin
export SSL_CERT_FILE="$this_dir"/usr/conda/ssl/cert.pem
export APPIMAGE=1
"$this_dir"/usr/bin/python "$this_dir"/usr/bin/minimal-podcasts-player  "$@"
