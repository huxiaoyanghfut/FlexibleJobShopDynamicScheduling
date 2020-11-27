from math import fmod

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


# =========================================================================================
def createGanttChart(aJobsList, machinesList, itinerariesList, time=0):
    """Creates graph in specified aFrame"""

    plt.figure()
    cMax = max([j.endTime for j in aJobsList])
    chartFig, ax = plt.subplots()
    ax.set_xlabel('Time', fontsize=12)  # description of axis and chart title
    ax.set_ylabel('Machines', fontsize=12)
    chartTitle = "Gantt chart  Cmax=" + str(cMax) +"\n"

    for i, itinerary in enumerate(itinerariesList):
        arr = [job for job in aJobsList if job.itinerary == itinerary.name]
        arr.sort(key=lambda x: x.endTime)
        chartTitle = chartTitle + " C" + str(arr[-1].itinerary[-1]) + "=" + str(arr[-1].endTime) + ","
        if not fmod(i, 10) and i != 0:
            chartTitle = chartTitle + "\n"

    plt.title(chartTitle, fontsize=10)


    # values for machines y axis
    machinesNamesRev = list(reversed([mach.name for mach in machinesList]))

    machinesTicksPos = [15]
    for i in range(len(machinesNamesRev[1:])):
        machinesTicksPos.append(machinesTicksPos[i] + 10)  # machine increase this +10
    ax.set_yticks(machinesTicksPos)
    ax.set_yticklabels(machinesNamesRev)  # set labels as machines names in reversed order

    ax.set_ylim(5, machinesTicksPos[-1] + 10)  # this is related with amout of machines and height (last machine+10) of chart.
    ax.set_xlim(0, cMax + 20)  # from zero to end time of last job (max end time in job.endtime list)

    # setting the legend (color and itinerary)
    legendsColors = []
    seen = set()
    uniqueItinerariesInJobList = [job for job in aJobsList if job.itinerary not in seen and not seen.add(job.itinerary)]
    for job in uniqueItinerariesInJobList:
        legendsColors.append(mpatches.Patch(color=job.colorOfItinerary, label=job.itinerary))  # legend color and name
    plt.legend(handles=legendsColors, fontsize=8)

    tuplesForMachineAxis = []
    colorsForMachineAxis = []
    for index, machLabel in enumerate(machinesNamesRev):
        for job in aJobsList:
            if job.machine == machLabel:
                tuplesForMachineAxis.append(job.getTupleStartAndDuration())
                colorsForMachineAxis.append(job.colorOfItinerary)
        ax.broken_barh(tuplesForMachineAxis, ((index + 1) * 10, 9), facecolors=colorsForMachineAxis)
        tuplesForMachineAxis.clear()
        colorsForMachineAxis.clear()

    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))  # this is cosmetics to set unit to 10
    for label in ax.get_xticklabels()[::2]:  # and show only every two ticks
        label.set_visible(False)
    ax.axvline(time , ls='--', color='r')
    plt.show()
