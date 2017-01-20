from matplotlib import pyplot as plt
from evaluation.savitzky_golay import savitzky_golay
from scipy.optimize import curve_fit
from evaluation.fit_functions import preamp_curve
from decimal import Decimal
import deltasigma as ds
import numpy as np
import os
import re


def evaluate(soup):
    for configuration in ('both', 'both-manual', 'sigdel', 'preamp'):
        data_path = os.path.join('measurements-dc', configuration, 'data')
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

                configuration_node = chip_node.find('configuration', configuration=configuration, type='dc')
                if configuration_node is None:
                    configuration_node = soup.new_tag('configuration', configuration=configuration, type='dc')
                    chip_node.append(configuration_node)

                evaluate_chip(os.path.join(data_path, d), configuration, soup, configuration_node)


def evaluate_chip(chip_dir_name, configuration, soup, configuration_node):
    for root, dirs, files in os.walk(chip_dir_name):
        for file in files:
            match_dc = re.match('.*?([0-9]\.[0-9]+)V.*', file)
            match_fs = re.match('.*?([0-9]+)kHz.*', file)

            # gain sign was only tested in preamp configuration
            if configuration == 'preamp':
                match_sign = re.match('.*gain([\+-])[0-9]+.*', file)
            else:
                match_sign = re.match('(.*)', '+')  # default was positive

            # gain is 1 if measuring only the sigdel
            if configuration == 'sigdel':
                match_gain = re.match('(.*)', '1')
            else:
                match_gain = re.match('.*gain[\+-]?([0-9]+).*', file)

            if match_dc is None or match_fs is None or match_gain is None or match_sign is None:
                print('WARNING: Skipping file {}'.format(file))
                continue

            current_dc = match_dc.group(1).lstrip('0')
            current_fs = match_fs.group(1).lstrip('0')
            current_gain = match_gain.group(1).lstrip('0')
            current_sign = match_sign.group(1)

            print('evaluating DC for {}/{}, sign={}, gain={}, fs={}, dc={}'.format(chip_dir_name, file, current_sign, current_gain, current_fs, current_dc))

            measurement_node = configuration_node.find('measurement', fs=current_fs, gain=current_gain, sign=current_sign)
            if measurement_node is None:
                measurement_node = soup.new_tag('measurement', fs=current_fs, gain=current_gain, sign=current_sign)
                configuration_node.append(measurement_node)

            value_node = measurement_node.find('value', input=current_dc)
            if value_node is None:
                value_node = soup.new_tag('value', input=current_dc)
                measurement_node.append(value_node)

            # everything except for the preamp measurements require the CIC filter
            if configuration == 'preamp':
                gain_is_positive = True if current_sign == '+' else False

                fit_node = value_node.find('fit')
                if fit_node is None:
                    fit_node = soup.new_tag('fit')
                    value_node.append(fit_node)

                measured_dc,\
                amp, amp_offset, period, t_offset, duty_cycle, tau1, tau2,\
                Samp, Samp_offset, Speriod, St_offset, Sduty_cycle, Stau1, Stau2 =\
                    parse_preamp_data(os.path.join(chip_dir_name, file), float(current_dc), gain_is_positive)

                value_node.attrs['output'] = measured_dc

                fit_node.attrs['amp'] = amp
                fit_node.attrs['Samp'] = Samp
                fit_node.attrs['amp_offset'] = amp_offset
                fit_node.attrs['Samp_offset'] = Samp_offset
                fit_node.attrs['period'] = period
                fit_node.attrs['Speriod'] = Speriod
                fit_node.attrs['t_offset'] = t_offset
                fit_node.attrs['St_offset'] = St_offset
                fit_node.attrs['duty_cycle'] = duty_cycle
                fit_node.attrs['Sduty_cycle'] = Sduty_cycle
                fit_node.attrs['tau1'] = tau1
                fit_node.attrs['Stau1'] = Stau1
                fit_node.attrs['tau2'] = tau2
                fit_node.attrs['Stau2'] = Stau2

            else:
                measured_dc, bins, bin_edges, noise_amplitude, std = parse_sigdel_and_both(os.path.join(chip_dir_name, file))

                value_node.attrs['output'] = measured_dc

                histogram_node = soup.new_tag('histogram', bins=bins, bin_edges=bin_edges)
                value_node.append(histogram_node)

                noise_node = soup.new_tag('noise', amplitude=noise_amplitude)
                value_node.append(noise_node)

                std_node = soup.new_tag('std', std=std)
                value_node.append(std_node)


