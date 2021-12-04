from sortedcollections import SortedDict
from clTask import Task
from clJob import Job
from clItinerary import  Itinerary
from clMachine import Machine

def rescheduleInsertJobsSPT(jobsListExportPrevious, rescheduleTime, insertJobsList, machinesList):
    """
    插入紧急订单重调度
    :param jobsListExportPrevious: 任务初始调度结果
    :param rescheduleTime: 重调度时间
    :param insertJobsList: 插入的任务列表
    :param machinesList: 当前可用的机器列表
    :return: jobsListToExportNew 任务重调度结果
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
                                               job.assignedMachine == machine.name]
        allPreviousOperations[machine.name].sort(key=lambda j: j.startTime)
        rescheduleOperations[machine.name] = [job for job in jobsListExportPrevious if
                                              job.assignedMachine == machine.name and job.startTime >= rescheduleTime]
        rescheduleOperations[machine.name].sort(key=lambda j: j.startTime)

        #重调度时刻机器时间更新
        unchangedLength = len(allPreviousOperations[machine.name]) - len(rescheduleOperations[machine.name])
        unchangedOperations[machine.name] = allPreviousOperations[machine.name][0:unchangedLength]
        currentTimeOnMachines[machine.name] = unchangedOperations[machine.name][-1].endTime
        if currentTimeOnMachines[machine.name] < rescheduleTime:
            currentTimeOnMachines[machine.name] = rescheduleTime

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
        #生成重调度列表
        for job in rescheduleOperations[machine.name]:
            rescheduleJobsList.append(job)
    for job in insertJobsList:
        job.priority = 5
    rescheduleJobsList.extend(insertJobsList)
    allJobsList = jobsListToExportNew + rescheduleJobsList
    # 调度时间初始化
    time = SortedDict(time)
    while len(jobsListToExportNew) < len(jobsListExportPrevious) + len(insertJobsList):
        for t, operations in time.items():
            operations = GetWaitingOperationsSPT(allJobsList, float(t), machinesList,  currentTimeOnMachines)

            for keyMach, tasks in operations.items():
                if len(tasks):
                    if float(t) < currentTimeOnMachines[keyMach]:
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
    return jobsListToExportNew

def recheduleChangePriority(jobsListExportPrevious, rescheduleTime,priorItinerary, machinesList):
    """
    :param jobsListExportPrevious: 初始调度结果
    :param rescheduleTime: 重调度时间
    :param priorItinerary: 优先的任务序号
    :param machinesList: 可用机器列表
    :return: jobsListToExportNew: 重调度方案
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
                                               job.assignedMachine == machine.name]
        allPreviousOperations[machine.name].sort(key=lambda j: j.startTime)
        rescheduleOperations[machine.name] = [job for job in jobsListExportPrevious if
                                              job.assignedMachine == machine.name and job.startTime >= rescheduleTime]
        rescheduleOperations[machine.name].sort(key=lambda j: j.startTime)

        # 重调度时刻机器时间更新
        unchangedLength = len(allPreviousOperations[machine.name]) - len(rescheduleOperations[machine.name])
        unchangedOperations[machine.name] = allPreviousOperations[machine.name][0:unchangedLength]
        currentTimeOnMachines[machine.name] = unchangedOperations[machine.name][-1].endTime
        if currentTimeOnMachines[machine.name] < rescheduleTime:
            currentTimeOnMachines[machine.name] = rescheduleTime

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
        # 生成重调度列表
        for job in rescheduleOperations[machine.name]:
            if job.idItinerary == priorItinerary:
                job.priority = 5
            rescheduleJobsList.append(job)

    allJobsList = jobsListToExportNew + rescheduleJobsList
    # 调度时间初始化
    time = SortedDict(time)
    while len(jobsListToExportNew) < len(jobsListExportPrevious):
        for t, operations in time.items():
            operations = GetWaitingOperationsSPT(allJobsList, float(t), machinesList, currentTimeOnMachines)

            for keyMach, tasks in operations.items():
                if len(tasks):
                    if float(t) < currentTimeOnMachines[keyMach]:
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
    return jobsListToExportNew

