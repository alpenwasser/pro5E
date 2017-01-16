import json
import numpy as np
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup


def get_linearity_results(soup, configuration, fs):
    for chip_node in soup.chips.find_all('chip'):
        for configuration_node in chip_node.find_all('configuration', configuration=configuration, type='dc'):
            for measurement_node in configuration_node.find_all('measurement', fs=str(fs), gain='1', sign='+'):
                offset = (float(measurement_node.fit['b0']), float(measurement_node.fit['Sb0']))
                slope = (float(measurement_node.fit['b1']), float(measurement_node.fit['Sb1']))
                mse = float(measurement_node.mse['mse'])

                yield slope, offset, mse


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
        ax = fig.add_subplot(4, 1, subplot_id + 1)
        for color, fs in (('b', 32), ('r', 96), ('g', 256)):
            x = 0
            for slope, offset, mse in get_linearity_results(soup, configuration, fs):
                ax.scatter(x, slope[0], c=color)
                x += 1
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
    #display_dc_slope_results(fitted_soup)
    #display_dc_offset_results(fitted_soup)
    display_noise_amplitude_and_standard_deviation(fitted_soup)
