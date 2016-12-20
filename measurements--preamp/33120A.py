#!/usr/bin/env python3

import serial
import struct
import sys
import getopt

# --------------------------------------------------------------------------- #
# DESCRIPTION                                                                 #
# --------------------------------------------------------------------------- #
# Controls two 33120A  arbitrary function generators via  RS232 connection and
# USB adapter. One of  the generators is used  to output a square  wave (to be
# used as the clock) between 0V and  3V, the other generator is used to output
# a DC signal.

# --------------------------------------------------------------------------- #
# USAGE                                                                       #
# --------------------------------------------------------------------------- #
# ./33120A.py --clock=<frequency>
# ./33120A.py -c <frequency>
# Set the CLK generator's frequency. <frequency> is a value in Hertz.
# Example: Set square wave frequency to 96 kHz
# ./33120A.py -c 96e3

# ./33120A.py --voltage=<voltage>
# ./33120A.py -v <voltage>
# Set the other generator to output a DC voltage of <voltage>. <voltage> is
# a value in Volts.
# Example: Set a DC voltage of 0.9V:
# ./33120A.py -v 0.9

# --------------------------------------------------------------------------- #
# SETTINGS                                                                    #
# --------------------------------------------------------------------------- #
CLK_DEVICE = '/dev/ttyUSB1'
DC_DEVICE  = '/dev/ttyUSB0'

# --------------------------------------------------------------------------- #
# IMPLEMENTATION                                                              #
# --------------------------------------------------------------------------- #
class FunctionGenerator(object):
    def __init__(self, device):
        self.__gen = serial.Serial(
            port=device,
            baudrate=9600,
            timeout=1,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_TWO,
            bytesize=serial.EIGHTBITS
        )
        self.__gen.write(b'OUTP:LOAD INF\n')

    def set_dc(self, voltage):
        self.__gen.write(bytes('APPL:DC DEF, DEF, {} V\n'.format(voltage), 'ascii'))

    def set_clk(self, freq):
        self.__gen.write(bytes('APPL:SQU {} HZ, 3 VPP, 1.5 V\n'.format(freq), 'ascii'))

    def set_sin(self, frequency, vpp, offset):
        self.__gen.write(bytes('APPL:SIN {} HZ, {} VPP, {} V\n'.format(frequency, vpp, offset), 'ascii'))


def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hc:v:",["help","clock=","voltage="])
    except getopt.GetoptError:
        print('33120A.py -c <clock frequency> -v <input voltage>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('33120A.py -c <clock frequency> -v <input voltage>')
            sys.exit(0)
        elif opt in ("-c", "--clock"):
            fgClk = FunctionGenerator(CLK_DEVICE)
            fgClk.set_clk(arg)
        elif opt in ("-v", "--voltage"):
            fgVin = FunctionGenerator(DC_DEVICE)
            fgVin.set_dc(float(arg))

if __name__ == '__main__':
    main(sys.argv[1:])
