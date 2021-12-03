import random
import json
from numpy.random import choice
from sortedcollections import SortedDict
from clTask import Task
from clJob import Job
from clItinerary import  Itinerary
from clMachine import Machine


# =========================================================================================

def prepareJobs(machinesList, itinerariesList):
    """Converts available data to list of jobs on which is calculations and graphs made"""
    jobsList = []
    itineraryColors = []

    pastelFactor = random.uniform(0, 1)
    # 从工艺路径任务中解析出每一个工序任务
    for idItinerary, itineraryObj in enumerate(itinerariesList):
    # 为每一条工艺路线创建不同的颜色
        itineraryColors.append(
            generate_new_color(itineraryColors, pastelFactor))
    #实例化每一个工序任务，创建工序任务列表
        for idTask, taskObj in enumerate(itineraryObj.tasksList):
            if itineraryObj.name == "Itinerary 0":
                jobsList.append(Job(itineraryObj.name, itineraryColors[idItinerary], idTask + 1, 0,
                                   taskObj.machine, taskObj.duration))
            else:
                jobsList.append(Job(itineraryObj.name, itineraryColors[idItinerary], idTask + 1, idItinerary + 1,
                                taskObj.machine, taskObj.duration))
    return jobsList


def algorithmSPT(aJobsList, machinesList):
    """
    SPT/SJF heuristic algorithm for job shop problem
    """
    # 记录某一时间各机器前的任务等待队列，相当于时间进度条，模拟时间流逝，推进排队
    time = {} 
    waitingOperations = {}
    # 当前机器时间，可以用来更新time
    currentTimeOnMachines = {}  
    jobsListToExport = []

    # initialize machines times and get
    # first waiting operations for each machine
    # global machinesList, itinerariesList

    
    for machine in machinesList:
        currentTimeOnMachines[machine.name] = 0
    #初始化各机器当前等待队列
    for machine in machinesList:
        waitingOperations[machine.name] = []
        for job in aJobsList:
            if job.idOperation == 1 and machine.name in job.machine:
                #找出当前任务可选机器中机器时间最小的机器
                if len(job.machine) == 1:
                    waitingOperations[machine.name].append(job)
                else:
                    minTimeMachine = machine.name
                    for mac in job.machine:
                        if currentTimeOnMachines[mac] <  currentTimeOnMachines[minTimeMachine]:
                            minTimeMachine = mac.name
                    if minTimeMachine == machine.name:
                        waitingOperations[machine.name].append(job)

        waitingOperations[machine.name].sort(key=lambda j: j.duration)

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
            operations = getWaitingOperationsSPT(aJobsList, float(t), machinesList, currentTimeOnMachines)

            for keyMach, tasks in operations.items():
                if len(tasks):
                    if float(t) < currentTimeOnMachines[keyMach]:
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


def getWaitingOperationsSPT(aJobsList, time, machinesList, currentTimeOnMachines):
    """Get waiting jobs at current time in shortest duration order"""

    incomingOperations = {}

    # global machinesList
    for mach in machinesList:
        assignedJobsForMachine = []
        for job in aJobsList:
            if job.completed == False and mach.name in job.machine:
                if len(job.machine) ==1:
                    assignedJobsForMachine.append(job)
                else:
                    minTimeMachine = mach.name
                    for mac in job.machine:
                        if currentTimeOnMachines[mac] <  currentTimeOnMachines[minTimeMachine]:
                            minTimeMachine = mac
                    if minTimeMachine == mach.name:
                        assignedJobsForMachine.append(job)
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



