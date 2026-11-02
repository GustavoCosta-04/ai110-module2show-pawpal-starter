import datetime
from dataclasses import dataclass, field


# =============================================================================
# Task
# A single care activity (feeding, walk, vet visit, ...) for one pet.
# =============================================================================
@dataclass
class Task:
    task_id: int
    title: str
    task_type: str
    date: datetime.date
    time: datetime.time
    priority: str
    completed: bool = False
    recurring: bool = False

    def mark_completed(self):
        """Mark this task as done."""
        pass


# =============================================================================
# Pet
# A pet that belongs to an Owner and has its own list of Tasks.
# =============================================================================
@dataclass
class Pet:
    pet_id: int
    name: str
    species: str
    age: int
    owner_id: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a task to this pet."""
        pass

    def remove_task(self, task_id: int):
        """Remove the task with the given id from this pet."""
        pass

    def get_tasks(self):
        """Return all tasks for this pet."""
        pass


# =============================================================================
# Owner
# A person who owns one or more Pets.
# =============================================================================
class Owner:
    def __init__(self, owner_id: int, name: str, email: str):
        self.owner_id = owner_id
        self.name = name
        self.email = email
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet):
        """Add a pet to this owner."""
        pass

    def remove_pet(self, pet_id: int):
        """Remove the pet with the given id from this owner."""
        pass

    def get_pets(self):
        """Return all pets belonging to this owner."""
        pass


# =============================================================================
# Scheduler
# Organizes Tasks: sorting, conflict detection, daily views, recurrence.
# =============================================================================
class Scheduler:
    def __init__(self):
        self.tasks: list[Task] = []

    def add_task(self, task: Task):
        """Add a task to the scheduler."""
        pass

    def sort_tasks(self):
        """Sort tasks (e.g., by date, time, and priority)."""
        pass

    def detect_conflicts(self):
        """Find tasks scheduled at the same date and time."""
        pass

    def get_daily_tasks(self, date: datetime.date):
        """Return the tasks scheduled for the given date."""
        pass

    def generate_recurring_tasks(self):
        """Create upcoming copies of tasks marked as recurring."""
        pass
