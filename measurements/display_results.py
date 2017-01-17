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


def get_linearity_results(soup, configuration, fs):
    for chip_node in soup.chips.find_all('chip'):
        for configuration_node in chip_node.find_all('configuration', configuration=configuration, type='dc'):
            for measurement_node in configuration_node.find_all('measurement', fs=str(fs), gain='1', sign='+'):
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


def display_dc_slope_results(soup):
    fig = plt.figure('test')
    for subplot_id, configuration in enumerate(('both', 'both-manual', 'sigdel', 'preamp')):
        ax = fig.add_subplot(4, 2, subplot_id*2 + 1)
        ax2 = fig.add_subplot(4, 2, subplot_id*2 + 2)
        slopes_avg = list()
        slopes_std = list()
        sample_frequencies = np.array((32, 96, 256))
        for fs_id, fs in enumerate(sample_frequencies):
            slopes = [slope for input_voltage, slope, offset, mse in get_linearity_results(soup, configuration, fs)]
            slopes = list(list(x) for x in zip(*slopes))
            avg, std = avg_std(slopes[0], slopes[1])
            slopes_avg.append(avg)
            slopes_std.append(std)

            # Offset fs data slightly from one another so they appear in "chunks" in the plot
            xdata = np.array(range(len(slopes[0])))*1.1-0.05 + fs_id*0.2-0.1
            ax2.errorbar(xdata, slopes[0], yerr=slopes[1], fmt='o')

        popt, pcov = curve_fit(linear_function, sample_frequencies, slopes_avg, sigma=slopes_std, absolute_sigma=True)
        perr = np.sqrt(np.diag(pcov))
        print('avg_std(): {0:.4f} +/- {1:.4f}'.format(*avg_std(slopes_avg, slopes_std)))
        print('perr: {0:.5f} +/- {1:.8f}'.format(*perr))

        ax.errorbar(sample_frequencies, slopes_avg, yerr=slopes_std, fmt='o')
        ax.plot(sample_frequencies, linear_function(sample_frequencies, *popt))
        ax.set_title('Slopes for {}'.format(configuration))
    plt.show()


def display_dc_offset_results(soup):
    fig = plt.figure('test')
    for subplot_id, configuration in enumerate(('both', 'both-manual', 'sigdel', 'preamp')):
        ax = fig.add_subplot(4, 1, subplot_id + 1)
        for color, fs in (('b', 32), ('r', 96), ('g', 256)):
            x = 0
            for slope, offset, mse in get_linearity_results(soup, configuration, fs):
                ax.scatter(x, offset[0], c=color)
                x += 1
        ax.set_title('Offsets for {}'.format(configuration))
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


if __name__ == '__main__':
    fitted_soup = BeautifulSoup(open('fitted_data.xml', 'r'), 'xml')
    raw_soup = BeautifulSoup(open('processed_measurements.xml', 'r'), 'xml')

    #display_dc_mse_results(fitted_soup)
    display_dc_slope_results(fitted_soup)
    #display_dc_offset_results(fitted_soup)
    #display_noise_amplitude_and_standard_deviation(fitted_soup)
