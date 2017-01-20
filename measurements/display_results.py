import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from evaluation.fit_functions import linear_function
from bs4 import BeautifulSoup


def make_subplot_better(ax):
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
    ax.figure.subplots_adjust(bottom=0.15, left=0.125, right=0.925, top=0.90, hspace=0.5)

    # set the grid on
    ax.grid('on')

    # add more ticks
    ax.set_xticks(np.arange(25))

    # remove tick marks
    ax.xaxis.set_tick_params(size=0)
    ax.yaxis.set_tick_params(size=0)

    # change the color of the top and right spines to opaque gray
    ax.spines['right'].set_color((.8, .8, .8))
    ax.spines['top'].set_color((.8, .8, .8))

    # tweak the axis labels
    xlab = ax.xaxis.get_label()
    ylab = ax.yaxis.get_label()

    xlab.set_style('italic')
    xlab.set_size(10)
    ylab.set_style('italic')
    ylab.set_size(10)

    # tweak the title
    ttl = ax.title
    ttl.set_weight('bold')


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
        make_subplot_better(ax)
        for color, fs in (('b', 32), ('r', 96), ('g', 256)):
            x = 0
            for input_voltage, slope, offset, mse in get_linearity_results(soup, configuration, fs, 1, '+'):
                ax.scatter(x, mse, c=color)
                x += 1
        ax.set_title('MSEs for {}'.format(configuration))
        ax.set_ylim([-0.01, 0.01])
    #plt.savefig('dc_mse.pdf', facecolor='white', edgecolor='none')
    #plt.gcf().clear()
    plt.show()


def display_dc_slope_results_for_sigdel_and_both(soup):
    fig = plt.figure('test')
    configurations = ('both', 'sigdel')
    sample_frequencies = np.array((32, 96, 256))
    for subplot_id, configuration in enumerate(configurations):
        ax = fig.add_subplot(2, 2, subplot_id*2 + 1)
        ax2 = fig.add_subplot(2, 2, subplot_id*2 + 2)
        make_subplot_better(ax)
        make_subplot_better(ax2)
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
    #plt.savefig('dc_slope_for_sigdel_and_both.pdf', facecolor='white', edgecolor='none')
    #plt.gcf().clear()
    plt.show()


def display_dc_slope_results_for_preamp(soup):
    for sign in ('+', '-'):
        sample_frequencies = np.array((32, 96, 256))
        gains = (1, 2, 4, 8, 16)
        fig = plt.figure('test')
        for gain_id, gain in enumerate(gains):
            ax2 = fig.add_subplot(5, 2, gain_id*2 + 1)
            ax = fig.add_subplot(5, 2, gain_id*2 + 2)
            make_subplot_better(ax)
            make_subplot_better(ax2)
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
        #plt.savefig('dc_slope_preamp_gain{}.pdf'.format(gain), facecolor='white', edgecolor='none')
        #plt.gcf().clear()


def display_dc_offset_results(soup):
    fig = plt.figure('test')
    for subplot_id, configuration in enumerate(('both', 'sigdel', 'preamp')):
        ax = fig.add_subplot(3, 2, subplot_id * 2 + 1)
        ax2 = fig.add_subplot(3, 2, subplot_id * 2 + 2)
        make_subplot_better(ax)
        make_subplot_better(ax2)
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

        ax.errorbar(sample_frequencies, offsets_avg, yerr=offsets_std, fmt='o')
        ax.plot(sample_frequencies, linear_function(sample_frequencies, *popt))
        ax2.set_title('{} offsets'.format(configuration))
        ax.set_title('offset vs Sampling Frequency\nfuck'.format(configuration))
    #plt.savefig('dc_offsets.pdf', facecolor='white', edgecolor='none')
    #plt.gcf().clear()
    plt.show()


