#!/usr/bin/env python3
import numpy as np
from matplotlib.pyplot import *
import deltasigma as ds
import matplotlib.pyplot as plt
import sys


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

fig_out = plt.figure(figsize=(20, 8))
ax_out = fig_out.add_subplot(111)
#ax_out.step(t_sdm_cic, s_sdm_cic*NORM_FACT, where='post', label=r"$V_{out,cic}$", zorder=4)
ax_out.scatter(t_sdm_cic, s_sdm_cic*NORM_FACT, label=r"$V_{out,cic}$")
#xlim(0.2,1.6)

# set title and axis
ax_out.set_title("Filtered Bit-Stream, Filter Length {}".format(cic["length"]))
ax_out.set_xlabel("Time (s)")
ax_out.set_ylabel("Voltage (V)")
ax_out.legend(loc='upper left')
fig_out.tight_layout()
show()
