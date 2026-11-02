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

    demo_sorting_and_filtering()
    demo_recurring_tasks()
    demo_conflict_detection()


def demo_conflict_detection():
    """Show conflict warnings for pending tasks sharing the exact same date and time."""
    today = datetime.date.today()
    owner = Owner(owner_id=4, name="Conflict Demo", email="conflict@example.com")
    buddy = Pet(pet_id=1, name="Buddy", species="Dog", age=4, owner_id=owner.owner_id)
    whiskers = Pet(pet_id=2, name="Whiskers", species="Cat", age=2, owner_id=owner.owner_id)
    owner.add_pet(buddy)
    owner.add_pet(whiskers)

    # 08:00 and 11:00: two pending tasks on different pets -> conflicts
    buddy.add_task(Task(1, "Morning walk", "walk", today, datetime.time(8, 0), "high"))
    whiskers.add_task(Task(2, "Give medication", "medication", today, datetime.time(8, 0), "high"))
    buddy.add_task(Task(3, "Vet visit", "vet", today, datetime.time(11, 0), "high"))
    whiskers.add_task(Task(4, "Nail trim", "grooming", today, datetime.time(11, 0), "low"))
    # 14:00: one pending, one completed -> NOT a conflict
    buddy.add_task(Task(5, "Grooming", "grooming", today, datetime.time(14, 0), "medium"))
    done = Task(6, "Play session", "play", today, datetime.time(14, 0), "low")
    whiskers.add_task(done)
    done.mark_complete()

    scheduler = Scheduler(owner)

    print("\n" + "=" * 62)
    print("  Conflict Detection Demo")
    print("=" * 62)
    warnings = scheduler.get_conflict_warnings()
    print(f"\nWarnings found: {len(warnings)}")
    for message in warnings:
        print(f"  WARNING: {message}")
    print("\n14:00 is not listed: 'Play session' is completed, so it is excluded.")

    # Once the clashing tasks are done, the warnings disappear
    for task in buddy.get_tasks()[:2]:
        task.mark_complete()
    print(f"After completing Buddy's 08:00 and 11:00 tasks: "
          f"{len(scheduler.get_conflict_warnings())} warning(s)")


def demo_recurring_tasks():
    """Show that completing a daily/weekly task creates its next occurrence."""
    today = datetime.date.today()
    owner = Owner(owner_id=3, name="Recurring Demo", email="recurring@example.com")
    rex = Pet(pet_id=1, name="Rex", species="Dog", age=3, owner_id=owner.owner_id)
    owner.add_pet(rex)

    daily = Task(1, "Give vitamins", "medication", today, datetime.time(8, 0),
                 "high", frequency="daily")
    weekly = Task(2, "Bath time", "grooming", today, datetime.time(17, 0),
                  "medium", frequency="weekly")
    rex.add_task(daily)
    rex.add_task(weekly)

    scheduler = Scheduler(owner)

    print("\n" + "=" * 62)
    print("  Recurring Tasks Demo")
    print("=" * 62)

    new_daily = scheduler.mark_task_complete(daily)
    new_weekly = scheduler.mark_task_complete(weekly)

    print("\nCompleted tasks:")
    for task in (daily, weekly):
        print(f"  {task.title:<14}{task.frequency:<8}{task.date}  Done: {task.completed}")

    print("\nNewly generated occurrences:")
    for task in (new_daily, new_weekly):
        print(f"  {task.title:<14}{task.frequency:<8}{task.date}  Done: {task.completed}")

    # Duplicate prevention: doing it again creates nothing new
    again = scheduler.mark_task_complete(daily)
    regenerated = scheduler.generate_recurring_tasks()
    print(f"\nCompleting 'Give vitamins' again created: {again}")
    print(f"generate_recurring_tasks() created {len(regenerated)} new task(s)")
    print(f"Rex now has {len(rex.get_tasks())} tasks in total")


def print_tasks(heading, owner, tasks):
    """Print a short list of tasks with time, pet, title and status."""
    print(f"\n{heading}")
    if not tasks:
        print("  (none)")
    for task in tasks:
        status = "Done" if task.completed else "Pending"
        print(f"  {task.time.strftime('%H:%M')}  {find_pet_name(owner, task):<9}"
              f"{task.title:<18}{status}")


def demo_sorting_and_filtering():
    """Show sort_by_time and filter_tasks using tasks added out of order."""
    today = datetime.date.today()
    owner = Owner(owner_id=2, name="Demo Owner", email="demo@example.com")
    rex = Pet(pet_id=1, name="Rex", species="Dog", age=3, owner_id=owner.owner_id)
    luna = Pet(pet_id=2, name="Luna", species="Cat", age=5, owner_id=owner.owner_id)
    owner.add_pet(rex)
    owner.add_pet(luna)

    # Deliberately NOT in chronological order
    rex.add_task(Task(1, "Evening walk", "walk", today, datetime.time(18, 0), "medium"))
    luna.add_task(Task(2, "Breakfast", "feeding", today, datetime.time(7, 30), "high"))
    rex.add_task(Task(3, "Vet checkup", "vet", today, datetime.time(12, 0), "high"))
    luna.add_task(Task(4, "Brush fur", "grooming", today, datetime.time(9, 15), "low"))
    luna.get_tasks()[0].mark_complete()  # Breakfast is done

    scheduler = Scheduler(owner)

    print("\n" + "=" * 62)
    print("  Sorting & Filtering Demo")
    print("=" * 62)
    print_tasks("Original order (as added):", owner, owner.get_all_tasks())
    print_tasks("Sorted by time:", owner, scheduler.sort_by_time())
    print_tasks("Only Rex's tasks:", owner, scheduler.filter_tasks(pet_name="Rex"))
    print_tasks("Only completed tasks:", owner, scheduler.filter_tasks(completed=True))
    print_tasks("Only pending tasks:", owner, scheduler.filter_tasks(completed=False))
    print_tasks("Luna's pending tasks:", owner,
                scheduler.filter_tasks(pet_name="Luna", completed=False))


if __name__ == "__main__":
    main()
