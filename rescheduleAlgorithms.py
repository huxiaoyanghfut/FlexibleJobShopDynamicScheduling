from sortedcollections import SortedDict
from clTask import Task
from clJob import Job
from clItinerary import  Itinerary
from clMachine import Machine
#插入紧急订单重调度
def rescheduleInsertJobsSPT(jobsListExportPrevious, recheduleTime, insertJobsList, machinesList):
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
                                               job.assignedMachine == machine.name]
        allPreviousOperations[machine.name].sort(key=lambda j: j.startTime)
        rescheduleOperations[machine.name] = [job for job in jobsListExportPrevious if
                                              job.assignedMachine == machine.name and job.startTime >= recheduleTime]
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
        #生成重调度列表
        for job in rescheduleOperations[machine.name]:
            rescheduleJobsList.append(job)
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


def GetWaitingOperationsSPT(aJobsList, nowTime, machinesList,  currentTimeOnMachines):
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

    # TODO:更改优先级情况下重调度
    # TODO:机器故障下重调度
