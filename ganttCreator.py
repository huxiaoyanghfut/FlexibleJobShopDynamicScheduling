from matplotlib import ticker
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei']

# =========================================================================================
def createGanttChart(aJobsList, machinesList, itinerariesList, time=0):
    """Creates graph in specified aFrame"""

    plt.figure()
    cMax = max([j.endTime for j in aJobsList])
    plt.xlabel('时间', fontsize=12)  # description of axis and chart title
    plt.ylabel('机器', fontsize=12)
    chartTitle = "甘特图  Cmax=" + str(cMax) +"\n"
    plt.title(chartTitle, fontsize=12)

    ## 计算各个工件的完工时间 OK
    chartDetails = ""
    for i, itinerary in enumerate(itinerariesList):
        arr = [job for job in aJobsList if job.itinerary == itinerary.name]
        arr.sort(key=lambda x: x.endTime)
        chartDetails = chartDetails + " C" + str(arr[-1].itinerary[-1]) + "=" + str(arr[-1].endTime) + ","
    
    plt.suptitle(chartDetails, fontsize=10)


    # values for machines y axis OK
    machinesNamesRev = list(reversed([mach.name for mach in machinesList]))
    machinesTicksPos = [15]
    for i in range(len(machinesNamesRev[1:])):
        machinesTicksPos.append(machinesTicksPos[i] + 10)  # machine increase this +10
    plt.yticks(machinesTicksPos, machinesNamesRev) # set labels as machines names in reversed order

    plt.ylim(5, machinesTicksPos[-1] + 10)  # this is related with amout of machines and height (last machine+10) of chart.
    plt.xlim(0, cMax + 20)  # from zero to end time of last job (max end time in job.endtime list)

    #甘特图画矩形
    tuplesForMachineAxis = []
    colorsForMachineAxis = []
    for index, machLabel in enumerate(machinesNamesRev):
        for job in aJobsList:
            if job.assignedMachine == machLabel:
                tuplesForMachineAxis.append(job.getTupleStartAndDuration())
                colorsForMachineAxis.append(job.colorOfItinerary)
        plt.gca().broken_barh(tuplesForMachineAxis, ((index + 1) * 10, 9), facecolors=colorsForMachineAxis)
        tuplesForMachineAxis = []
        colorsForMachineAxis = []

    # setting the legend (color and itinerary) OK 
    legendsColors = []
    seen = set()
    uniqueItinerariesInJobList = [job for job in aJobsList if job.itinerary not in seen and not seen.add(job.itinerary)]
    for job in uniqueItinerariesInJobList:
        legendsColors.append(mpatches.Patch(color=job.colorOfItinerary, label=job.itinerary))  # legend color and name
    plt.legend(handles=legendsColors, fontsize=8)

    
    
    plt.grid(True)
    plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(10))
    for label in plt.gca().get_xticklabels()[::2]:  # and show only every two ticks
        label.set_visible(False)
    plt.axvline(time , ls='--', color='r')
    plt.show()
    