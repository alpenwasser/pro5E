from matplotlib.pyplot import *
import deltasigma as ds
import numpy as np
import os
import re
import xml.etree.ElementTree as ET


def evaluate():
    root_node = ET.Element('chips')
    for configuration in ['both']:  # ['both', 'both-manual', 'preamp', 'sigdel']:
        data_path = os.path.join('measurements-dc', configuration, 'data')
        for root, dirs, files in os.walk(data_path):
            for d in dirs:
                match = re.match('chip([0-9]+)', d)
                if match is None:
                    continue
                chip_id = match.group(1).lstrip('0')
                chip_node = ET.SubElement(root_node, 'chip')
                chip_node.set('id', chip_id)
                configuration_node = ET.SubElement(chip_node, 'configuration')
                configuration_node.set('name', configuration)
                measurement_node = ET.SubElement(configuration_node, 'measurement')
                measurement_node.set('type', 'dc')
                evaluate_chip(os.path.join(data_path, d), configuration, measurement_node)

    open('processed_measurements.xml', 'w').write(ET.dump(root_node))


def evaluate_chip(chip_dir_name, configuration, measurement_node):
    for root, dirs, files in os.walk(chip_dir_name):
        for file in files:
            # apparently, we can't keep our file naming consistent
            if configuration in ('both', 'both-manual'):
                match_dc = re.match('.*?([0-9]\.[0-9]+)V.*', file)
                match_fs = re.match('.*?([0-9]+)kHz.*', file)
            elif configuration == 'preamp':
                pass

            if match_dc is None or match_fs is None:
                continue

            print('evaluating DC for {}/{}'.format(chip_dir_name, file))

            current_dc = match_dc.group(1).lstrip('0')
            current_fs = match_fs.group(1).lstrip('0')
            measurement_node.set('fs', current_fs)
            measurement_node.set('gain', '1')
            ET.SubElement(measurement_node, 'input').text = current_dc
            ET.SubElement(measurement_node, 'output').text = str(bit_stream_to_dc(os.path.join(chip_dir_name, file)))


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
