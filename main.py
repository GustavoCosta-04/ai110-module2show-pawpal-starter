import datetime

from pawpal_system import Owner, Pet, Task, Scheduler


def find_pet_name(owner, task):
    """Look up which of the owner's pets a task belongs to."""
    for pet in owner.get_pets():
        if any(task is t for t in pet.get_tasks()):
            return pet.name
    return "Unknown"


def print_schedule(owner, scheduler, day):
    """Print the schedule for one day in a readable table."""
    print("=" * 62)
    print(f"  Today's Schedule - {day.strftime('%A, %B %d, %Y')}")
    print(f"  Owner: {owner.name}")
    print("=" * 62)
    print(f"{'Time':<9}{'Pet':<10}{'Task':<28}{'Status'}")
    print("-" * 62)

    tasks = scheduler.get_daily_tasks(day)
    if not tasks:
        print("  No tasks scheduled today.")
    for task in tasks:
        time_text = task.time.strftime("%I:%M %p")
        status = "[x] Done" if task.completed else "[ ] Pending"
        print(f"{time_text:<9}{find_pet_name(owner, task):<10}{task.title:<28}{status}")

    print("=" * 62)


def main():
    today = datetime.date.today()

    # One owner with two pets
    owner = Owner(owner_id=1, name="Gustavo", email="gustavo@example.com")
    buddy = Pet(pet_id=1, name="Buddy", species="Dog", age=4, owner_id=owner.owner_id)
    whiskers = Pet(pet_id=2, name="Whiskers", species="Cat", age=2, owner_id=owner.owner_id)
    owner.add_pet(buddy)
    owner.add_pet(whiskers)

    # Tasks at different times, split between the pets
    buddy.add_task(Task(
        task_id=1, title="Morning walk", task_type="walk",
        date=today, time=datetime.time(7, 30), priority="high",
    ))
    buddy.add_task(Task(
        task_id=2, title="Evening feeding", task_type="feeding",
        date=today, time=datetime.time(18, 0), priority="medium",
        frequency="daily",
    ))
    whiskers.add_task(Task(
        task_id=3, title="Give medication", task_type="medication",
        date=today, time=datetime.time(9, 0), priority="high",
    ))
    whiskers.add_task(Task(
        task_id=4, title="Play session", task_type="play",
        date=today, time=datetime.time(15, 30), priority="low",
    ))

    # Mark one task as done to show the status column
    whiskers.get_tasks()[0].mark_complete()

    scheduler = Scheduler(owner)
    print_schedule(owner, scheduler, today)

    conflicts = scheduler.detect_conflicts()
    print(f"\nScheduling conflicts found: {len(conflicts)}")


if __name__ == "__main__":
    main()
