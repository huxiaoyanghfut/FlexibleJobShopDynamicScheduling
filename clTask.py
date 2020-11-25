#=========================================================================================
class Task():
    """Task is a part of Itinerary """

    def __init__(self, aName, aDuration, MachinesList):
        self.name = aName
        self.duration = aDuration
        self.machine = MachinesList
        self.taskChanged = False

    def exportToDict(self):
        """Serialize information about Task into dictionary"""
        exData = {}
        exData['taskName'] = self.name
        exData['taskMachine'] = self.machine.exportToDict()
        exData['taskDuration'] = self.duration
        return exData