import numpy as np
from matplotlib import pyplot as plt
from bs4 import BeautifulSoup, element
from evaluation.fit_functions import linear_function
from scipy.optimize import curve_fit


def mse(a, b):
    return np.power(a - b, 2).mean()


def iterate_dc_measurements_for_linearity(soup):
    for chip_node in soup.chips.find_all('chip'):
        chip_id = chip_node['id']
        for configuration_node in chip_node.find_all('configuration', type='dc'):
            configuration = configuration_node['configuration']
            for measurement_node in configuration_node.find_all('measurement', gain='1', sign='+'):
                fs = measurement_node['fs']

                # Make sure we sort values from lowest to highest input voltage,
                # so noise amplitude and std vectors can be (possibly) correlated to input voltage
                values = sorted(measurement_node.find_all('value'), key=lambda tag: float(tag['input']))

                # Expected and measured DC voltages
                expected, measured = zip(*[(float(value['input']), float(value['output']))
                                           for value in values])

                # For everything but the preamp we have some additional statistical data
                if configuration in ('both', 'both-manual', 'sigdel'):
                    hist, bin_edges = zip(*[([float(x) for x in value.histogram['bins'].split(',')],
                                             [float(x) for x in value.histogram['bin_edges'].split(',')])
                                            for value in values])
                    noise_amplitude = [float(value.noise['amplitude']) for value in values]
                    std = [float(value.std['std']) for value in values]
                else:
                    hist = None
                    bin_edges = None
                    noise_amplitude = None
                    std = None

                yield chip_id, configuration, fs, \
                      np.array(expected), np.array(measured), \
                      hist, bin_edges, \
                      noise_amplitude, std


def calculate_dc_linearities(soup_in, soup_out):
    for chip_id, configuration, fs, \
        expected, measured, \
        hist, bin_edges, \
        noise_amplitude, std \
            in iterate_dc_measurements_for_linearity(soup_in):

        print('Evaluation DC linearity: chip_id={}, configuration={}, fs={}'.format(
            chip_id, configuration, fs
        ))
        # build XML tree
        chip_node = soup_out.chips.find('chip', id=chip_id)
        if chip_node is None:
            chip_node = soup_out.new_tag('chip', id=chip_id)
            soup_out.chips.append(chip_node)
        configuration_node = chip_node.find('configuration', configuration=configuration, type='dc')
        if configuration_node is None:
            configuration_node = soup_out.new_tag('configuration', configuration=configuration, type='dc')
            chip_node.append(configuration_node)
        measurement_node = configuration_node.find('measurement', gain='1', sign='+', fs=fs)
        if measurement_node is None:
            measurement_node = soup_out.new_tag('measurement', gain='1', sign='+', fs=fs)
            configuration_node.append(measurement_node)

        fit_node = measurement_node.find('fit')
        if fit_node is None:
            fit_node = soup_out.new_tag('fit')
            measurement_node.append(fit_node)

        mse_node = measurement_node.find('mse')
        if mse_node is None:
            mse_node = soup_out.new_tag('mse')
            measurement_node.append(mse_node)

        input_voltage_node = measurement_node.find('input_voltage')
        if input_voltage_node is None:
            input_voltage_node = soup_out.new_tag('input_voltage')
            measurement_node.append(input_voltage_node)
        input_voltage_node.attrs['voltage'] = ','.join([str(x) for x in expected])

        if std is not None:
            std_node = measurement_node.find('std')
            if std_node is None:
                std_node = soup_out.new_tag('std')
                measurement_node.append(std_node)
            std_node.attrs['std'] = ','.join([str(x) for x in std])

        if noise_amplitude is not None:
            noise_node = measurement_node.find('noise')
            if noise_node is None:
                noise_node = soup_out.new_tag('noise')
                measurement_node.append(noise_node)
            noise_node.attrs['amplitude'] = ','.join([str(x) for x in noise_amplitude])

        # Linear fit to data. Some interesting info (possibly):
        # http://stats.stackexchange.com/questions/29903/what-is-a-good-way-to-measure-the-linearity-of-a-dataset
        popt, pcov = curve_fit(linear_function, expected, measured)
        perr = np.sqrt(np.diag(pcov))
        for n, coefficient in enumerate(popt):
            fit_node.attrs['b{}'.format(n)] = coefficient
        for n, standard_deviation in enumerate(perr):
            fit_node.attrs['Sb{}'.format(n)] = standard_deviation

        mse_node.attrs['mse'] = str(mse(expected, measured))

        if False:
            model = linear_function(expected, *popt)
            plt.scatter(expected, measured)
            plt.plot(expected, model)
            plt.show()


if __name__ == '__main__':
    soup_in = BeautifulSoup(open('processed_measurements.xml', 'r'), 'xml')
    soup_out = BeautifulSoup('<chips/>', 'xml')

    calculate_dc_linearities(soup_in, soup_out)

    open('fitted_data.xml', 'wb').write(soup_out.prettify("utf-8"))
