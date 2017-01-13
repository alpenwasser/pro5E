import numpy as np
from bs4 import BeautifulSoup
from evaluation.fit_functions import linear_function
from scipy.optimize import curve_fit


def mse(a, b):
    return np.power(a-b, 2).mean()


def iterate_dc_measurements_for_linearity(soup):
    for measurement_node in soup.chips.find_all('chip'):
        chip_id = measurement_node['id']
        for configuration_node in measurement_node.find_all('configuration', type='dc'):
            configuration = configuration_node['configuration']
            for measurement_node in configuration_node.find_all('measurement', gain='1', sign='+'):
                fs = measurement_node['fs']
                expected, measured = zip(*[(float(value['input']), float(value['output']))
                                           for value in measurement_node.find_all('value')])
                yield chip_id, configuration, fs, np.array(expected), np.array(measured)


def calculate_dc_linearities(soup_in, soup_out):
    for chip_id, configuration, fs, expected, measured in iterate_dc_measurements_for_linearity(soup_in):
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

        # Linear fit to data. Some interesting info (possibly):
        # http://stats.stackexchange.com/questions/29903/what-is-a-good-way-to-measure-the-linearity-of-a-dataset
        popt, pcov = curve_fit(linear_function, expected, measured)
        perr = np.sqrt(np.diag(pcov))
        for n, coefficient in enumerate(popt):
            fit_node.attrs['b{}'.format(n)] = coefficient
        for n, standard_deviation in enumerate(perr):
            fit_node.attrs['Sb{}'.format(n)] = standard_deviation

        mse_node.string = str(mse(expected, measured))

if __name__ == '__main__':
    soup_in = BeautifulSoup(open('processed_measurements.xml', 'r'), 'xml')
    soup_out = BeautifulSoup('<chips/>', 'xml')

    calculate_dc_linearities(soup_in, soup_out)

    open('fitted_data.xml', 'wb').write(soup_out.prettify("utf-8"))
