# Task Tracker CLI

A simple command-line task tracker for managing todo items with persistent storage in `tasks.json`.

This project is inspired by the [Task Tracker roadmap](https://roadmap.sh/projects/task-tracker).

## Features

- Add a task with a description
- Delete a task by ID
- Update a task description or state
- List all tasks or filter by status
- Persist tasks across runs using JSON storage
- Supports task states: `pending`, `in_progress`, and `done`

## Requirements

- Python 3.11 or newer
- Dependencies from `requirements.txt` (mostly for testing)

## Setup

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies

```bash
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

## Usage

Start the CLI from the repository root:

```bash
python main.py
```

You will see a prompt like:

```bash
task-cli>
```

Enter commands to manage tasks.

## Commands

- `add <description>`
  - Add a new task.
  - Example: `add "Write project README"`

- `del <task_id>`
  - Delete a task by its ID.
  - Example: `del 2`

- `update <task_id> -d "<new description>"`
  - Update the description of an existing task.
  - Example: `update 3 -d "Finish test coverage"`

- `update <task_id> -s <state>`
  - Update the state of an existing task.
  - Valid states: `pending`, `in_progress`, `done`
  - Example: `update 3 -s done`

- `list`
  - Show all tasks.

- `list done`
  - Show only completed tasks.

- `list pending`
  - Show only pending tasks.

- `list in_progress`
  - Show only tasks in progress.

- `cls`
  - Clear the terminal screen.

- `exit`
  - Exit the CLI and save tasks to `tasks.json`.

## Example Workflow

```bash
python main.py
# task-cli> add Plan weekend trip
# task-cli> add Buy groceries
# task-cli> list
# task-cli> update 1 -s in_progress
# task-cli> list in_progress
# task-cli> update 2 -s done
# task-cli> exit
```

## Notes

- Tasks are stored in `tasks.json` in the project root.
- Each task stores an ID, description, state, creation timestamp, and last updated timestamp.
- If `tasks.json` exists when the CLI starts, tasks are loaded automatically.

## Testing

Run the test suite with:

```bash
pytest
```
