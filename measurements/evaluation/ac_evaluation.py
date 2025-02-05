import os
import re


def evaluate(soup):
    for configuration in ('both', 'sigdel'):
        data_path = os.path.join('measurements-ac', configuration, 'data')
        for root, dirs, files in os.walk(data_path):
            for d in dirs:
                match = re.match('chip([0-9]+)', d)
                if match is None:
                    continue

                chip_id = match.group(1).lstrip('0')
                chip_node = soup.chips.find('chip', id=chip_id)
                if chip_node is None:
                    chip_node = soup.new_tag('chip', id=chip_id)
                    soup.chips.append(chip_node)

                configuration_node = chip_node.find('configuration', configuration=configuration, type='ac')
                if configuration_node is None:
                    configuration_node = soup.new_tag('configuration', configuration=configuration, type='ac')
                    chip_node.append(configuration_node)

                evaluate_chip(os.path.join(data_path, d), configuration, soup, configuration_node)


def evaluate_chip(chip_dir_name, configuration, soup, configuration_node):
    for root, dirs, files in os.walk(chip_dir_name):
        for file in files:
            match_fs = re.match('^.*?([0-9]+)kHz-[0-9]+k?Hz.*$', file)
            match_f0 = re.match('^.*?[0-9]+kHz-([0-9]+k?)Hz.*$', file)
            match_vpp = re.match('.*?([0-9]\.[0-9]+)VPP.*', file)

            if match_fs is None or match_f0 is None or match_vpp is None:
                print('WARNING: Skipping file {}'.format(file))
                continue

            current_fs = match_fs.group(1).lstrip('0')
            current_f0 = match_f0.group(1).lstrip('0')
            current_vpp = match_vpp.group(1)

            # kilo hertz
            if current_f0[0] == 'k':
                current_f0 = current_f0[1:] + '000'

            print('evaluating AC for {}/{}, fs={}, f0={}, vpp={}, dc={}'.format(chip_dir_name, file, current_sign, current_gain, current_fs, current_dc))

            measurement_node = configuration_node.find('measurement', fs=current_fs, gain=current_gain, sign=current_sign)
            if measurement_node is None:
                measurement_node = soup.new_tag('measurement', fs=current_fs, gain=current_gain, sign=current_sign)
                configuration_node.append(measurement_node)

            measured_dc = str(bit_stream_to_dc(os.path.join(chip_dir_name, file)))

            value_node = soup.new_tag('value', input=current_dc,
                                               output=measured_dc)
            measurement_node.append(value_node)


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
