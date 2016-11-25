#!/bin/sh
ssh pi@10.84.130.16 'cd bitstream/build && sudo ./bitstream'
scp pi@10.84.130.16:/home/pi/bitstream/build/bit_stream.txt bit_stream.txt
#cp bit_stream.txt measurements/16-11-25/bit_stream-$1.txt
python bitstream.py
