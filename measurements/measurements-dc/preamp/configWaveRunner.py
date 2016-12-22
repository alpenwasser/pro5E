#!/usr/bin/env python3

import vxi11
import sys
import getopt

# --------------------------------------------------------------------------- #
# DESCRIPTION                                                                 #
# --------------------------------------------------------------------------- #
# Sets  voltage/div,  time/div and  offset  for  a given  oscilloscope  trace.
# Needed for generating  sane display settings so that we  can acquire optimal
# measurement data.

# --------------------------------------------------------------------------- #
# USAGE                                                                       #
# --------------------------------------------------------------------------- #
# Set voltage/div
# ./configWaveRunner.py --vdiv=<value>
# ./configWaveRunner.py -v <value>
# where <value> is a voltage in millivolts
#
# Set time/div
# ./configWaveRunner.py --tdiv=<value>
# ./configWaveRunner.py -t <value>
# where <value> is a time in microseconds
#
# Set offset
# ./configWaveRunner.py --offset=<value>
# ./configWaveRunner.py -o <value>
# where <value> is an offset voltage in millivolts

# --------------------------------------------------------------------------- #
# SETTINGS                                                                    #
# --------------------------------------------------------------------------- #
# The intrument's IP address can be checked on the oscilloscope itself.  Make
# sure you have a LAN connection to it.
INSTR_IP='169.254.14.189'
CHANNEL='C3'

# --------------------------------------------------------------------------- #
# IMPLEMENTATION                                                              #
# --------------------------------------------------------------------------- #
class WaveRunner(object):
    def __init__(self, instr_IP, channel):
        self.__gen = vxi11.Instrument(instr_IP)
        #print(self.__gen.ask('*IDN?')) # For diagnostics
        self.__gen.channel = channel
        self.__gen.write(self.__gen.channel + ':TRACE ON')

    def set_time_div(self,microseconds):
        self.__gen.write(self.__gen.channel + ':TIME_DIV ' + microseconds + 'US')

    def set_volt_div(self,millivolts):
        self.__gen.write(self.__gen.channel + ':VOLT_DIV ' + millivolts + 'MV')

    def set_offset(self,millivolts):
        self.__gen.write(self.__gen.channel + ':OFFSET ' + millivolts + 'MV')

def main(argv):
    instr = WaveRunner(INSTR_IP,CHANNEL)
    try:
        opts, args = getopt.getopt(argv,"t:v:o",["tdiv=","vdiv=","offset="])
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-t", "--tdiv"):
            instr.set_time_div(arg)
        elif opt in ("-v", "--vdiv"):
            instr.set_volt_div(arg)
        elif opt in ("-o", "--offset"):
            instr.set_offset(arg)

if __name__ == '__main__':
    main(sys.argv[1:])