def display_noise_amplitude_and_standard_deviation(soup):
    fig = plt.figure('test')
    for subplot_id, configuration in enumerate(('both', 'both-manual', 'sigdel')):
        ax = fig.add_subplot(3, 1, subplot_id + 1)
        make_subplot_better(ax)
        for color, fs in (('b', 32), ('r', 96), ('g', 256)):
            x = 0
            for input_voltage, noise_amplitude, std in get_noise_amp_and_std(soup, configuration, fs):
                ax.scatter(input_voltage, noise_amplitude, c=color)
                x += 1
        ax.set_title('Noise amplitude for {}'.format(configuration))
    #plt.savefig('dc_noise_amp.pdf', facecolor='white', edgecolor='none')
    #plt.gcf().clear()
    plt.show()

    fig = plt.figure('test')
    for subplot_id, configuration in enumerate(('both', 'both-manual', 'sigdel')):
        ax = fig.add_subplot(3, 1, subplot_id + 1)
        make_subplot_better(ax)
        for color, fs in (('b', 32), ('r', 96), ('g', 256)):
            x = 0
            for input_voltage, noise_amplitude, std in get_noise_amp_and_std(soup, configuration, fs):
                ax.scatter(input_voltage, std, c=color)
                x += 1
        ax.set_title('Standard deviation for {}'.format(configuration))
    #plt.savefig('dc_noise_std.pdf', facecolor='white', edgecolor='none')
    #plt.gcf().clear()
    plt.show()


def get_tau_results(soup, fs, gain, sign):
    for chip_node in soup.chips.find_all('chip'):
        for configuration_node in chip_node.find_all('configuration', configuration='preamp', type='dc'):
            for measurement_node in configuration_node.find_all('measurement', fs=fs, gain=gain, sign=sign):
                taus1 = [float(x) for x in measurement_node.taus.attrs['taus1'].split(',')]
                taus2 = [float(x) for x in measurement_node.taus.attrs['taus2'].split(',')]
                Staus1 = [float(x) for x in measurement_node.taus.attrs['Staus1'].split(',')]
                Staus2 = [float(x) for x in measurement_node.taus.attrs['Staus2'].split(',')]
                input_voltages = [float(x) for x in measurement_node.input_voltage.attrs['voltage'].split(',')]

                # If the expected voltage is greater than Vref (1.5V), then we are interested in the charge taus.
                # Otherwise we are interested in the discharge taus. If the gain is negative, the opposite is true.
                interesting_taus = list()
                for voltage, tau1, tau2, Stau1, Stau2 in zip(input_voltages, taus1, taus2, Staus1, Staus2):
                    if sign == '+':
                        interesting_taus.append((tau1, Stau1) if voltage > 1.5 else (tau2, Stau2))
                    else:
                        interesting_taus.append((tau1, Stau1) if voltage < 1.5 else (tau2, Stau2))

                yield input_voltages, list(zip(*interesting_taus))


def average_taus_for_all_chips(soup, fs, gain, sign):
    chip_taus = list()
    for input_voltages, taus in get_tau_results(soup, fs, gain, sign):
        chip_taus.append(taus)
    chip_taus = [list(zip(*x)) for x in zip(*chip_taus)]
    taus, Staus = list(zip(*[avg_std(means, uncertainties) for means, uncertainties in zip(chip_taus[0], chip_taus[1])]))
    return input_voltages, taus, Staus


def display_tau_results(soup):
    # The two tau constants are expected to change depending on the gain
    sampling_frequencies = (32, 96, 256)
    gains = (1, 2, 4, 8, 16)
    fig = plt.figure('test')
    for subplot_id, gain in enumerate(gains):
        ax = fig.add_subplot(3, 2, subplot_id + 1)
        make_subplot_better(ax)
        min_ = 0
        max_ = 0
        for fs in sampling_frequencies:
            input_voltages, taus, Staus = average_taus_for_all_chips(soup, fs, gain, '+')
            ax.errorbar(input_voltages, taus, yerr=Staus, fmt='o')
            min_ = np.min(taus) if np.min(taus) < min_ else min_
            max_ = np.max(taus) if np.max(taus) > max_ else max_
        ax.set_ylim(min_, max_)
    plt.show()


if __name__ == '__main__':
    fitted_soup = BeautifulSoup(open('fitted_data.xml', 'r'), 'xml')
    #raw_soup = BeautifulSoup(open('processed_measurements.xml', 'r'), 'xml')

    #display_dc_mse_results(fitted_soup)
    display_dc_slope_results_for_preamp(fitted_soup)
    display_dc_slope_results_for_sigdel_and_both(fitted_soup)
    display_dc_offset_results(fitted_soup)
    display_noise_amplitude_and_standard_deviation(fitted_soup)
    display_tau_results(fitted_soup)
