import subprocess
import os
import re
from task_manager import (
    TaskManager,
    GET_ONLY_DONE_TASKS,
    GET_ONLY_PENDING_TASKS,
    GET_ONLY_IN_PROGRESS_TASKS,
)
import json
from task import Task


def clear_screen():
    subprocess.call("cls" if os.name == "nt" else "clear", shell=True)


if __name__ == "__main__":
    task_manager = TaskManager()
    json_file_path = "tasks.json"
    # Load tasks from JSON file if it exists
    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as f:

            tasks_data = json.load(f)
            for task_data in tasks_data:
                task = Task(description=task_data["description"])
                task.id = task_data["id"]
                task.created_at = task_data["created_at"]
                task.updated_at = task_data["updated_at"]
                task.state = Task.State(task_data["state"])
                task_manager.tasks.append(task)
                task.task_id = max(task.task_id, task.id)  # Ensure task_id is updated to the max ID

    while True:
        current_input = input("task-cli> ")
        # Need to split the input into command and arguments
        # and the separator will be space, and quotes should be handled as well
        command, *args = re.split(
            r'\s+(?=(?:[^"]*"[^"]*")*[^"]*$)', current_input.strip()
        )  # Split the input into command and arguments
        print(f"Command: {command}, Arguments: {args}")

        if command == "cls":
            clear_screen()
        elif command == "exit":
            break
        elif command == "add":
            if not args:
                print("Description is required for adding a task.")
                continue
            description = " ".join(args).strip('"')
            task_manager.add_task(description)
            print(f"Task added successfully (ID: {task_manager.tasks[-1].id})")
        elif command == "del":
            if not args:
                print("Task ID is required for deleting a task.")
                continue
            try:
                task_id = int(args[0])
                task_manager.del_task(task_id)
                print(f"Task deleted successfully (ID: {task_id})")
            except ValueError:
                print("Invalid Task ID. Please enter a numeric value.")

        # Why don't we have a single update command that can update both description and state? We can use a flag to indicate which one to update.
        # So, the first arg will be the task ID, and the second arg will be the field to update (description or state), and the third arg will be the new value.
        elif command == "update":
            if len(args) < 3:
                print("Task ID, field, and new value are required for updating a task.")
                continue
            try:
                task_id = int(args[0])
                field = args[1]
                value = " ".join(args[2:]).strip('"')
                print(
                    f"Updating task with ID: {task_id}, Field: {field}, New Value: {value}"
                )
                if field == "-d":
                    task_manager.update_task(task_id, description=value)
                elif field == "-s":
                    task_manager.update_task_state(task_id, state=value)
                else:
                    print("Invalid field. Use '-d' for description or '-s' for state.")
                    continue
                print(f"Task updated successfully (ID: {task_id})")
            except ValueError:
                print("Invalid Task ID. Please enter a numeric value.")
            except Exception as e:
                print(str(e))
        elif command == "list":
            if len(args) > 1:
                print(
                    "Too many arguments for list command. Use 'done', 'pending', or 'in_progress' to filter tasks."
                )
                continue
            if not args:
                tasks = task_manager.get_filtered_tasks()
            elif args[0] == "done":
                tasks = task_manager.get_filtered_tasks(GET_ONLY_DONE_TASKS)
            elif args[0] == "pending":
                tasks = task_manager.get_filtered_tasks(GET_ONLY_PENDING_TASKS)
            elif args[0] == "in_progress":
                tasks = task_manager.get_filtered_tasks(GET_ONLY_IN_PROGRESS_TASKS)
            else:
                print(
                    "Invalid argument for list command. Use 'done', 'pending', or 'in_progress'."
                )
                continue
            if not tasks:
                print("No tasks found.")
            else:
                for task in tasks:
                    print(
                        f"ID: {task.id}, Description: {task.description}, Status: {task.state}, Created At: {task.created_at}, Updated At: {task.updated_at}"
                    )
        
        # Save tasks to JSON file before exiting
        with open(json_file_path, "w") as f:
            json.dump([task.to_dict() for task in task_manager.tasks], f)
