import datetime
from dataclasses import dataclass, field, replace

VALID_PRIORITIES = ("low", "medium", "high")
VALID_FREQUENCIES = ("once", "daily", "weekly")


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
    description: str = ""
    frequency: str = "once"  # "once", "daily", or "weekly"

    def __post_init__(self):
        """Validate the task's fields and keep recurring and frequency consistent."""
        if not self.title.strip():
            raise ValueError("Task title cannot be empty.")
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(f"Priority must be one of {VALID_PRIORITIES}.")
        if self.frequency not in VALID_FREQUENCIES:
            raise ValueError(f"Frequency must be one of {VALID_FREQUENCIES}.")
        # Keep 'recurring' and 'frequency' consistent with each other.
        if self.frequency != "once":
            self.recurring = True
        elif self.recurring:
            self.frequency = "daily"

    def mark_complete(self):
        """Mark this task as done."""
        self.completed = True

    def mark_completed(self):
        """Alias matching the Phase 1 UML name."""
        self.mark_complete()


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

    def __post_init__(self):
        """Validate the pet's name and age."""
        if not self.name.strip():
            raise ValueError("Pet name cannot be empty.")
        if self.age < 0:
            raise ValueError("Pet age cannot be negative.")

    def add_task(self, task: Task):
        """Add a task to this pet (task ids must be unique per pet)."""
        if any(t.task_id == task.task_id for t in self.tasks):
            raise ValueError(f"Task id {task.task_id} already exists for {self.name}.")
        self.tasks.append(task)

    def remove_task(self, task_id: int):
        """Remove the task with the given id from this pet."""
        for task in self.tasks:
            if task.task_id == task_id:
                self.tasks.remove(task)
                return
        raise ValueError(f"No task with id {task_id} for {self.name}.")

    def get_tasks(self):
        """Return a copy of this pet's task list."""
        return list(self.tasks)


# =============================================================================
# Owner
# A person who owns one or more Pets.
# =============================================================================
class Owner:
    def __init__(self, owner_id: int, name: str, email: str):
        """Create an owner with validated name and email and no pets."""
        if not name.strip():
            raise ValueError("Owner name cannot be empty.")
        if "@" not in email:
            raise ValueError("Owner email must contain '@'.")
        self.owner_id = owner_id
        self.name = name
        self.email = email
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet):
        """Add a pet to this owner (pet ids must be unique)."""
        if pet.owner_id != self.owner_id:
            raise ValueError("Pet's owner_id does not match this owner.")
        if any(p.pet_id == pet.pet_id for p in self.pets):
            raise ValueError(f"Pet id {pet.pet_id} already exists.")
        self.pets.append(pet)

    def remove_pet(self, pet_id: int):
        """Remove the pet with the given id from this owner."""
        for pet in self.pets:
            if pet.pet_id == pet_id:
                self.pets.remove(pet)
                return
        raise ValueError(f"No pet with id {pet_id}.")

    def get_pets(self):
        """Return a copy of this owner's pet list."""
        return list(self.pets)

    def get_all_tasks(self):
        """Return every task from every pet this owner has."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks


# =============================================================================
# Scheduler
# Organizes Tasks: sorting, conflict detection, daily views, recurrence.
# =============================================================================
class Scheduler:
    def __init__(self, owner: Owner = None):
        """Create a scheduler for the given owner with no standalone tasks."""
        self.owner = owner
        # Extra tasks added directly to the scheduler (not tied to a pet).
        self.tasks: list[Task] = []

    def add_task(self, task: Task):
        """Add a standalone task directly to the scheduler."""
        self.tasks.append(task)

    def get_all_tasks(self):
        """Gather tasks from all of the owner's pets, plus standalone ones."""
        all_tasks = self.owner.get_all_tasks() if self.owner else []
        for task in self.tasks:
            if not any(task is t for t in all_tasks):
                all_tasks.append(task)
        return all_tasks

    def sort_tasks(self):
        """Return all tasks in chronological order (high priority first on ties)."""
        priority_rank = {"high": 0, "medium": 1, "low": 2}
        return sorted(
            self.get_all_tasks(),
            key=lambda t: (t.date, t.time, priority_rank[t.priority]),
        )

    def get_daily_tasks(self, date: datetime.date):
        """Return the tasks scheduled for the given date, in time order."""
        return [t for t in self.sort_tasks() if t.date == date]

    def detect_conflicts(self):
        """Return pairs of incomplete tasks scheduled at the same date and time."""
        pending = [t for t in self.sort_tasks() if not t.completed]
        conflicts = []
        for i in range(len(pending)):
            for j in range(i + 1, len(pending)):
                a, b = pending[i], pending[j]
                if a.date == b.date and a.time == b.time:
                    conflicts.append((a, b))
        return conflicts

    def generate_recurring_tasks(self):
        """Create and return the next occurrence of each completed recurring task."""
        all_tasks = self.get_all_tasks()
        next_id = max((t.task_id for t in all_tasks), default=0) + 1
        new_tasks = []

        for task in all_tasks:
            if not (task.recurring and task.completed):
                continue
            days = 1 if task.frequency == "daily" else 7
            next_date = task.date + datetime.timedelta(days=days)

            already_exists = any(
                t.title == task.title
                and t.task_type == task.task_type
                and t.date == next_date
                and t.time == task.time
                for t in all_tasks + new_tasks
            )
            if already_exists:
                continue

            new_task = replace(task, task_id=next_id, date=next_date, completed=False)
            next_id += 1
            self._store_next_to(task, new_task)
            new_tasks.append(new_task)

        return new_tasks

    def _store_next_to(self, original: Task, new_task: Task):
        """Put new_task in the same place (pet or scheduler) as original."""
        if self.owner:
            for pet in self.owner.pets:
                if any(original is t for t in pet.tasks):
                    pet.add_task(new_task)
                    return
        self.tasks.append(new_task)
