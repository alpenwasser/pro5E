#!/usr/bin/env python3
import numpy as np
import deltasigma as ds
import sys
import os


# === GLOBALS ============================================================================
file_name = sys.argv[1] if len(sys.argv) > 1 else "bit_stream.txt"
Vmin = 0.0                              # Minimum absolute possible input
Vmax = 3.0                              # Maximum absolute possible input
Vref = 1.5                              # Relative Vref
Vgnda = 1.5                             # Absolute analog ground
Vin_min = 0.                            # Minimum absolute used input
Vin_max = 3.                            # Maximum absolute used input
fs = 256.0e3                            # Sampling frequency (SD-modulator)
Ts = 1/fs                               # Sampling period
T_SaH = Ts*512                          # Input signal sampling period (S/H-block)
Nbit  = 12                              # Bit accuracy (for LSB/2 plot)
NORM_FACT = Vmax                        # Signals are always plottet normalized to one times this factor
cic = {
    "length": 128,                      # Decimation (CIC) filter length
    "lengths": [16, 32, 64, 128, 256],  # all possible filter lengths
    "order": 3                          # Decimation filter order
}

# ========================================================================================
# === LOAD DATA ==== Bit-stream and input signal =========================================
#t_sdm, s_sdm_orig = np.loadtxt(open("bit_stream.txt", "rb"), skiprows=0, unpack=True)
t_sdm, s_sdm_orig = np.loadtxt(open(file_name, "rb"), skiprows=0, unpack=True)
s_sdm = np.round(s_sdm_orig/np.max(s_sdm_orig))     # normalize to one

# ========================================================================================
# === FILTER DATA ==== Use decimation filter (CIC) =======================================
s_sdm_cic = ds.sinc_decimate(s_sdm, cic["order"], cic["length"])
t_sdm_cic = t_sdm[cic["length"]:len(t_sdm):cic["length"]]
s_sdm_cic = s_sdm_cic[2:]
t_sdm_cic = t_sdm_cic[2:]

# ========================================================================================
# === CREATE TARGET DIRECTORY ============================================================
src_dir_path    = os.path.dirname(os.path.relpath(file_name))
target_dir_path = src_dir_path.replace('data','data-processed')
basename        = os.path.basename(file_name)
target_file     = os.path.join(target_dir_path,basename)

if not os.path.isdir(target_dir_path):
    os.makedirs(target_dir_path)

file = open(target_file,'w')
file.write('Time,Ampl\n')
for i in range(0,len(t_sdm_cic) - 1):
    file.write(str(t_sdm_cic[i]) + ',' + str(s_sdm_cic[i] * NORM_FACT) + '\n')
file.close()
