#!/usr/bin/env python3

import serial
import struct
import sys
import getopt

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
        #self.__gen.write(bytes('APPL:SQU 1E-4 HZ, {} VPP, {} V\n'.format(voltage, voltage/2), 'ascii'))
        self.__gen.write(bytes('APPL:DC DEF, DEF, {} V\n'.format(voltage), 'ascii'))

    def set_clk(self, freq):
        self.__gen.write(bytes('APPL:SQU {} HZ, 3 VPP, 1.5 V\n'.format(freq), 'ascii'))

    def set_sin(self, frequency, vpp, offset):
        self.__gen.write(bytes('APPL:SIN {} HZ, {} VPP, {} V\n'.format(frequency, vpp, offset), 'ascii'))


def main(argv):
    try:
        opts, args = getopt.getopt(argv,"h:c:v:",["help","clock=","voltage="])
    except getopt.GetoptError:
        print('33120A.py -c <clock frequency> -v <input voltage>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('33120A.py -c <clock frequency> -v <input voltage>')
            sys.exit(0)
        elif opt in ("-c", "--clock"):
            fgClk = FunctionGenerator('/dev/ttyUSB1')
            fgClk.set_clk(arg)
        elif opt in ("-v", "--voltage"):
            fgVin = FunctionGenerator('/dev/ttyUSB0')
            fgVin.set_dc(float(arg))

if __name__ == '__main__':
    main(sys.argv[1:])
