#!/usr/bin/env python3

import csv
import sys
import numpy as np
import deltasigma as ds
from matplotlib import pyplot as plt

class SigDelPlot(object):
    def __init__(self, data_file):
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
        self.__file = data_file

    def load_data(self):

stuff=SigDelPlot(sys.argv[1])
