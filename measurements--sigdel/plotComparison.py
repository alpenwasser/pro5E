#!/usr/bin/env python3

import csv
import sys
import numpy as np
import deltasigma as ds
from matplotlib import pyplot as plt

# --------------------------------------------------------------------------- #
# DESCRIPTION                                                                 #
# --------------------------------------------------------------------------- #
# Creates a plot for each file given as an argument on the command line. One
# plot in one window is created per data file.

# --------------------------------------------------------------------------- #
# USAGE                                                                       #
# --------------------------------------------------------------------------- #
# ./plotTrace.py <file1> <file2> ...
#
# EXAMPLE:
# ./plotTrace.py data/chip01Gain+01/chip01-gain+01-032kHz-0.9V.txt

# --------------------------------------------------------------------------- #
# GLOBAL VARIABLES                                                            #
# --------------------------------------------------------------------------- #
# The script will cycle through these colors for all the traces to be plotted.
# See also here:
# http://stackoverflow.com/questions/22408237/named-colors-in-matplotlib#22408462

COLORS=list()
COLORS.append('crimson')
COLORS.append('darkblue')
COLORS.append('darkcyan')
COLORS.append('darkgoldenrod')
COLORS.append('darkgray')
COLORS.append('darkgreen')
COLORS.append('darkkhaki')
COLORS.append('darkmagenta')
COLORS.append('darkolivegreen')
COLORS.append('darkorange')
COLORS.append('darkorchid')
COLORS.append('darkred')
COLORS.append('darksalmon')
COLORS.append('darkseagreen')
COLORS.append('darkslateblue')
COLORS.append('darkslategray')
COLORS.append('darkturquoise')
COLORS.append('darkviolet')
COLORS.append('deepskyblue')
COLORS.append('dimgray')
COLORS.append('cadetblue')
COLORS.append('red')
COLORS.append('blue')
COLORS.append('blueviolet')
COLORS.append('deeppink')
COLORS.append('aqua')

#COLORS.append('cyan')
#COLORS.append('chartreuse')
#COLORS.append('azure')
#COLORS.append('aquamarine')
#COLORS.append('aliceblue')
#COLORS.append('antiquewhite')
#COLORS.append('beige')
#COLORS.append('bisque')
#COLORS.append('black')
#COLORS.append('blanchedalmond')
#COLORS.append('brown')
#COLORS.append('burlywood')

