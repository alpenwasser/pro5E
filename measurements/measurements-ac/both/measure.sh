#!/usr/bin/env bash

#!/bin/sh
ssh -p 22 pi@10.84.130.16 'cd bitstream/build && sudo ./bitstream'
scp -P 22 pi@10.84.130.16:/home/pi/bitstream/build/bit_stream.txt bit_stream.txt
#cp bit_stream.txt data/chip1/bit_stream-$1.txt
python3 bitstream.py