def estimate_initial_parameters(xdata, ydata):
    # Smooth data a bit. Window size 201, 3rd degree polynomial
    ydata_smooth = savitzky_golay(ydata, 201, 3)

    # use a schmitt trigger type of approach to determine the transition points
    noise_amp = 0.05
    mid = np.mean(ydata_smooth)
    amp_offset = np.min(ydata_smooth)
    amp = np.max(ydata_smooth) - amp_offset
    low_threshold = mid - amp*noise_amp
    high_threshold = mid + amp*noise_amp
    low_transitions = list()
    high_transitions = list()
    initial_state = 0 if ydata_smooth[0] < mid else 1
    state = initial_state
    for x, y in zip(xdata, ydata_smooth):
        if state == 0:
            if y > high_threshold:
                state = 1
                high_transitions.append(x)
        else:
            if y < low_threshold:
                state = 0
                low_transitions.append(x)

    # average of differences between every transition point is a good estimate for period
    diffs = [t2 - t1 for t1, t2 in zip(high_transitions[:-1], high_transitions[1:])]
    diffs += [t2 - t1 for t1, t2 in zip(low_transitions[:-1], low_transitions[1:])]
    period = np.mean(diffs)

    duty_cycles = list()
    for t1, t2 in zip(high_transitions[:-1], high_transitions[1:]):
        for t in low_transitions:
            if t1 < t < t2:
                duty_cycles.append((t - t1) / (t2 - t1))
    for t1, t2 in zip(low_transitions[:-1], low_transitions[1:]):
        for t in high_transitions:
            if t1 < t < t2:
                duty_cycles.append((t2 - t) / (t2 - t1))
    duty_cycle = np.mean(duty_cycles)

    # and thus my inner bowels spoketh: "this value feeleth correct"
    tau = period * 0.1

    if initial_state == 0:
        t_offset = 0
    else:
        t_offset = period / 2

    return amp, amp_offset, period, t_offset, duty_cycle, tau, tau


def fit_preamp_data(xdata, ydata):
    p0 = estimate_initial_parameters(xdata, ydata)
    xdata = xdata[::10]  # otherwise it takes too long
    ydata = ydata[::10]
    try:
        popt, pcov = curve_fit(preamp_curve, xdata, ydata, p0=p0)
    except:
        return p0, p0
    return popt, pcov


def parse_preamp_data(file_name, expected_dc, gain_is_positive):
    with open(file_name, 'r') as f:
        # data begins at line 6
        for i in range(5):
            f.readline()
        data = [line.split(',') for line in f]
        xdata = np.array([float(x[0]) for x in data])
        ydata = np.array([float(x[1]) for x in data])

        # Fit data, this gives us lots of useful information and makes it easier to extract certain data
        popt, pcov = fit_preamp_data(xdata, ydata)
        perr = np.sqrt(np.diag(pcov))
        ydata_model = np.array(preamp_curve(xdata, *popt))

        # The measured DC value is either above or below the 1.5V mark.
        vref = 1.5
        if not gain_is_positive:
            expected_dc = vref - expected_dc
        if expected_dc > vref:
            measured_dc = np.max(ydata_model)
        else:
            measured_dc = np.min(ydata_model)

        if False:
            plt.plot(xdata, ydata)
            plt.plot(xdata, ydata_model)
            plt.plot([xdata[0], xdata[-1]], [measured_dc, measured_dc])
            plt.figtext(0.7, 0.8, 'tau_1: {0:.2E}\ntau_2: {1:.2E}'.format(Decimal(popt[5]), popt[6]))
            plt.savefig('256kHz-{}V.png'.format(expected_dc))
            plt.savefig('256kHz-{}V.pdf'.format(expected_dc))
            plt.gcf().clear()

        return [str(measured_dc)] + [str(x) for x in popt] + [str(x) for x in perr]


def parse_sigdel_and_both(file_name):
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
    measured_dc = np.median(s_sdm_cic[5:])

    # histogram
    hist, bin_edges = np.histogram(s_sdm_cic, bins=40)
    hist = ','.join([str(x) for x in hist])
    bin_edges = ','.join([str(x) for x in bin_edges])

    noise_amplitude = np.max(s_sdm_cic[10:]) - np.min(s_sdm_cic[10:])

    std = np.std(s_sdm_cic[10:])

    return measured_dc, hist, bin_edges, noise_amplitude, std
