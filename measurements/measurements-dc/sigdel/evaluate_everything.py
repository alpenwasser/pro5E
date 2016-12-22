from evaluation import dc_linear
import json
import numpy as np
from matplotlib import pyplot as plt

RECALCULATE_DC = 0


def display_results():

    with open('dc_linear.json', 'r') as f:
        chips = json.load(f)


    for key,value in chips.items():
        fig_out = plt.figure('asdf')
        for n, freq in enumerate(value):
            x = chips[key][freq][0]
            y = chips[key][freq][1]
            xnp = np.array(x)
            ynp = np.array(y)
            delta = ynp-xnp
            #print(delta)
            delta = np.abs(ynp-xnp)
            #print(delta)

            ax_out = fig_out.add_subplot(3,1,n+1)
            ax_out.scatter(xnp, ynp)
            ax_out.set_title("Chip No. {}, Sample Frequency: {} kHz".format(key, freq))

    plt.show()


if __name__ == '__main__':
    if RECALCULATE_DC:
        dc_linear.evaluate()
    display_results()
