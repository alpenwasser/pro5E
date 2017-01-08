from evaluation import dc_linear
import json
import numpy as np
from matplotlib import pyplot as plt

RECALCULATE_DC = False


def display_results():

    with open('processed_measurements.json', 'r') as f:
        data = json.load(f)

    for chip_id, chip_data in data['chips'].items():
        fig_out = plt.figure('asdf')
        linearity_measurements = chip_data['both']['linearity']['fs']
        for n, fs in enumerate(linearity_measurements):
            x = linearity_measurements[fs]['gain']['1']['input voltage']
            y = linearity_measurements[fs]['gain']['1']['output voltage']
            xnp = np.array(x)
            ynp = np.array(y)
            delta = ynp-xnp
            #print(delta)
            delta = np.abs(ynp-xnp)
            #print(delta)

            ax_out = fig_out.add_subplot(3,1,n+1)
            ax_out.scatter(xnp, ynp)
            ax_out.set_title("Chip No. {}, Sample Frequency: {} kHz".format(chip_id, fs))

        plt.show()


if __name__ == '__main__':
    if RECALCULATE_DC:
        dc_linear.evaluate()
    display_results()
