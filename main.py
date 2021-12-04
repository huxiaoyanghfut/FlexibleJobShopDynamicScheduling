from algorithms import prepareJobs, algorithmSPT
from rescheduleAlgorithms import *
from ganttCreator import createGanttChart
from parseData import parseData
import copy
from parseNewData import parseNewData


def main():
    machinesList, itinerariesList = parseData(input("请输入数据保存路径："))
    jobsList = prepareJobs(machinesList, itinerariesList)
    resultSPT = algorithmSPT(copy.deepcopy(jobsList), machinesList)
    createGanttChart(resultSPT, machinesList, itinerariesList)
    loop = True
    while loop:
        yourChoice = input("是否需要进行重调度？[y/n]:")
        if yourChoice == "y":
            rescheduleTime = float(input("请输入重调度时间（0~Cmax之间）："))
            print("请选择重调度方式：")
            print(30 * "-", "MENU", 30 * "-")
            print("1. 插入紧急订单")
            print("2. 更改未完工工件的优先级")
            print("3. 机器故障")
            print("4. 退出")
            print(66 * "-")
            rescheduleChoice = input("输入你的选择 [1-4]: ")
            if rescheduleChoice == "1":
                savePath = input("请输入紧急订单保存路径[文件路径]:")
                insertItineraryList = parseNewData(savePath)
                insertJobList = prepareJobs(machinesList, insertItineraryList)
                resultInsertReschedule = rescheduleInsertJobsSPT(resultSPT, rescheduleTime, insertJobList, machinesList)
                insertItineraryList.extend(itinerariesList)
                createGanttChart(resultInsertReschedule, machinesList, itinerariesList, rescheduleTime)
            elif rescheduleChoice == "2":
                priorItinerary = int(input("请输入优先的工件序号:"))
                resultPriorReschedule = recheduleChangePriority(resultSPT, rescheduleTime, priorItinerary, machinesList)
                createGanttChart(resultPriorReschedule, machinesList, itinerariesList, rescheduleTime)
            elif rescheduleChoice == "3":
                faultyMachine = input("请输入发生故障的机器号[如：M3]：")
                resultFaultyReschedule = recheduleMachineFault(resultSPT, rescheduleTime, faultyMachine, machinesList)
                createGanttChart(resultFaultyReschedule, machinesList, itinerariesList, rescheduleTime)
            elif rescheduleChoice == "4":
                return 0
        elif yourChoice == "n":
            return 0

if __name__ == '__main__':
    main()
