#!/usr/bin/env bash

# ---------------------------------------------------------------------------- #
# DESCRIPTION                                                                  #
# ---------------------------------------------------------------------------- #
# This script executes a set of measurements for
# 1 chip
# at three sampling frequencies
# for 11 DC voltages on the input
# (hence the name)

# ---------------------------------------------------------------------------- #
# USAGE                                                                        #
# ---------------------------------------------------------------------------- #
# Configure the settings down below and execute:
# ./measure--1-3-11.sh
# The oscilloscope will require some manual intervention at the beginning, for
# which this script will prompt you  before continuing. So don't just start it
# and run off to get coffee.

# ---------------------------------------------------------------------------- #
# DEPENDENCIES                                                                 #
# ---------------------------------------------------------------------------- #
# The following  python scripts must  be placed in  the same
# directory as this script:
#
# 33120A.py                # control the function generators for VIN and CLK

# ---------------------------------------------------------------------------- #
# SETTINGS                                                                     #
# ---------------------------------------------------------------------------- #
# Adjust these as needed...
CHIP='chip10'
DATA_DIR="data-ac/${CHIP}"

# ---------------------------------------------------------------------------- #
# SETUP AND NOTIFICATIONS                                                      #
# ---------------------------------------------------------------------------- #

IFS='' read -r -d '' chip_msg <<-EOF
	Chip and Gain Selection
	========================================================
	Measuring ${CHIP}
EOF
IFS='' read -r -d '' good_to_go <<-'EOF'
	Commencing Automated Measuring
	========================================================
	No further manual intervention is required from here on.
	We recommend grabbing a cup of coffee or something like 
	that.
	                          {
	                       }   }   {
	                      {   {  }  }
	                       }   }{  {
	                      {  }{  }  }
	                     ( }{ }{  { )
	                    .-{   }   }-.
	                    ( ( } { } { } )
	                    |`-.._____..-'|
	                    |             ;--.
	                    |   (__)     (__  \
	                    |   (oo)      | )  )
	                    |    \/       |/  /
	                    |             /  /
	                    |            (  /
	                    \             y'
	                    `-.._____..-'
	
EOF
#(Design by Felix Lee, http://www.ascii-art.de/ascii/c/coffee.txt)

# Initialize the osccilloscope

printf '%s\n%s' "$chip_msg" "$good_to_go"

# ---------------------------------------------------------------------------- #
# CONFIGURATION DATA                                                           #
# ---------------------------------------------------------------------------- #

declare -A fsStrings
fsStrings[32e3]='032kHz'
fsStrings[96e3]='096kHz'
fsStrings[256e3]='256kHz'

declare -a ampls=(\
    0.8\
	1.2\
	1.6\
	2.0\
)

declare -a freqs=(\
	16\
	32\
	64\
	128\
	256\
	512\
	768\
	1024\
	1536\
	2048\
	3072\
	4096\
)

# ---------------------------------------------------------------------------- #
# DO THE STUFF                                                                 #
# ---------------------------------------------------------------------------- #
# Measure ALL the things!!!
mkdir -p "$DATA_DIR"
for clk in 32e3 96e3 256e3;do
    ./33120A.py --clock=$clk
    # Give the function generator time to settle:
    sleep 0.25 

    # Run through DC ramp
    for ampl in "${ampls[@]}";do
		for freq in "${freqs[@]}";do
			./33120A.py --sine-amplitude="$ampl" --sine-frequency="$freq"
			sleep 0.25

			printf 'Acquiring trace:\n\tfs =  %s Hz\n\tf_in = %s Hz\n\tVPP = %s V\n' $clk $freq $ampl
			local_file="${DATA_DIR}/${CHIP}-${fsStrings[$clk]}-$(printf '%04d' ${freq})Hz-${ampl}VPP.txt"
			ssh -p 22 pi@10.84.130.16 'cd bitstream/build && sudo ./bitstream'
			scp -P 22 \
				pi@10.84.130.16:/home/pi/bitstream/build/bit_stream.txt \
				"$local_file"
		done
    done
done
