import random
import json
from numpy.random import choice
from sortedcollections import SortedDict
from clTask import Task
from clJob import Job
from clItinerary import  Itinerary
from clMachine import Machine
import logging
logging.basicConfig(level=logging.INFO)

# =========================================================================================

def prepareJobs(machinesList, itinerariesList):
    """Converts available data to list of jobs on which is calculations and graphs made"""
    jobsList = []
    itineraryColors = []

    pastelFactor = random.uniform(0, 1)
    # parse all tasks from all itineraries
    for idItinerary, itineraryObj in enumerate(itinerariesList):
        itineraryColors.append(
            generate_new_color(itineraryColors, pastelFactor))  # create new color for every new itinerary
        for idTask, taskObj in enumerate(itineraryObj.tasksList):
            for index, mach in enumerate(machinesList):
                if mach.name == taskObj.machine.name:
                    if itineraryObj.name == "Itinerary 0":
                        jobsList.append(Job(itineraryObj.name, itineraryColors[idItinerary], idTask + 1, 0,
                                           taskObj.machine.name, index, taskObj.duration))
                    else:
                        jobsList.append(Job(itineraryObj.name, itineraryColors[idItinerary], idTask + 1, idItinerary + 1,
                                        taskObj.machine.name, index, taskObj.duration))
                    break
    return jobsList


def algorithmSPT(aJobsList, machinesList):
    """
    SPT/SJF heuristic algorithm for job shop problem
    """

    time = {} # 记录某一时间各机器前的任务等待队列，相当于时间进度条，模拟时间流逝，推进排队
    waitingOperations = {}
    currentTimeOnMachines = {}  #当前机器时间，可以用来更新time
    jobsListToExport = []

    # initialize machines times and get
    # first waiting operations for each machine
    # global machinesList, itinerariesList
    for machine in machinesList:
        waitingOperations[machine.name] = [job for job in aJobsList if
                                           job.machine == machine.name and job.idOperation == 1]
        waitingOperations[machine.name].sort(key=lambda j: j.duration)
        currentTimeOnMachines[machine.name] = 0

    time[0] = waitingOperations

    for keyMach, operations in waitingOperations.items():
        # for each waiting task in front of machine set time to 0, update
        # properties
        if len(operations):
            operations[0].startTime = 0
            operations[0].completed = True
            operations[0].assignedMachine = keyMach

            # push task to production, and create new event to stop at,
            # on ending time, then update machines time
            jobsListToExport.append(operations[0])
            currentTimeOnMachines[keyMach] = operations[0].getEndTime()
            time[currentTimeOnMachines[keyMach]] = {}

    while len(jobsListToExport) != len(aJobsList):
        for t, operations in time.items():
            operations = getWaitingOperationsSPT(aJobsList, float(t), machinesList)

            for keyMach, tasks in operations.items():
                if len(tasks):
                    if float(t) < currentTimeOnMachines[tasks[0].machine]:
                        continue

                    tasks[0].startTime = float(t)
                    tasks[0].completed = True
                    tasks[0].assignedMachine = keyMach

                    jobsListToExport.append(tasks[0])

                    currentTimeOnMachines[keyMach] = tasks[0].getEndTime()
                    time[currentTimeOnMachines[keyMach]] = {}

            del time[t]
            break

        time = SortedDict(time)  # chronological order

    return jobsListToExport


def getWaitingOperationsSPT(aJobsList, time, machinesList):
    """Get waiting jobs at current time in shortest duration order"""

    incomingOperations = {}
    assignedJobsForMachine = []

    # global machinesList
    for mach in machinesList:
        assignedJobsForMachine = [job for job in aJobsList if job.completed == False and job.machine == mach.name]
        incomingOperations[mach.name] = []

        for j in assignedJobsForMachine:
            if j.idOperation == 1:
                incomingOperations[mach.name].append(j)
            else:
                previousTask = [job for job in aJobsList if
                                job.itinerary == j.itinerary and job.idOperation == j.idOperation - 1 and job.endTime <= time]
                if len(previousTask):
                    if previousTask[0].completed:
                        incomingOperations[mach.name].append(j)
        # sort added jobs by duration
        incomingOperations[mach.name].sort(key=lambda j: j.duration)
    return incomingOperations


def color_distance(c1,c2):
    return sum([abs(x[0] - x[1]) for x in zip(c1,c2)])
def get_random_color(pastel_factor=0.5):
    return [(x + pastel_factor) / (1.0 + pastel_factor) for x in [random.uniform(0,1.0) for i in [1,2,3]]]
