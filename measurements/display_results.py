import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from evaluation.fit_functions import linear_function
from bs4 import BeautifulSoup


def avg_std(values, uncertainties):
    weights = 1 / np.power(uncertainties, 2)
    avg = np.sum([value * weight for value, weight in zip(values, weights)]) / np.sum(weights)
    uncertainty = 1 / np.sqrt(np.sum(weights))
    return avg, uncertainty


def get_linearity_results(soup, configuration, fs, gain, sign):
    for chip_node in soup.chips.find_all('chip'):
        for configuration_node in chip_node.find_all('configuration', configuration=configuration, type='dc'):
            for measurement_node in configuration_node.find_all('measurement', fs=str(fs), gain=str(gain), sign=sign):
                input_voltage = [float(x) for x in measurement_node.input_voltage['voltage'].split(',')]
                offset = (float(measurement_node.fit['b0']), float(measurement_node.fit['Sb0']))
                slope = (float(measurement_node.fit['b1']), float(measurement_node.fit['Sb1']))
                mse = float(measurement_node.mse['mse'])

                yield input_voltage, slope, offset, mse


def get_noise_amp_and_std(soup, configuration, fs):
    for chip_node in soup.chips.find_all('chip'):
        for configuration_node in chip_node.find_all('configuration', configuration=configuration, type='dc'):
            for measurement_node in configuration_node.find_all('measurement', fs=str(fs), gain='1', sign='+'):
                input_voltage = [float(x) for x in measurement_node.input_voltage['voltage'].split(',')]
                noise_amplitude = [float(x) for x in measurement_node.noise['amplitude'].split(',')]
                std = [float(x) for x in measurement_node.std['std'].split(',')]

                yield input_voltage, noise_amplitude, std


def display_dc_mse_results(soup):
    fig = plt.figure('test')
    for subplot_id, configuration in enumerate(('both', 'both-manual', 'sigdel', 'preamp')):
        ax = fig.add_subplot(4, 1, subplot_id + 1)
        for color, fs in (('b', 32), ('r', 96), ('g', 256)):
            x = 0
            for slope, offset, mse in get_linearity_results(soup, configuration, fs):
                ax.scatter(x, mse, c=color)
                x += 1
        ax.set_title('MSEs for {}'.format(configuration))
    plt.show()


def display_dc_slope_results_for_sigdel_and_both(soup):
    fig = plt.figure('test')
    configurations = ('both', 'both-manual', 'sigdel')
    sample_frequencies = np.array((32, 96, 256))
    for subplot_id, configuration in enumerate(configurations):
        ax = fig.add_subplot(3, 2, subplot_id*2 + 1)
        ax2 = fig.add_subplot(3, 2, subplot_id*2 + 2)
        slopes_avg = list()
        slopes_std = list()
        for fs_id, fs in enumerate(sample_frequencies):
            slopes = [slope for input_voltage, slope, offset, mse in get_linearity_results(soup, configuration, fs, 1, '+')]
            slopes = list(list(x) for x in zip(*slopes))
            avg, std = avg_std(slopes[0], slopes[1])
            slopes_avg.append(avg)
            slopes_std.append(std)

            # Offset fs data slightly from one another so they appear in "chunks" in the plot
            xdata = np.array(range(len(slopes[0])))*1.1-0.05 + fs_id*0.2-0.1
            ax2.errorbar(xdata, slopes[0], yerr=slopes[1], fmt='o')

        popt, pcov = curve_fit(linear_function, sample_frequencies, slopes_avg, sigma=slopes_std, absolute_sigma=True)
        perr = np.sqrt(np.diag(pcov))

        ax.errorbar(sample_frequencies, slopes_avg, yerr=slopes_std, fmt='o')
        ax.plot(sample_frequencies, linear_function(sample_frequencies, *popt))
        ax.set_title('Slopes for {}'.format(configuration))
    plt.show()


