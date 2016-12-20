#!/usr/bin/env python3

import csv
import sys
from matplotlib import pyplot as plt

# --------------------------------------------------------------------------- #
# DESCRIPTION                                                                 #
# --------------------------------------------------------------------------- #
# Creates a  pgf plot file  for each  given data file,  with a reduced  set of
# points in  order to ensure that  pdflatex can still render  the file without
# all that utterly stupid nonsense about exceeding memory limits.

# --------------------------------------------------------------------------- #
# USAGE                                                                       #
# --------------------------------------------------------------------------- #
# ./genFig.py <decimation factor> <file1> <file2> <file...>
# Where:
# <decimation factor>  is the factor by  which the number of  data points gets
# reduced.
#
# EXAMPLE:
# ./plotTrace.py 100 datafile1.txt datafile2.txt
# This would  create a plot  with the traces for  the two datafiles  with only
# every 100th plot point printed.

# --------------------------------------------------------------------------- #
# GLOBAL VARIABLES                                                            #
# --------------------------------------------------------------------------- #
# The script will cycle through these colors for all the traces to be plotted.
# See also here:
# http://stackoverflow.com/questions/22408237/named-colors-in-matplotlib#22408462
START_TIME = 0
STOP_TIME  = 0

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
def read_table(dataFile,decimator):
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

        decim_iterator = 0
        for line in reader:
            if decim_iterator % decimator == 0:
                for i in range(0, len(lineData)):
                    # Copy the data from the line into the correct columns.
                    lineData[i].append(line[i])
            decim_iterator = decim_iterator + 1

        data = dict()

        for i in range(0, len(cols)):
                # Create each key in the dict with the data in its column.
                data[cols[i]] = lineData[i]


    return(data)


def plot_data(dataFile,traceColor,axis,decimator):
    data = read_table(dataFile,decimator)
    #axis   = fig.add_subplot(1,1,1,axisbg='black')
    axis.scatter(data["Time"],data["Ampl"],s=1,color=traceColor)
    #axis.plot(data["Time"],data["Ampl"],color=traceColor,)

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
    decimator = int(sys.argv[1])
    arguments = sys.argv[2:]
    for i in range(0,len(arguments)):
        plot_data(arguments[i],COLORS[(i + 1) % len(COLORS) - 1],ax,decimator)
    #plt.show()
    fig.savefig('comparison.pgf')
else:
    exit(2)
