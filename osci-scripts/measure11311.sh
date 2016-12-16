#!/usr/bin/env zsh

# ---------------------------------------------------------------------------- #
# DESCRIPTION                                                                  #
# ---------------------------------------------------------------------------- #
# This script executes a set of measurements for
# 1 chip
# at 1 gain setting
# at three sampling frequencies
# for 11 DC voltages on the input
# (hence the name)


# ---------------------------------------------------------------------------- #
# DEPENDENCIES                                                                 #
# ---------------------------------------------------------------------------- #
# The following  python scripts must  be placed in  the same
# directory as this script:
#
# resetWaverunner.py       # reset the oscilloscope
# initWaverunner.py        # initialize the oscilloscope with sane settings
# 33120A.py                # control the function generators for VIN and CLK
# configWaverunner.py      # set various parameters on the osccilloscope
# acquireWaveRunnerData.py # acquire and download data from oscilloscope


# ---------------------------------------------------------------------------- #
# SETTINGS                                                                     #
# ---------------------------------------------------------------------------- #
# Adjust these as needed...
CHIP='chip01'
SIGN='-'
CHANNEL='3'
GAIN='1'
DATA_DIR="data/${CHIP}Gain${SIGN}$(printf '%02d' $GAIN)"


# ---------------------------------------------------------------------------- #
# SETUP AND NOTIFICATIONS                                                      #
# ---------------------------------------------------------------------------- #

# Initialize the osccilloscope
printf 'Initializing oscilloscope...'
#./resetWaverunner.py
#./initWaverunner.py
printf 'Done.\n'
printf 'Manual intervention on oscilloscope required: Set "Max Sample Points" to 500 kS.\n'
printf 'Press Enter to continue'
read
printf 'Manual intervention on oscilloscope required: Clean out trace file directory on oscilloscope.\n'
printf 'Press Enter to continue'
read
printf 'Manual intervention on oscilloscope required: '
printf 'Reset the trace file counter by opening the "File->Save Waveform" dialog and by selecting the appropriate channel.\n'
printf 'This must be done AFTER having cleaned out the trace file directory!\n'
printf 'Press Enter to continue'
read

# ---------------------------------------------------------------------------- #
# CONFIGURATION DATA                                                           #
# ---------------------------------------------------------------------------- #
# These settings are mainly used for the configWaverunner.py script

# Time Bases:
#  32 kHz: 5us
#  96 kHz: 2.5us
# 256 kHz: 1us
declare -A timeDivs
timeDivs[32e3]='5'
timeDivs[96e3]='2.5'
timeDivs[256e3]='1'

declare -A fsStrings
fsStrings[32e3]='032kHz'
fsStrings[96e3]='096kHz'
fsStrings[256e3]='256kHz'

# ----------------------------------
# Display settings for osccilloscope
# ----------------------------------
# NOTE: The  boundaries and  scaling of  the  downloaded data  depend  on  the
# oscilloscope's  display settings,  which is  why we  need these  despite not
# actually caring much about the oscilloscope's display.
# For GAIN +1
# DC Voltage | MVOLT_DIV | OFFSET MV |
#        0.5 |       200 |     -1000 |
#        0.7 |       200 |     -1100 |
#        0.9 |       100 |     -1200 |
#        1.1 |       100 |     -1300 |
#        1.3 |        50 |     -1400 |
#        1.5 |        20 |     -1500 |
#        1.7 |        50 |     -1600 |
#        1.9 |       100 |     -1700 |
#        2.1 |       100 |     -1800 |
#        2.3 |       200 |     -1900 |
#        2.5 |       200 |     -2000 |
# Reverse order of table for GAIN -1

declare -a ampls=(0.5 0.7 0.9 1.1 1.3 1.5 1.7 1.9 2.1 2.3 2.5)

declare -A voltDivs
voltDivs[+0.5]='200'
voltDivs[+0.7]='200'
voltDivs[+0.9]='100'
voltDivs[+1.1]='100'
voltDivs[+1.3]='50'
voltDivs[+1.5]='20'
voltDivs[+1.7]='50'
voltDivs[+1.9]='100'
voltDivs[+2.1]='100'
voltDivs[+2.3]='200'
voltDivs[+2.5]='200'
voltDivs[-0.5]='200'
voltDivs[-0.7]='200'
voltDivs[-0.9]='100'
voltDivs[-1.1]='100'
voltDivs[-1.3]='50'
voltDivs[-1.5]='20'
voltDivs[-1.7]='50'
voltDivs[-1.9]='100'
voltDivs[-2.1]='100'
voltDivs[-2.3]='200'
voltDivs[-2.5]='200'

declare -A offsets
offsets[+0.5]='-1000'
offsets[+0.7]='-1100'
offsets[+0.9]='-1200'
offsets[+1.1]='-1300'
offsets[+1.3]='-1400'
offsets[+1.5]='-1500'
offsets[+1.7]='-1600'
offsets[+1.9]='-1700'
offsets[+2.1]='-1800'
offsets[+2.3]='-1900'
offsets[+2.5]='-2000'
offsets[-0.5]='-2000'
offsets[-0.7]='-1900'
offsets[-0.9]='-1800'
offsets[-1.1]='-1700'
offsets[-1.3]='-1600'
offsets[-1.5]='-1500'
offsets[-1.7]='-1400'
offsets[-1.9]='-1300'
offsets[-2.1]='-1200'
offsets[-2.3]='-1100'
offsets[-2.5]='-1000'


# ---------------------------------------------------------------------------- #
# DO THE STUFF                                                                 #
# ---------------------------------------------------------------------------- #
# Measure ALL the things!!!
i=0
mkdir -p "$DATA_DIR"
for clk in 32e3 96e3 256e3;do
    ./33120A.py --clock=$clk
    sleep 0.25 # give the function generator time to settle
    ./configWaverunner.py --tdiv=${timeDivs[$clk]}

    # Run through DC ramp
    for ampl in "${ampls[@]}";do
        ./33120A.py --voltage="$ampl"
        sleep 0.25
        ./configWaverunner.py --vdiv=${voltDivs[${SIGN}${ampl}]} --offset=${offsets[${SIGN}${ampl}]}
        sleep 2
        printf 'Acquiring trace for %s Hz and %s V\n' $clk $ampl
        ./acquireWaveRunnerData.py \
            --remotefile="C${CHANNEL}Trace$(printf '%05d' $i).txt" \
            --localfile="${DATA_DIR}/${CHIP}-gain${SIGN}$(printf '%02d' ${GAIN})-${fsStrings[$clk]}-${ampl}V.txt"
        i=$((i+1))
    done
done
