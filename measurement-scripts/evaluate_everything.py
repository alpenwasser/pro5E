from evaluation import dc_linear
import json
import numpy as np
from matplotlib import pyplot as plt

RECALCULATE_DC = 0


def display_results():
    with open('dc_linear.json', 'r') as f:
        chips = json.load(f)

    x = chips['6']['256'][0]
    y = chips['6']['256'][1]

    plt.scatter(x, y)
    plt.show()

if __name__ == '__main__':
    if RECALCULATE_DC:
        dc_linear.evaluate()
    display_results()
