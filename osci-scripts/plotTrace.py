#!/usr/bin/env python3

import csv
import sys
from matplotlib import pyplot as plt

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


def plot_data(dataFile):
    data = read_table(dataFile)
    fig  = plt.figure(dataFile)
    ax   = fig.add_subplot(1,1,1)
    ax.scatter(data["Time"],data["Ampl"],s=1,color='blue')
    #ax.plot(data["Time"],data["Ampl"])

    # Axis Scaling
    start_time = float(data["Time"][0])
    stop_time  = float(data["Time"][len(data["Time"])-1])
    ax.set_xlim([start_time,stop_time])


# Create one figure for each input file
if (len(sys.argv) > 1):
    for i in range(1,len(sys.argv)):
        plot_data(sys.argv[i])
    plt.show()
else:
    exit(2)
