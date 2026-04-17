import pytest
from unittest.mock import patch, call
from task import Task
from task_manager import (
    TaskManager,
    GET_ONLY_PENDING_TASKS,
    GET_ONLY_DONE_TASKS,
    GET_ONLY_IN_PROGRESS_TASKS,
)


class TestTaskManager:
    """Test suite for the TaskManager class"""

    @pytest.fixture(autouse=True)
    def reset_task_id(self):
        """Reset the class-level task_id counter before each test"""
        Task.task_id = 0
        yield
        Task.task_id = 0

    @pytest.fixture
    def manager(self):
        """Fixture to create a fresh TaskManager instance"""
        return TaskManager()

    @pytest.fixture
    def populated_manager(self):
        """Fixture to create a TaskManager with multiple tasks"""
        manager = TaskManager()
        manager.add_task("Task 1")
        manager.add_task("Task 2")
        manager.add_task("Task 3")
        return manager

    # Tests for __init__ method
    def test_init_creates_empty_task_list(self):
        """Test that TaskManager initializes with an empty task list"""
        manager = TaskManager()

        assert isinstance(manager.tasks, list)
        assert len(manager.tasks) == 0

    def test_init_creates_independent_managers(self):
        """Test that multiple TaskManager instances have independent task lists"""
        manager1 = TaskManager()
        manager2 = TaskManager()

        manager1.add_task("Task 1")

        assert len(manager1.tasks) == 1
        assert len(manager2.tasks) == 0

    # Tests for add_task method
    def test_add_task_creates_task_with_description(self, manager):
        """Test that add_task creates a task with the correct description"""
        description = "Write unit tests"

        manager.add_task(description)

        assert len(manager.tasks) == 1
        assert manager.tasks[0].description == description

    def test_add_task_creates_task_object(self, manager):
        """Test that add_task creates a proper Task instance"""
        manager.add_task("Test task")

        assert isinstance(manager.tasks[0], Task)

    def test_add_task_assigns_sequential_ids(self, manager):
        """Test that adding multiple tasks assigns sequential IDs"""
        manager.add_task("Task 1")
        manager.add_task("Task 2")
        manager.add_task("Task 3")

        assert manager.tasks[0].id == 1
        assert manager.tasks[1].id == 2
        assert manager.tasks[2].id == 3

    def test_add_task_sets_initial_state_to_pending(self, manager):
        """Test that newly added tasks have PENDING state"""
        manager.add_task("New task")

        assert manager.tasks[0].state == Task.State.PENDING

    def test_add_task_multiple_times_increases_list_size(self, manager):
        """Test that adding multiple tasks increases the task list size"""
        assert len(manager.tasks) == 0

        manager.add_task("Task 1")
        assert len(manager.tasks) == 1

        manager.add_task("Task 2")
        assert len(manager.tasks) == 2

        manager.add_task("Task 3")
        assert len(manager.tasks) == 3

    # Tests for del_task method
    def test_del_task_removes_task_by_id(self, populated_manager):
        """Test that del_task removes the correct task by ID"""
        initial_count = len(populated_manager.tasks)
        task_id_to_delete = populated_manager.tasks[1].id

        populated_manager.del_task(task_id_to_delete)

        assert len(populated_manager.tasks) == initial_count - 1
        assert all(task.id != task_id_to_delete for task in populated_manager.tasks)

    def test_del_task_with_nonexistent_id_does_nothing(self, populated_manager):
        """Test that deleting a non-existent task ID doesn't affect the list"""
        initial_count = len(populated_manager.tasks)

        populated_manager.del_task(999)

        assert len(populated_manager.tasks) == initial_count

    def test_del_task_removes_first_task(self, populated_manager):
        """Test that del_task can remove the first task"""
        first_task_id = populated_manager.tasks[0].id

        populated_manager.del_task(first_task_id)

        assert all(task.id != first_task_id for task in populated_manager.tasks)

    def test_del_task_removes_last_task(self, populated_manager):
        """Test that del_task can remove the last task"""
        last_task_id = populated_manager.tasks[-1].id

        populated_manager.del_task(last_task_id)

        assert all(task.id != last_task_id for task in populated_manager.tasks)

    def test_del_task_on_empty_manager(self, manager):
        """Test that deleting from an empty manager doesn't cause errors"""
        manager.del_task(1)

        assert len(manager.tasks) == 0

    def test_del_task_removes_all_tasks_one_by_one(self, populated_manager):
        """Test that all tasks can be removed sequentially"""
        task_ids = [task.id for task in populated_manager.tasks]

        for task_id in task_ids:
            populated_manager.del_task(task_id)

        assert len(populated_manager.tasks) == 0

    # Tests for update_task method
    def test_update_task_changes_description(self, populated_manager):
        """Test that update_task changes the task description"""
        task_id = populated_manager.tasks[0].id
        new_description = "Updated description"

        populated_manager.update_task(task_id, new_description)

        assert populated_manager.tasks[0].description == new_description

    def test_update_task_sets_updated_at_timestamp(self, populated_manager):
        """Test that update_task sets the updated_at timestamp"""
        task_id = populated_manager.tasks[0].id
        assert populated_manager.tasks[0].updated_at is None

        populated_manager.update_task(task_id, "New description")

        assert populated_manager.tasks[0].updated_at is not None

    def test_update_task_preserves_state(self, populated_manager):
        """Test that update_task doesn't change the task state"""
        task_id = populated_manager.tasks[0].id
        populated_manager.tasks[0].in_progress()
        initial_state = populated_manager.tasks[0].state

        populated_manager.update_task(task_id, "Updated")

        assert populated_manager.tasks[0].state == initial_state

    def test_update_task_with_nonexistent_id_prints_message(self, manager, capsys):
        """Test that updating a non-existent task prints an error message"""
        manager.update_task(999, "New description")

        captured = capsys.readouterr()
        assert "Task with id 999 not found" in captured.out

    def test_update_task_doesnt_affect_other_tasks(self, populated_manager):
        """Test that updating one task doesn't affect others"""
        task_id = populated_manager.tasks[1].id
        other_descriptions = [
            populated_manager.tasks[0].description,
            populated_manager.tasks[2].description,
        ]

        populated_manager.update_task(task_id, "Updated middle task")

        assert populated_manager.tasks[0].description == other_descriptions[0]
        assert populated_manager.tasks[2].description == other_descriptions[1]

    # Tests for update_task_state method
    def test_update_task_state_to_done(self, populated_manager):
        """Test that update_task_state changes state to DONE"""
        task_id = populated_manager.tasks[0].id

        populated_manager.update_task_state(task_id, Task.State.DONE)

        assert populated_manager.tasks[0].state == Task.State.DONE

    def test_update_task_state_to_pending(self, populated_manager):
        """Test that update_task_state changes state to PENDING"""
        task_id = populated_manager.tasks[0].id
        populated_manager.tasks[0].in_progress()

        populated_manager.update_task_state(task_id, Task.State.PENDING)

        assert populated_manager.tasks[0].state == Task.State.PENDING

    def test_update_task_state_to_in_progress(self, populated_manager):
        """Test that update_task_state changes state to IN_PROGRESS"""
        task_id = populated_manager.tasks[0].id

        populated_manager.update_task_state(task_id, Task.State.IN_PROGRESS)

        assert populated_manager.tasks[0].state == Task.State.IN_PROGRESS

    def test_update_task_state_sets_updated_at(self, populated_manager):
        """Test that update_task_state sets the updated_at timestamp"""
        task_id = populated_manager.tasks[0].id
        assert populated_manager.tasks[0].updated_at is None

        populated_manager.update_task_state(task_id, Task.State.DONE)

        assert populated_manager.tasks[0].updated_at is not None

    def test_update_task_state_with_nonexistent_id_prints_message(
        self, manager, capsys
    ):
        """Test that updating state of non-existent task prints an error message"""
        manager.update_task_state(999, Task.State.DONE)

        captured = capsys.readouterr()
        assert "Task with id 999 not found" in captured.out

    def test_update_task_state_with_invalid_state_prints_message(
        self, populated_manager, capsys
    ):
        """Test that updating with an invalid state prints an error message"""
        task_id = populated_manager.tasks[0].id

        populated_manager.update_task_state(task_id, "INVALID_STATE")

        captured = capsys.readouterr()
        assert "not found" in captured.out

    def test_update_task_state_transitions(self, populated_manager):
        """Test multiple state transitions on the same task"""
        task_id = populated_manager.tasks[0].id

        populated_manager.update_task_state(task_id, Task.State.IN_PROGRESS)
        assert populated_manager.tasks[0].state == Task.State.IN_PROGRESS

        populated_manager.update_task_state(task_id, Task.State.DONE)
        assert populated_manager.tasks[0].state == Task.State.DONE

        populated_manager.update_task_state(task_id, Task.State.PENDING)
        assert populated_manager.tasks[0].state == Task.State.PENDING

    # Tests for get_filtered_tasks method
    def test_get_filtered_tasks_without_predicate_returns_all(self, populated_manager):
        """Test that get_filtered_tasks without predicate returns all tasks"""
        result = populated_manager.get_filtered_tasks()

        assert len(result) == len(populated_manager.tasks)
        assert result == populated_manager.tasks

    def test_get_filtered_tasks_with_none_predicate_returns_all(
        self, populated_manager
    ):
        """Test that get_filtered_tasks with None predicate returns all tasks"""
        result = populated_manager.get_filtered_tasks(predicate=None)

        assert len(result) == len(populated_manager.tasks)
        assert result == populated_manager.tasks

    def test_get_filtered_tasks_returns_same_list_reference_without_predicate(
        self, populated_manager
    ):
        """Test that get_filtered_tasks returns the original list reference when no predicate is provided"""
        result = populated_manager.get_filtered_tasks()

        # When no predicate is provided, the implementation returns the original list
        assert result is populated_manager.tasks
        assert result == populated_manager.tasks

    def test_get_filtered_tasks_with_pending_predicate(self, manager):
        """Test filtering tasks with PENDING state"""
        manager.add_task("Pending task 1")
        manager.add_task("Pending task 2")
        manager.add_task("Done task")
        manager.tasks[2].done()

        result = manager.get_filtered_tasks(GET_ONLY_PENDING_TASKS)

        assert len(result) == 2
        assert all(task.state == Task.State.PENDING for task in result)

    def test_get_filtered_tasks_with_done_predicate(self, manager):
        """Test filtering tasks with DONE state"""
        manager.add_task("Task 1")
        manager.add_task("Task 2")
        manager.add_task("Task 3")
        manager.tasks[0].done()
        manager.tasks[2].done()

        result = manager.get_filtered_tasks(GET_ONLY_DONE_TASKS)

        assert len(result) == 2
        assert all(task.state == Task.State.DONE for task in result)

    def test_get_filtered_tasks_with_in_progress_predicate(self, manager):
        """Test filtering tasks with IN_PROGRESS state"""
        manager.add_task("Task 1")
        manager.add_task("Task 2")
        manager.add_task("Task 3")
        manager.tasks[1].in_progress()

        result = manager.get_filtered_tasks(GET_ONLY_IN_PROGRESS_TASKS)

        assert len(result) == 1
        assert result[0].state == Task.State.IN_PROGRESS

    def test_get_filtered_tasks_with_custom_predicate(self, manager):
        """Test filtering with a custom predicate"""
        manager.add_task("Buy groceries")
        manager.add_task("Write code")
        manager.add_task("Buy books")

        # Custom predicate: tasks with "Buy" in description
        buy_tasks_predicate = lambda task: "Buy" in task.description
        result = manager.get_filtered_tasks(buy_tasks_predicate)

        assert len(result) == 2
        assert all("Buy" in task.description for task in result)

    def test_get_filtered_tasks_returns_empty_when_no_matches(self, populated_manager):
        """Test that filtering returns empty list when no tasks match"""
        # Set all tasks to PENDING
        result = populated_manager.get_filtered_tasks(GET_ONLY_DONE_TASKS)

        assert len(result) == 0
        assert result == []

    def test_get_filtered_tasks_on_empty_manager(self, manager):
        """Test that filtering on empty manager returns empty list"""
        result = manager.get_filtered_tasks(GET_ONLY_PENDING_TASKS)

        assert result == []

    # Tests for predefined predicates
    def test_get_only_pending_tasks_predicate(self):
        """Test that GET_ONLY_PENDING_TASKS predicate works correctly"""
        pending_task = Task("Pending")
        done_task = Task("Done")
        done_task.done()

        assert GET_ONLY_PENDING_TASKS(pending_task) is True
        assert GET_ONLY_PENDING_TASKS(done_task) is False

    def test_get_only_done_tasks_predicate(self):
        """Test that GET_ONLY_DONE_TASKS predicate works correctly"""
        pending_task = Task("Pending")
        done_task = Task("Done")
        done_task.done()

        assert GET_ONLY_DONE_TASKS(done_task) is True
        assert GET_ONLY_DONE_TASKS(pending_task) is False

    def test_get_only_in_progress_tasks_predicate(self):
        """Test that GET_ONLY_IN_PROGRESS_TASKS predicate works correctly"""
        pending_task = Task("Pending")
        in_progress_task = Task("In Progress")
        in_progress_task.in_progress()

        assert GET_ONLY_IN_PROGRESS_TASKS(in_progress_task) is True
        assert GET_ONLY_IN_PROGRESS_TASKS(pending_task) is False

    # Integration tests
    def test_complete_workflow(self, manager):
        """Test a complete task management workflow"""
        # Add tasks
        manager.add_task("Task 1")
        manager.add_task("Task 2")
        manager.add_task("Task 3")
        assert len(manager.tasks) == 3

        # Update a task description
        manager.update_task(2, "Updated Task 2")
        assert manager.tasks[1].description == "Updated Task 2"

        # Change task states
        manager.update_task_state(1, Task.State.IN_PROGRESS)
        manager.update_task_state(3, Task.State.DONE)

        # Filter tasks
        pending = manager.get_filtered_tasks(GET_ONLY_PENDING_TASKS)
        assert len(pending) == 1

        in_progress = manager.get_filtered_tasks(GET_ONLY_IN_PROGRESS_TASKS)
        assert len(in_progress) == 1

        done = manager.get_filtered_tasks(GET_ONLY_DONE_TASKS)
        assert len(done) == 1

        # Delete a task
        manager.del_task(2)
        assert len(manager.tasks) == 2

    def test_edge_case_delete_and_filter(self, manager):
        """Test filtering after deleting tasks"""
        manager.add_task("Task 1")
        manager.add_task("Task 2")
        manager.add_task("Task 3")

        manager.tasks[0].done()
        manager.tasks[1].done()

        # Delete one done task
        manager.del_task(1)

        # Filter should still work correctly
        done_tasks = manager.get_filtered_tasks(GET_ONLY_DONE_TASKS)
        assert len(done_tasks) == 1
        assert done_tasks[0].id == 2

    def test_update_nonexistent_then_add_new_task(self, manager):
        """Test that operations on non-existent tasks don't affect new tasks"""
        # Try to update non-existent task
        manager.update_task(999, "Ghost task")

        # Add a real task
        manager.add_task("Real task")

        # Verify the real task is unaffected
        assert len(manager.tasks) == 1
        assert manager.tasks[0].description == "Real task"

    def test_massive_task_list_performance(self, manager):
        """Test that manager handles many tasks efficiently"""
        # Add 100 tasks
        for i in range(100):
            manager.add_task(f"Task {i}")

        assert len(manager.tasks) == 100

        # Update some states
        for i in range(0, 100, 3):
            manager.update_task_state(manager.tasks[i].id, Task.State.DONE)

        # Filter
        done_tasks = manager.get_filtered_tasks(GET_ONLY_DONE_TASKS)
        assert len(done_tasks) == 34  # 0, 3, 6, ..., 99 = 34 tasks

        # Delete half
        for task in manager.tasks[::2]:
            manager.del_task(task.id)

        assert len(manager.tasks) == 50
