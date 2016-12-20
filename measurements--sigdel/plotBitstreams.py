#!/usr/bin/env python3

import csv
import sys
import getopt
import numpy as np
import deltasigma as ds
from matplotlib import pyplot as plt

class SigDelPlot(object):
    def __init__(self):
        # Initialize with default values.
        self.__Vmin = 0.0                      # Minimum absolute possible input
        self.__Vmax = 3.0                      # Maximum absolute possible input
        self.__Vref = 1.5                      # Relative Vref
        self.__Vgnda = 1.5                     # Absolute analog ground
        self.__Vin_min = 0.                    # Minimum absolute used input
        self.__Vin_max = 3.                    # Maximum absolute used input
        self.__fs = 256.0e3                    # Sampling frequency (SD-modulator)
        self.__Ts = 1/self.__fs                # Sampling period
        self.__T_SaH = self.__Ts*512           # Input signal sampling period (S/H-block)
        self.__Nbit  = 12                      # Bit accuracy (for LSB/2 plot)
        self.__NORM_FACT = self.__Vmax         # Signals are always plottet normalized to one times this factor
        self.__cic = {
            "length": 128,                     # Decimation (CIC) filter length
            "lengths": [16, 32, 64, 128, 256], # all possible filter lengths
            "order": 3                         # Decimation filter order
        }
        self.__files = list()
        self.__data  = dict()
        self.__time_raw   = list()
        self.__bits_volts = list()
        self.__bits       = list()
        self.__t_cic      = list()
        self.__bits_cic   = list()

    def load_data(self,file_path):

    def add_datafile(self,file_path):
        self.__files.append(file_path)

    def set_fs(self,frequency):
        self.__fs = frequency

    def set_filterlength(self,filterlength):
        self.__cic["length"] = filterlength

    def set_filterorder(self,filterorder):
        self.__cic["order"] = filterorder


def main(argv):
    try:
        opts, args = getopt.getopt(argv,"d:f:l:o:",["datafile=","frequency=","length=","order="])
    except getopt.GetoptError:
        sys.exit(2)

    sdPlot = SigDelPlot()

    for opt, arg in opts:
        if opt in ("-d","--datafile"):
            sdPlot.add_datafile(arg)
        elif opt in ("-f","--frequency"):
            sdPlot.set_fs(arg)
        elif opt in ("-l","--length"):
            sdPlot.set_filterlength(arg)
        elif opt in ("-o","--order"):
            sdPlot.set_filterorder(arg)


if __name__ == '__main__':
    main(sys.argv[1:])
