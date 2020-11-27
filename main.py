from algorithms import prepareJobs, algorithmSPT
from rescheduleAlgorithms import *
from chartGanttCreator import createGanttChart
from parseData import parseData
import copy

from parseNewData import parseNewData


def main():
    machinesList, itinerariesList = parseData()
    jobsList = prepareJobs(machinesList, itinerariesList)
    resultSPT = algorithmSPT(copy.deepcopy(jobsList), machinesList)
    createGanttChart(resultSPT, machinesList, itinerariesList)
    yourChoice = input("是否需要进行重调度？[y/n]:")
    if yourChoice == "y":
        time = float(input("请输入重调度时间（0~Cmax之间）："))
        insertItineraryList = parseNewData()
        insertJobList = prepareJobs(machinesList, insertItineraryList)
        resultReschedule = rescheduleInsertJobsSPT(resultSPT, time, insertJobList, machinesList)
        insertItineraryList.extend(itinerariesList)
        createGanttChart(resultReschedule, machinesList, insertItineraryList, time)
    elif yourChoice == "n":
        return 0


if __name__ == '__main__':
    main()