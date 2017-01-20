#!/usr/bin/env python3

import vxi11
import sys
import getopt

# ----------------------------------------------------------------------- #
# DESCRIPTION                                                             #
# ----------------------------------------------------------------------- #
# Acquires, stores and downloads measurement  data from the oscilloscope to
# the controlling computer. Removes files on oscilloscope after download.

# ----------------------------------------------------------------------- #
# USAGE                                                                   #
# ----------------------------------------------------------------------- #
# ./acquireWaveRunnerData.py \
#     -channel=<channel> \
#     --remotefile=<remotefile> \
#     --localfile=<localfile>
# Where:
#
# <remotefile>:  the  filename  which  is  used  by  the  oscilloscope  for
# storing  a   waveform  on   its  HDD. This  will   usually  be   of  form
# <ch>Trace<number>.txt,  for   example  C1Trace00001.txt  for   the  first
# waveform for the first channel.
#
# NOTE: This cannot be configured remotely,  the filename is merely used to
# tell the script  which remote file to download  from the oscilloscope. If
# the  oscilloscope's  filename  iterator  and  the  script's  <remotefile>
# parameter  are  not  in  sync,  the  download  will  fail. Resetting  the
# oscilloscope's counter  requires manual intervention on  the oscilloscope
# via the "File->Save Waveform" dialog.
#
# <localfile>: The   filename  to   be  used   for  storing   the  waveform
# on    the    computer    onto   which    it    is    downloaded. Example:
# chip01-gain+01-256kHz-1.9V.txt
#
# <channel>: The channel for which a waveform is to be stored.
#
# EXAMPLES:
# ./acquireWaveRunnerData.py \
#     --channel=C2 \
#     --remotefile=C2Trace00000.txt \
#     --localfile=trace1.txt
# or in short form:
# ./acquireWaveRunnerData.py -c C2 -r C2Trace00000.txt -l trace1.txt

# ----------------------------------------------------------------------- #
# SETTINGS                                                                #
# ----------------------------------------------------------------------- #
instrIP='169.254.14.189'
# CHANNEL='C3'
# Data directory on the oscilloscope.
# NOTE: This must also  be configured via the  "File->Save Waveform" dialog
# on  the oscilloscope  itself;  merely  setting it  remotely  will not  be
# sufficient.
DATA_DIR='D:\\traces'

# ----------------------------------------------------------------------- #
# IMPLEMENTATION                                                          #
# ----------------------------------------------------------------------- #
class waverunner(object):
    def __init__(self, instrIP):
        self.__gen = vxi11.Instrument(instrIP)
        #print(self.__gen.ask('*IDN?'))

    def store_data(self,channel):
        self.__gen.write('STO ' + channel + ',HDD')

    def transfer_file(self,remotefile,localfile):
        trace_file_path = DATA_DIR + '\\' + remotefile
        data=self.__gen.ask('TRFL? DISK,HDD,FILE,"' + trace_file_path + '"')
        file=open(localfile,'w')
        # NOTE: data is a  Windows text string; newlines are
        # represented by  \n\r.  Its  last line is  a string
        # 'ffffffff' (see LeCroy documentation). This string
        # is  unneeded and  interferes  with processing  the
        # data.   We therefore  cut  off  the string's  last
        # line: the  8 'f'  characters as  well as  the \n\r
        # part.
        file.write(data[:-10])
        file.close()

    def cleanup(self,remotefile):
        trace_file_path = DATA_DIR + '\\' + remotefile
        self.__gen.write('DELF DISK,HDD,FILE,' + trace_file_path)

def main(argv):
    instr = waverunner(instrIP)
    try:
        opts, args = getopt.getopt(
            argv,"c:r:l",["channel=","remotefile=","localfile="])
    except getopt.GetoptError:
        sys.exit(2)

    remotefile = ''
    localfile  = ''
    channel    = ''
    for opt, arg in opts:
        if opt in ("-r", "--remotefile"):
            remotefile=arg
        elif opt in ("-l", "--localfile"):
            localfile=arg
        elif opt in ("-c", "--channel"):
            channel=arg

    instr.store_data(channel)
    instr.transfer_file(remotefile,localfile)
    instr.cleanup(remotefile)


if __name__ == '__main__':
    main(sys.argv[1:])