def generate_new_color(existing_colors, pastel_factor=0.5):
    """Generate new color if not exist in existing array of colors"""
    max_distance = None
    best_color = None
    for i in range(0, 100):
        color = get_random_color(pastel_factor=pastel_factor)
        if not existing_colors:
            return color
        best_distance = min([color_distance(color, c) for c in existing_colors])
        if not max_distance or best_distance > max_distance:
            max_distance = best_distance
            best_color = color
    return best_color


def reschedulingSPT(jobsListExportPrevious, recheduleTime, insertJobsList, machinesList):
    """

    :param jobsListExportPrevious:
    :param recheduleTime:
    :param insertJobsList:
    :param machinesList:
    :return: jobsListToExportNew
    """
    time = {}
    allPreviousOperations = {}
    rescheduleOperations = {}
    rescheduleJobsList = []
    currentTimeOnMachines = {}
    jobsListToExportNew = []
    unchangedOperations = {}
    # 遍历机器，生成每个机器前工序集合和需要重调度的工序集合
    for machine in machinesList:
        allPreviousOperations[machine.name] = [job for job in jobsListExportPrevious if
                                               job.machine == machine.name]
        allPreviousOperations[machine.name].sort(key=lambda j: j.startTime)
        rescheduleOperations[machine.name] = [job for job in jobsListExportPrevious if
                                              job.machine == machine.name and job.startTime >= recheduleTime]
        rescheduleOperations[machine.name].sort(key=lambda j: j.startTime)
        #重调度时刻机器时间更新
        unchangedLength = len(allPreviousOperations[machine.name]) - len(rescheduleOperations[machine.name])
        unchangedOperations[machine.name] = allPreviousOperations[machine.name][0:unchangedLength]
        currentTimeOnMachines[machine.name] = unchangedOperations[machine.name][-1].endTime


        if currentTimeOnMachines[machine.name] < recheduleTime:
            currentTimeOnMachines[machine.name] = recheduleTime
        # 初始化各机器时间
        time[currentTimeOnMachines[machine.name]] = {}

        # 更新各机器下重调度工序状态
        unchangedOperations[machine.name][-1].completed = True
        for job in rescheduleOperations[machine.name]:
            job.startTime = 0
            job.completed = False
        # 输出无需重调度的任务结果
        for job in unchangedOperations[machine.name]:
            jobsListToExportNew.append(job)
    for machine in machinesList:
        #各机器下添加插入的任务
        for job in insertJobsList:
            if job.machine == machine.name:
                rescheduleOperations[machine.name].append(job)
        #生成重调度列表
        for job in rescheduleOperations[machine.name]:
            rescheduleJobsList.append(job)
    allJobsList = jobsListToExportNew + rescheduleJobsList
    # 调度时间初始化
    time = SortedDict(time)
    while len(jobsListToExportNew) < len(jobsListExportPrevious) + len(insertJobsList):
        for t, operations in time.items():
            operations = rescheduleGetWaitingOperationsSPT(allJobsList, float(t), machinesList)

            for keyMach, tasks in operations.items():
                if len(tasks):
                    if float(t) < currentTimeOnMachines[tasks[0].machine]:
                        continue
                    tasks[0].startTime = float(t)
                    tasks[0].completed = True
                    tasks[0].assignedMachine = keyMach

                    jobsListToExportNew.append(tasks[0])

                    currentTimeOnMachines[keyMach] = tasks[0].getEndTime()
                    time[currentTimeOnMachines[keyMach]] = {}

            del time[t]
            break
        time = SortedDict(time)  # chronological order
    finalOperation = {}
    for machine in machinesList:
        finalOperation[machine] = [job for job in jobsListToExportNew if job.machine == machine.name]
    return jobsListToExportNew


def rescheduleGetWaitingOperationsSPT(aJobsList, nowTime, machinesList):
    """Get waiting jobs at current time in shortest duration order"""

    incomingOperations = {}
    assignedJobsForMachine = []

    # global machinesList
    for mach in machinesList:
        assignedJobsForMachine = [job for job in aJobsList if job.completed == False and job.machine == mach.name]
        incomingOperations[mach.name] = []

        for j in assignedJobsForMachine:
            if j.idOperation == 1:
                incomingOperations[mach.name].append(j)
            else:
                previousTask = [job for job in aJobsList if
                                job.itinerary == j.itinerary and job.idOperation == j.idOperation - 1 and job.endTime <= nowTime]
                if len(previousTask):
                    if previousTask[0].completed:
                        incomingOperations[mach.name].append(j)
        # sort added jobs by duration
        incomingOperations[mach.name].sort(key=lambda j: j.duration)
        # 将该时刻等待队列中的紧急订单插入队首
        for job in incomingOperations[mach.name]:
            if 0 == job.idItinerary:
                temp = job
                incomingOperations[mach.name].remove(job)
                incomingOperations[mach.name].insert(0, temp)
                break
    return incomingOperations



