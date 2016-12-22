from matplotlib.pyplot import *
import deltasigma as ds
import numpy as np
import os
import re
import json


def evaluate():
    chips = dict()
    for root, dirs, files in os.walk('data'):
        for d in dirs:
            match = re.match('chip([0-9]+)', d)
            if match is None:
                continue
            chips[match.group(1)] = evaluate_chip(os.path.join('data', d))

    with open('dc_linear.json', 'w') as f:
        json.dump(chips, f)


def evaluate_chip(chip_dir_name):
    """
    Only evaluate DC bit-streams and only evaluate gains of 1 for now.
    """
    results = dict()
    for root, dirs, files in os.walk(chip_dir_name):
        for file in files:
            match_dc = re.match('.*([0-9]\.[0-9]+)VDC.*', file)
            match_fs = re.match('.*fs([0-9]+)kHz.*', file)
            gain = re.match('.*gain1\-.*', file)
            if match_dc is None or match_fs is None or gain is None:
                continue

            print('evaluating DC for {}/{}'.format(chip_dir_name, file))

            current_fs = match_fs.group(1)
            if current_fs not in results:
                results[current_fs] = [list(), list()]

            results[current_fs][0].append(float(match_dc.group(1)))
            results[current_fs][1].append(float(bit_stream_to_dc(os.path.join(chip_dir_name, file))))
    return results


def bit_stream_to_dc(file_name):
    # === GLOBALS ============================================================================
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
        "length": 256,                      # Decimation (CIC) filter length
        "lengths": [16, 32, 64, 128, 256],  # all possible filter lengths
        "order": 3                          # Decimation filter order
    }

    # ========================================================================================
    # === LOAD DATA ==== Bit-stream and input signal =========================================
    t_sdm, s_sdm = np.loadtxt(open(file_name, "rb"), skiprows=0, unpack=True)

    # ========================================================================================
    # === FILTER DATA ==== Use decimation filter (CIC) =======================================
    s_sdm_cic = ds.sinc_decimate(s_sdm, cic["order"], cic["length"])
    t_sdm_cic = t_sdm[cic["length"]:len(t_sdm):cic["length"]]

    # first few points are zero, omit them
    return np.median(s_sdm_cic[5:])
