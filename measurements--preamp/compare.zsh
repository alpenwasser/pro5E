#!/usr/bin/env zsh

# --------------------------------------------------------------------------- #
# DESCRIPTION                                                                 #
# --------------------------------------------------------------------------- #
# Small helper script to quickly evaluate a measurement run for one chip at
# one gain setting.

# --------------------------------------------------------------------------- #
# USAGE                                                                       #
# --------------------------------------------------------------------------- #
# ./compare.zsh <chip number> <gain>
# EXAMPLE: Look at the plots for chip 08 for gain +4
# ./compare.zsh 08 +04

# --------------------------------------------------------------------------- #
# IMPLEMENTATION                                                              #
# --------------------------------------------------------------------------- #
chip="$1"
gain="$2"

./plotComparison.py data/"chip${chip}Gain${gain}"/*032kHz* &
./plotComparison.py data/"chip${chip}Gain${gain}"/*096kHz* &
./plotComparison.py data/"chip${chip}Gain${gain}"/*256kHz* &
