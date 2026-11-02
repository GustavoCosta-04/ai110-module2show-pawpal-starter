import datetime

from pawpal_system import Pet, Task


def make_task(task_id=1):
    """Helper that builds a simple Task for the tests."""
    return Task(
        task_id=task_id,
        title="Morning walk",
        task_type="walk",
        date=datetime.date(2026, 1, 1),
        time=datetime.time(8, 0),
        priority="high",
    )


def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(pet_id=1, name="Buddy", species="Dog", age=4, owner_id=1)
    initial_count = len(pet.get_tasks())

    pet.add_task(make_task())

    assert len(pet.get_tasks()) == initial_count + 1
