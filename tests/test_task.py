import pytest
from datetime import datetime
from unittest.mock import patch
from task import Task


class TestTask:
    """Test suite for the Task class"""

    @pytest.fixture(autouse=True)
    def reset_task_id(self):
        """Reset the class-level task_id counter before each test"""
        Task.task_id = 0
        yield
        Task.task_id = 0

    @pytest.fixture
    def mock_time(self):
        """Fixture to provide a consistent mock time"""
        return "2024-04-16 10:30:45"

    @pytest.fixture
    def task(self, mock_time):
        """Fixture to create a basic task with mocked time"""
        with patch("task.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = mock_time
            return Task("Test task description")

    # Tests for __init__ method
    def test_init_creates_task_with_correct_id(self):
        """Test that task initialization assigns correct sequential IDs"""
        task1 = Task("First task")
        task2 = Task("Second task")
        task3 = Task("Third task")

        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3

    def test_init_sets_description(self):
        """Test that task initialization sets the description"""
        description = "My important task"
        task = Task(description)

        assert task.description == description

    def test_init_sets_state_to_pending(self):
        """Test that new tasks start with PENDING state"""
        task = Task("New task")

        assert task.state == Task.State.PENDING

    def test_init_sets_created_at(self, mock_time):
        """Test that created_at is set to current time"""
        with patch("task.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = mock_time
            task = Task("Task with time")

            assert task.created_at == mock_time

    def test_init_sets_updated_at_to_none(self):
        """Test that updated_at is initially None"""
        task = Task("New task")

        assert task.updated_at is None

    # Tests for get_next_id class method
    def test_get_next_id_increments_counter(self):
        """Test that get_next_id increments the class-level counter"""
        initial_id = Task.task_id

        id1 = Task.get_next_id()
        id2 = Task.get_next_id()
        id3 = Task.get_next_id()

        assert id1 == initial_id + 1
        assert id2 == initial_id + 2
        assert id3 == initial_id + 3

    def test_get_next_id_returns_unique_ids(self):
        """Test that get_next_id returns unique IDs across multiple calls"""
        ids = [Task.get_next_id() for _ in range(10)]

        assert len(ids) == len(set(ids))  # All IDs should be unique

    # Tests for get_current_time static method
    def test_get_current_time_format(self):
        """Test that get_current_time returns correctly formatted time string"""
        with patch("task.datetime") as mock_datetime:
            mock_now = datetime(2024, 4, 16, 10, 30, 45)
            mock_datetime.now.return_value = mock_now

            result = Task.get_current_time()

            assert result == "2024-04-16 10:30:45"

    def test_get_current_time_calls_datetime_now(self):
        """Test that get_current_time calls datetime.now()"""
        with patch("task.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2024-01-01 00:00:00"

            Task.get_current_time()

            mock_datetime.now.assert_called_once()

    # Tests for _update_state method
    def test_update_state_changes_state(self, task):
        """Test that _update_state changes the task state"""
        task._update_state(Task.State.DONE)

        assert task.state == Task.State.DONE

    def test_update_state_sets_updated_at(self, task, mock_time):
        """Test that _update_state sets the updated_at timestamp"""
        new_time = "2024-04-16 11:00:00"

        with patch("task.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = new_time
            task._update_state(Task.State.IN_PROGRESS)

            assert task.updated_at == new_time

    # Tests for done method
    def test_done_sets_state_to_done(self, task):
        """Test that done() sets state to DONE"""
        task.done()

        assert task.state == Task.State.DONE

    def test_done_updates_timestamp(self, task):
        """Test that done() updates the updated_at timestamp"""
        assert task.updated_at is None

        task.done()

        assert task.updated_at is not None

    def test_done_from_different_states(self):
        """Test that done() works from any state"""
        task = Task("Test task")

        # From PENDING
        task.done()
        assert task.state == Task.State.DONE

        # From IN_PROGRESS
        task.in_progress()
        task.done()
        assert task.state == Task.State.DONE

        # From DONE (idempotent)
        task.done()
        assert task.state == Task.State.DONE

    # Tests for pending method
    def test_pending_sets_state_to_pending(self, task):
        """Test that pending() sets state to PENDING"""
        task.state = Task.State.DONE  # Change from initial state
        task.pending()

        assert task.state == Task.State.PENDING

    def test_pending_no_timestamp_update(self, task):
        """Test that pending() should not update the updated_at timestamp"""
        # If the task is already pending, calling pending() should not update the timestamp
        task.pending()

        assert task.updated_at is None

    # Tests for in_progress method
    def test_in_progress_sets_state_to_in_progress(self, task):
        """Test that in_progress() sets state to IN_PROGRESS"""
        task.in_progress()

        assert task.state == Task.State.IN_PROGRESS

    def test_in_progress_updates_timestamp(self, task):
        """Test that in_progress() updates the updated_at timestamp"""
        task.in_progress()

        assert task.updated_at is not None

    # Tests for update_description method
    def test_update_description_changes_description(self, task):
        """Test that update_description changes the task description"""
        new_description = "Updated task description"

        task.update_description(new_description)

        assert task.description == new_description

    def test_update_description_sets_updated_at(self, task):
        """Test that update_description sets the updated_at timestamp"""
        assert task.updated_at is None

        task.update_description("New description")

        assert task.updated_at is not None

    def test_update_description_preserves_state(self, task):
        """Test that update_description doesn't change the state"""
        task.in_progress()
        initial_state = task.state

        task.update_description("Modified description")

        assert task.state == initial_state

    # Tests for State enum
    def test_state_enum_members_are_strings(self):
        """Test that State enum members are strings (StrEnum behavior)"""
        assert isinstance(Task.State.DONE, str)
        assert isinstance(Task.State.PENDING, str)
        assert isinstance(Task.State.IN_PROGRESS, str)

    def test_state_enum_values(self):
        """Test that State enum has correct string values"""
        assert Task.State.DONE == "done"
        assert Task.State.PENDING == "pending"
        assert Task.State.IN_PROGRESS == "in_progress"

    # Integration tests
    def test_task_lifecycle(self):
        """Test a complete task lifecycle"""
        with patch("task.datetime") as mock_datetime:
            times = [
                "2024-04-16 10:00:00",
                "2024-04-16 11:00:00",
                "2024-04-16 12:00:00",
                "2024-04-16 13:00:00",
            ]
            mock_datetime.now.return_value.strftime.side_effect = times

            # Create task
            task = Task("Complete project")
            assert task.state == Task.State.PENDING
            assert task.updated_at is None

            # Start working on it
            task.in_progress()
            assert task.state == Task.State.IN_PROGRESS
            assert task.updated_at is not None
            first_update = task.updated_at

            # Update description while in progress
            task.update_description("Complete project - Phase 1")
            assert task.description == "Complete project - Phase 1"
            assert task.updated_at != first_update  # Timestamp changed

            # Complete the task
            task.done()
            assert task.state == Task.State.DONE

    def test_multiple_tasks_have_unique_ids_and_independent_states(self):
        """Test that multiple tasks maintain independence"""
        task1 = Task("Task 1")
        task2 = Task("Task 2")
        task3 = Task("Task 3")

        # Different IDs
        assert task1.id != task2.id != task3.id

        # Independent state changes
        task1.in_progress()
        task2.done()

        assert task1.state == Task.State.IN_PROGRESS
        assert task2.state == Task.State.DONE
        assert task3.state == Task.State.PENDING

    def test_timestamp_updates_on_state_transitions(self):
        """Test that each state transition updates the timestamp"""
        with patch("task.datetime") as mock_datetime:
            times = [
                "2024-04-16 10:00:00",
                "2024-04-16 11:00:00",
                "2024-04-16 12:00:00",
                "2024-04-16 13:00:00",
            ]
            mock_datetime.now.return_value.strftime.side_effect = times

            task = Task("Time test")
            created_time = task.created_at

            task.in_progress()
            first_transition = task.updated_at

            task.done()
            second_transition = task.updated_at

            task.pending()
            third_transition = task.updated_at

            # All transitions should have different timestamps
            assert created_time != first_transition
            assert first_transition != second_transition
            assert second_transition != third_transition
