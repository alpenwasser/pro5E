#!/usr/bin/env python3

# 256kHz: time_div: 1us/div
#  96kHz: time_div: 2.5us/div
#  32kHz: time_div: 5us/div

# Max sample points: 100kS

import vxi11
import sys
import getopt
instrIP='169.254.14.189'
CHANNEL='C3'
DATA_DIR='D:\\traces'
TRACE_FILE=CHANNEL + 'Trace00000.txt'
TRACE_FILE_PATH=DATA_DIR + '\\' + TRACE_FILE

class waverunner(object):
    def __init__(self, instrIP):
        self.__gen = vxi11.Instrument(instrIP)
        #print(self.__gen.ask('*IDN?'))

    def store_data(self):
        self.__gen.write('STO ' + CHANNEL + ',HDD')

    def transfer_file(self,remotefile,localfile):
        trace_file_path = DATA_DIR + '\\' + remotefile
        data=self.__gen.ask('TRFL? DISK,HDD,FILE,"' + trace_file_path + '"')
        file=open(localfile,'w')
        # NOTE: data  is a  Windows text string,  split with
        # \n\r.  Its  last line is a  string 'ffffffff' (see
        # LeCroy documentation) This  string is unneeded and
        # interferes with  plotting the data.   We therefore
        # cut  the  last  line  of the  string;  the  8  'f'
        # characters as well as the \n\r part.
        file.write(data[:-10])
        file.close()

    def cleanup(self,remotefile):
        trace_file_path = DATA_DIR + '\\' + remotefile
        self.__gen.write('DELF DISK,HDD,FILE,' + trace_file_path)

def main(argv):
    instr = waverunner(instrIP)
    try:
        opts, args = getopt.getopt(argv,"r:l",["remotefile=","localfile="])
    except getopt.GetoptError:
        sys.exit(2)

    remotefile=''
    localfile=''
    for opt, arg in opts:
        if opt in ("-r", "--remotefile"):
            remotefile=arg
        elif opt in ("-l", "--localfile"):
            localfile=arg

    instr.store_data()
    instr.transfer_file(remotefile,localfile)
    instr.cleanup(remotefile)


if __name__ == '__main__':
    main(sys.argv[1:])
