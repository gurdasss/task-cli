from enum import StrEnum, auto
from datetime import datetime


class Task:
    task_id = 0

    # I need to ensure that while saving the state
    # of any task, it's properly converted to a str and for that,
    # StrEnum ensures the members are treated as strings.
    class State(StrEnum):
        DONE = auto()
        PENDING = auto()
        IN_PROGRESS = auto()

    def __init__(self, description):
        self.id = self.get_next_id()
        self.description = description
        # Each newly created task will be pending
        self.state = self.State.PENDING
        self.created_at = self.get_current_time()
        self.updated_at = None

    @classmethod
    def get_next_id(cls):
        cls.task_id += 1
        return cls.task_id

    @staticmethod
    def get_current_time():
        # 1. Get the current local time
        # 2. Format it
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _update_state(self, state):
        """This method will update the state as well as updated_at property"""
        if self.state == state:
            return  # No state change, so we can skip updating
        self.state = state
        self.updated_at = self.get_current_time()

    def done(self):
        self._update_state(self.State.DONE)

    def pending(self):
        self._update_state(self.State.PENDING)

    def in_progress(self):
        self._update_state(self.State.IN_PROGRESS)

    def update_description(self, description):
        self.description = description
        self.updated_at = self.get_current_time()