#COLORS.append('chocolate')
#COLORS.append('coral')
#COLORS.append('cornflowerblue')
#COLORS.append('cornsilk')
#COLORS.append('dodgerblue')
#COLORS.append('firebrick')
#COLORS.append('floralwhite')
#COLORS.append('forestgreen')
#COLORS.append('fuchsia')
#COLORS.append('gainsboro')
#COLORS.append('ghostwhite')
#COLORS.append('gold')
#COLORS.append('goldenrod')
#COLORS.append('gray')
#COLORS.append('green')
#COLORS.append('greenyellow')
#COLORS.append('honeydew')
#COLORS.append('hotpink')
#COLORS.append('indianred')
#COLORS.append('indigo')
#COLORS.append('ivory')
#COLORS.append('khaki')
#COLORS.append('lavender')
#COLORS.append('lavenderblush')
#COLORS.append('lawngreen')
#COLORS.append('lemonchiffon')
#COLORS.append('lightblue')
#COLORS.append('lightcoral')
#COLORS.append('lightcyan')
#COLORS.append('lightgoldenrodyellow')
#COLORS.append('lightgreen')
#COLORS.append('lightgray')
#COLORS.append('lightpink')
#COLORS.append('lightsalmon')
#COLORS.append('lightseagreen')
#COLORS.append('lightskyblue')
#COLORS.append('lightslategray')
#COLORS.append('lightsteelblue')
#COLORS.append('lightyellow')
#COLORS.append('lime')
#COLORS.append('limegreen')
#COLORS.append('linen')
#COLORS.append('magenta')
#COLORS.append('maroon')
#COLORS.append('mediumaquamarine')
#COLORS.append('mediumblue')
#COLORS.append('mediumorchid')
#COLORS.append('mediumpurple')
#COLORS.append('mediumseagreen')
#COLORS.append('mediumslateblue')
#COLORS.append('mediumspringgreen')
#COLORS.append('mediumturquoise')
#COLORS.append('mediumvioletred')
#COLORS.append('midnightblue')
#COLORS.append('mintcream')
#COLORS.append('mistyrose')
#COLORS.append('moccasin')
#COLORS.append('navajowhite')
#COLORS.append('navy')
#COLORS.append('oldlace')
#COLORS.append('olive')
#COLORS.append('olivedrab')
#COLORS.append('orange')
#COLORS.append('orangered')
#COLORS.append('orchid')
#COLORS.append('palegoldenrod')
#COLORS.append('palegreen')
#COLORS.append('paleturquoise')
#COLORS.append('palevioletred')
#COLORS.append('papayawhip')
#COLORS.append('peachpuff')
#COLORS.append('peru')
#COLORS.append('pink')
#COLORS.append('plum')
#COLORS.append('powderblue')
#COLORS.append('purple')
#COLORS.append('rosybrown')
#COLORS.append('royalblue')
#COLORS.append('saddlebrown')
#COLORS.append('salmon')
#COLORS.append('sandybrown')
#COLORS.append('seagreen')
#COLORS.append('seashell')
#COLORS.append('sienna')
#COLORS.append('silver')
#COLORS.append('skyblue')
#COLORS.append('slateblue')
#COLORS.append('slategray')
#COLORS.append('snow')
#COLORS.append('springgreen')
#COLORS.append('steelblue')
#COLORS.append('tan')
#COLORS.append('teal')
#COLORS.append('thistle')
#COLORS.append('tomato')
#COLORS.append('turquoise')
#COLORS.append('violet')
#COLORS.append('wheat')
#COLORS.append('white')
#COLORS.append('whitesmoke')
#COLORS.append('yellow')
#COLORS.append('yellowgreen')

# --------------------------------------------------------------------------- #
# IMPLEMENTATION                                                              #
# --------------------------------------------------------------------------- #
def read_table(dataFile):
    with open(dataFile, 'rt') as fh:
        reader = csv.reader(fh, delimiter=',', skipinitialspace=True)

        lineData = list()

        # Skip the first four lines (superfluous header), keep the fifth
        cols = list()
        for i in range(0,5):
            cols = next(reader)
        #print(cols)

        for col in cols:
            # Create a list in lineData for each column of data.
            lineData.append(list())

        for line in reader:
            for i in range(0, len(lineData)):
                # Copy the data from the line into the correct columns.
                lineData[i].append(line[i])

        data = dict()

        for i in range(0, len(cols)):
            # Create each key in the dict with the data in its column.
            data[cols[i]] = lineData[i]

    return(data)


def plot_data(dataFile,traceColor,axis):
    data = read_table(dataFile)
    #ax   = fig.add_subplot(1,1,1,axisbg='black')
    #ax.scatter(data["Time"],data["Ampl"],s=1,color=traceColor)
    axis.plot(data["Time"],data["Ampl"],color=traceColor,)

    # Axis Scaling
    global START_TIME
    global STOP_TIME
    start_time = 0
    stop_time  = 0
    for timeStr in data["Time"]:
        time = float(timeStr)
        if time < start_time:
            start_time = time
        elif time > stop_time:
            stop_time = time

    if start_time < START_TIME:
        START_TIME = start_time
    if stop_time > STOP_TIME:
        STOP_TIME = stop_time

    axis.set_xlim([START_TIME,STOP_TIME])


if (len(sys.argv) > 1):
    fig  = plt.figure('Comparison')
    ax   = fig.add_subplot(1,1,1)
    for i in range(1,len(sys.argv)):
        plot_data(sys.argv[i],COLORS[i % len(COLORS) - 1],ax)
    plt.show()
else:
    exit(2)
