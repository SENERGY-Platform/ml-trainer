from tasks.task import Task
from data.preprocessors.consumption import ConsumptionPreProcessor

class TimeSeriesTask(Task):
    def __init__(self, frequency) -> None:
        super().__init__()
        self.frequency = frequency