def recheduleMachineFault(jobsListExportPrevious, rescheduleTime,faultyMachine, machinesList):
    pass
    #TODO

    time = {}
    allPreviousOperations = {}
    rescheduleOperations = {}
    rescheduleJobsList = []
    currentTimeOnMachines = {}
    jobsListToExportNew = []
    unchangedOperations = {}
    unscheduleItinerarys = []


    # 遍历机器，生成每个机器前工序集合和需要重调度的工序集合
    for machine in machinesList:
        allPreviousOperations[machine.name] = [job for job in jobsListExportPrevious if
                                               job.assignedMachine == machine.name]
        allPreviousOperations[machine.name].sort(key=lambda j: j.startTime)
        rescheduleOperations[machine.name] = [job for job in jobsListExportPrevious if
                                              job.assignedMachine == machine.name and job.startTime >= rescheduleTime]
        rescheduleOperations[machine.name].sort(key=lambda j: j.startTime)

        # 重调度时刻机器时间更新
        unchangedLength = len(allPreviousOperations[machine.name]) - len(rescheduleOperations[machine.name])
        unchangedOperations[machine.name] = allPreviousOperations[machine.name][0:unchangedLength]

        #如果故障机器上有未完工任务，则把该任务工艺路线后续任务不参与重调度


        currentTimeOnMachines[machine.name] = unchangedOperations[machine.name][-1].endTime
        if currentTimeOnMachines[machine.name] < rescheduleTime:
            currentTimeOnMachines[machine.name] = rescheduleTime

        # 初始化各机器时间
        time[currentTimeOnMachines[machine.name]] = {}

        # 更新各机器下重调度工序状态
        unchangedOperations[machine.name][-1].completed = True
        for job in rescheduleOperations[machine.name]:
            job.completed = False

        # 输出无需重调度的任务结果
        for job in unchangedOperations[machine.name]:
            jobsListToExportNew.append(job)

    # 1.先识别出故障机器前未完工任务（包括正在加工的）
    # 2. 遍历上述任务列表：
    #    如果任务可选机器列表长度为1，则重调度任务列表中不加入该任务；
    #    并且记录该任务的工艺路线号，后续是该工艺路线号的任务不参与调度；
    #    否则将任务加入重调度任务列表

    if unchangedOperations[faultyMachine][-1].endTime > rescheduleTime:
        unscheduleItinerarys.append(unchangedOperations[faultyMachine][-1].idItinerary)

    # 生成重调度初始列表
    for machine in machinesList:

        for job in rescheduleOperations[machine.name]:
            rescheduleJobsList.append(job)
    rescheduleJobsList.sort(key=lambda j: j.startTime)

    #得到受影响的工艺路线号
    for job in rescheduleOperations[faultyMachine]:
        if len(job.machine) == 1:
                unscheduleItinerarys.append(job.idItinerary)

    #去除受机器故障影响的任务
    rescheduleJobsListUpdate = []
    for job in rescheduleJobsList:
        if job.idItinerary in unscheduleItinerarys:
            continue
        else:
            rescheduleJobsListUpdate.append(job)
    # 机器列表更新
    machinesAvailableList = [machine for machine in machinesList if machine.name != faultyMachine]
    allJobsList = jobsListToExportNew + rescheduleJobsListUpdate

    # 调度时间初始化
    time = SortedDict(time)
    while len(jobsListToExportNew) < len(allJobsList):
        for t, operations in time.items():
            operations = GetWaitingOperationsSPT(allJobsList, float(t), machinesAvailableList, currentTimeOnMachines, faultyMachine)

            for keyMach, tasks in operations.items():
                if len(tasks):
                    if float(t) < currentTimeOnMachines[keyMach]:
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
    return jobsListToExportNew



def GetWaitingOperationsSPT(aJobsList, nowTime, machinesList,  currentTimeOnMachines, faultyMachine=""):
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
                        if mac == faultyMachine:
                            continue
                        elif currentTimeOnMachines[mac] <  currentTimeOnMachines[minTimeMachine]:
                            minTimeMachine = mac
                    if minTimeMachine == mach.name:
                        assignedJobsForMachine.append(job)

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
            if job.priority > 0:
                temp = job
                incomingOperations[mach.name].remove(job)
                incomingOperations[mach.name].insert(0, temp)
                break
    return incomingOperations
