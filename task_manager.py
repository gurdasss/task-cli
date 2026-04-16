from task import Task

# These are some predefined predicates that can be used to filter tasks based on their state.
GET_ONLY_PENDING_TASKS = lambda task: task.state == Task.State.PENDING
GET_ONLY_DONE_TASKS = lambda task: task.state == Task.State.DONE
GET_ONLY_IN_PROGRESS_TASKS = lambda task: task.state == Task.State.IN_PROGRESS


class TaskManager:

    def __init__(self):
        self.tasks = []

    def add_task(self, description):
        self.tasks.append(Task(description=description))

    def del_task(self, task_id):
        self.tasks = list(filter(lambda task: task.id != task_id, self.tasks))

    def update_task(self, task_id, description):
        task_to_update = next(filter(lambda task: task.id == task_id, self.tasks), None)
        if not task_to_update:
            print(f"Task with id {task_id} not found.")
            return
        task_to_update.update_description(description)

    def update_task_state(self, task_id, state):
        task_to_update = next(filter(lambda task: task.id == task_id, self.tasks), None)
        if task_to_update and state in Task.State:
            if state == Task.State.DONE:
                task_to_update.done()
            elif state == Task.State.PENDING:
                task_to_update.pending()
            elif state == Task.State.IN_PROGRESS:
                task_to_update.in_progress()
        else:
            print(f"Task with id {task_id} not found.")

    def get_filtered_tasks(self, predicate=None):
        if predicate:
            return list(filter(predicate, self.tasks))
        return self.tasks

    def show_tasks(self, tasks=None):
        if tasks is None:
            tasks = self.tasks
        for task in tasks:
            print(
                f"ID: {task.id}, Description: {task.description}, State: {task.state}, Created At: {task.created_at}, Updated At: {task.updated_at}"
            )


task_manager = TaskManager()
task_manager.add_task("Buy groceries")
task_manager.add_task("Finish the report")
# task_manager.update_task_state(1, Task.State.IN_PROGRESS)
# task_manager.update_task(1, "Buy groceries and cook dinner")
task_manager.show_tasks(task_manager.get_filtered_tasks())
