#!/usr/bin/env python3

# 256kHz: time_div: 1us/div
#  96kHz: time_div: 2.5us/div
#  32kHz: time_div: 5us/div

import vxi11
import sys
import getopt
instrIP='169.254.14.189'

class waverunner(object):
    def __init__(self, instrIP):
        self.__gen = vxi11.Instrument(instrIP)
        #print(self.__gen.ask('*IDN?'))
        self.__gen.write('C3:TRACE ON')

    def set_time_div(self,microseconds):
        self.__gen.write('C3:TIME_DIV ' + microseconds + 'US')

    def set_volt_div(self,millivolts):
        self.__gen.write('C3:VOLT_DIV ' + millivolts + 'MV')

    def set_offset(self,millivolts):
        self.__gen.write('C3:OFFSET ' + millivolts + 'MV')

def main(argv):
    instr = waverunner(instrIP)
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
