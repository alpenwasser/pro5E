import numpy as np
from matplotlib.pyplot import *
from scipy import signal

bitstream = [x for x in open('bit_stream.txt', 'r')]
time = [float(x.split('  ')[0]) for x in bitstream]
value = [float(x.split('  ')[1]) for x in bitstream]
time = time[1:10000]
value = value[0:10000]

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

h = signal.firwin(numtaps=100, cutoff=1100, nyq=128000)
filtered = signal.lfilter(h, 1.0, value)

plot(filtered)
show()

