from matplotlib.pyplot import *
import deltasigma as ds
import numpy as np
import os
import re
import json


def evaluate():
    data = {'chips': dict()}
    for configuration in ['both', 'both-manual', 'preamp', 'sigdel']:
        data_path = os.path.join('measurements-dc', configuration, 'data')
        for root, dirs, files in os.walk(data_path):
            for d in dirs:
                match = re.match('chip([0-9]+)', d)
                if match is None:
                    continue
                data['chips'][match.group(1).lstrip('0')] = {
                    configuration: {
                        'linearity': evaluate_chip(os.path.join(data_path, d), configuration)}}

    open('processed_measurements.json', 'w').write(json.dumps(data, indent=2, sort_keys=True))


def evaluate_chip(chip_dir_name, configuration):
    """
    Only evaluate DC bit-streams and only evaluate gains of 1 for now.
    """
    results = {'fs': dict()}
    for root, dirs, files in os.walk(chip_dir_name):
        for file in files:
            # apparently, we can't keep our file naming consistent
            if configuration in ('both', 'both-manual'):
                match_dc = re.match('.*?([0-9]\.[0-9]+)V.*', file)
                match_fs = re.match('.*?([0-9]+)kHz.*', file)
            elif configuration == 'preamp':
                match_dc = re.match('')
            if match_dc is None or match_fs is None:
                continue

            print('evaluating DC for {}/{}'.format(chip_dir_name, file))

            current_dc = match_dc.group(1).lstrip('0')
            current_fs = match_fs.group(1).lstrip('0')
            if current_fs not in results['fs']:
                results['fs'][current_fs] = {
                    'gain': {
                        '1': {
                            'input voltage': list(),
                            'output voltage': list()
                        }
                    }
                }

            results['fs'][current_fs]['gain']['1']['input voltage'].append(float(current_dc))
            results['fs'][current_fs]['gain']['1']['output voltage'].append(float(bit_stream_to_dc(os.path.join(chip_dir_name, file))))
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