def display_dc_slope_results_for_preamp(soup):
    for sign in ('+', '-'):
        fig = plt.figure('test')
        sample_frequencies = np.array((32, 96, 256))
        gains = (1, 2, 4, 8, 16)
        for gain_id, gain in enumerate(gains):
            ax = fig.add_subplot(5, 2, gain_id*2 + 1)
            ax2 = fig.add_subplot(5, 2, gain_id*2 + 2)
            slopes_avg = list()
            slopes_std = list()
            for fs_id, fs in enumerate(sample_frequencies):
                slopes = [slope for input_voltage, slope, offset, mse in get_linearity_results(soup, 'preamp', fs, gain, sign)]
                slopes = list(list(x) for x in zip(*slopes))
                avg, std = avg_std(slopes[0], slopes[1])
                slopes_avg.append(avg)
                slopes_std.append(std)

                # Offset fs data slightly from one another so they appear in "chunks" in the plot
                xdata = np.array(range(len(slopes[0])))*1.1-0.05 + fs_id*0.2-0.1
                ax2.errorbar(xdata, slopes[0], yerr=slopes[1], fmt='o')

            popt, pcov = curve_fit(linear_function, sample_frequencies, slopes_avg, sigma=slopes_std, absolute_sigma=True)
            perr = np.sqrt(np.diag(pcov))

            ax.errorbar(sample_frequencies, slopes_avg, yerr=slopes_std, fmt='o')
            ax.plot(sample_frequencies, linear_function(sample_frequencies, *popt))
            ax.set_title('Slopes for preamp')
        plt.show()


def display_dc_offset_results(soup):
    fig = plt.figure('test')
    for subplot_id, configuration in enumerate(('both', 'both-manual', 'sigdel', 'preamp')):
        ax = fig.add_subplot(4, 2, subplot_id * 2 + 1)
        ax2 = fig.add_subplot(4, 2, subplot_id * 2 + 2)
        offsets_avg = list()
        offsets_std = list()
        sample_frequencies = np.array((32, 96, 256))
        for fs_id, fs in enumerate(sample_frequencies):
            offsets = [offset for input_voltage, slope, offset, mse in get_linearity_results(soup, configuration, fs, 1, '+')]
            offsets = list(list(x) for x in zip(*offsets))
            avg, std = avg_std(offsets[0], offsets[1])
            offsets_avg.append(avg)
            offsets_std.append(std)

            # Offset fs data slightly from one another so they appear in "chunks" in the plot
            xdata = np.array(range(len(offsets[0]))) * 1.1 - 0.05 + fs_id * 0.2 - 0.1
            ax2.errorbar(xdata, offsets[0], yerr=offsets[1], fmt='o')

        popt, pcov = curve_fit(linear_function, sample_frequencies, offsets_avg, sigma=offsets_std, absolute_sigma=True)
        perr = np.sqrt(np.diag(pcov))
        print('avg_std(): {0:.4f} +/- {1:.4f}'.format(*avg_std(offsets_avg, offsets_std)))
        print('perr: {0:.5f} +/- {1:.8f}'.format(*perr))

        ax.errorbar(sample_frequencies, offsets_avg, yerr=offsets_std, fmt='o')
        ax.plot(sample_frequencies, linear_function(sample_frequencies, *popt))
        ax.set_title('offsets for {}'.format(configuration))
    plt.show()


def display_noise_amplitude_and_standard_deviation(soup):
    fig = plt.figure('test')
    for subplot_id, configuration in enumerate(('both', 'both-manual', 'sigdel')):
        ax = fig.add_subplot(3, 1, subplot_id + 1)
        for color, fs in (('b', 32), ('r', 96), ('g', 256)):
            x = 0
            for input_voltage, noise_amplitude, std in get_noise_amp_and_std(soup, configuration, fs):
                ax.scatter(input_voltage, noise_amplitude, c=color)
                x += 1
        ax.set_title('Noise amplitude for {}'.format(configuration))
    plt.show()

    fig = plt.figure('test')
    for subplot_id, configuration in enumerate(('both', 'both-manual', 'sigdel')):
        ax = fig.add_subplot(3, 1, subplot_id + 1)
        for color, fs in (('b', 32), ('r', 96), ('g', 256)):
            x = 0
            for input_voltage, noise_amplitude, std in get_noise_amp_and_std(soup, configuration, fs):
                ax.scatter(input_voltage, std, c=color)
                x += 1
        ax.set_title('Standard deviation for {}'.format(configuration))
    plt.show()


def display_tau_results(soup):
    # The two tau constants are expected to be different per chip
    for chip_node in soup.chips.find_all('chip'):
        pass


if __name__ == '__main__':
    fitted_soup = BeautifulSoup(open('fitted_data.xml', 'r'), 'xml')
    #raw_soup = BeautifulSoup(open('processed_measurements.xml', 'r'), 'xml')

    #display_dc_mse_results(fitted_soup)
    display_dc_slope_results_for_preamp(fitted_soup)
    display_dc_slope_results_for_sigdel_and_both(fitted_soup)
    #display_dc_offset_results(fitted_soup)
    #display_noise_amplitude_and_standard_deviation(fitted_soup)
    #display_tau_results(fitted_soup)