import datetime

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task

DAY = datetime.date(2026, 1, 1)


# -----------------------------------------------------------------------------
# Helpers and fixtures
# -----------------------------------------------------------------------------
def make_task(task_id=1, title="Morning walk", hour=8, minute=0, date=DAY,
              priority="high", **extra):
    """Helper that builds a simple Task; extra keyword args (frequency, completed...) pass through."""
    return Task(
        task_id=task_id,
        title=title,
        task_type="walk",
        date=date,
        time=datetime.time(hour, minute),
        priority=priority,
        **extra,
    )


def ids(tasks):
    """Return just the task ids, which makes comparing task lists easy to read."""
    return [t.task_id for t in tasks]


@pytest.fixture
def owner():
    return Owner(owner_id=1, name="Gustavo", email="gustavo@example.com")


@pytest.fixture
def rex(owner):
    pet = Pet(pet_id=1, name="Rex", species="Dog", age=3, owner_id=owner.owner_id)
    owner.add_pet(pet)
    return pet


@pytest.fixture
def luna(owner):
    pet = Pet(pet_id=2, name="Luna", species="Cat", age=5, owner_id=owner.owner_id)
    owner.add_pet(pet)
    return pet


@pytest.fixture
def scheduler(owner, rex, luna):
    """A scheduler for an owner who has two pets (Rex and Luna) with no tasks yet."""
    return Scheduler(owner)


@pytest.fixture
def populated(rex, luna, scheduler):
    """Scheduler where Rex and Luna each have one pending and one completed task."""
    rex.add_task(make_task(1, "Rex walk", hour=8))
    rex.add_task(make_task(2, "Rex vet", hour=12, completed=True))
    luna.add_task(make_task(3, "Luna meds", hour=9))
    luna.add_task(make_task(4, "Luna play", hour=10, completed=True))
    return scheduler


# -----------------------------------------------------------------------------
# Existing tests (Task and Pet basics)
# -----------------------------------------------------------------------------
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


# -----------------------------------------------------------------------------
# 1. Sorting
# -----------------------------------------------------------------------------
def test_sort_by_time_returns_chronological_order(rex, luna, scheduler):
    # Added deliberately out of order, spread across two pets
    rex.add_task(make_task(1, "Evening walk", hour=18))
    luna.add_task(make_task(2, "Breakfast", hour=7, minute=30))
    rex.add_task(make_task(3, "Vet visit", hour=12))

    sorted_tasks = scheduler.sort_by_time()

    assert [t.title for t in sorted_tasks] == ["Breakfast", "Vet visit", "Evening walk"]


def test_sort_by_time_does_not_change_original_list(rex, scheduler):
    rex.add_task(make_task(1, "Evening walk", hour=18))
    rex.add_task(make_task(2, "Breakfast", hour=7))

    scheduler.sort_by_time()

    assert ids(rex.get_tasks()) == [1, 2]  # still in the order they were added


def test_sort_by_time_orders_by_date_before_time(rex, scheduler):
    next_day = DAY + datetime.timedelta(days=1)
    rex.add_task(make_task(1, "Tomorrow early", hour=6, date=next_day))
    rex.add_task(make_task(2, "Today late", hour=20, date=DAY))

    assert ids(scheduler.sort_by_time()) == [2, 1]


def test_sort_by_time_uses_priority_to_break_ties(rex, scheduler):
    rex.add_task(make_task(1, "Low priority", hour=8, priority="low"))
    rex.add_task(make_task(2, "High priority", hour=8, priority="high"))
    rex.add_task(make_task(3, "Medium priority", hour=8, priority="medium"))

    assert ids(scheduler.sort_by_time()) == [2, 3, 1]


# -----------------------------------------------------------------------------
# 2. Filtering
# -----------------------------------------------------------------------------
def test_filter_by_pet_name(populated):
    assert ids(populated.filter_tasks(pet_name="Rex")) == [1, 2]


def test_filter_by_pet_name_ignores_case(populated):
    assert ids(populated.filter_tasks(pet_name="rEx")) == [1, 2]


def test_filter_completed_true_returns_only_finished_tasks(populated):
    # Sorted by time: Luna play (10:00) then Rex vet (12:00)
    assert ids(populated.filter_tasks(completed=True)) == [4, 2]


def test_filter_completed_false_returns_only_pending_tasks(populated):
    # False must filter (not be treated like "no filter")
    assert ids(populated.filter_tasks(completed=False)) == [1, 3]


def test_filter_by_pet_name_and_completed_together(populated):
    assert ids(populated.filter_tasks(pet_name="Luna", completed=False)) == [3]
    assert ids(populated.filter_tasks(pet_name="Rex", completed=True)) == [2]


def test_filter_unknown_pet_name_returns_empty_list(populated):
    assert populated.filter_tasks(pet_name="Goldie") == []


def test_filter_with_no_arguments_returns_all_tasks_in_time_order(populated):
    assert ids(populated.filter_tasks()) == [1, 3, 4, 2]


# -----------------------------------------------------------------------------
# 3. Recurring tasks
# -----------------------------------------------------------------------------
def test_completing_daily_task_creates_next_day_task_for_same_pet(rex, luna, scheduler):
    task = make_task(1, "Give vitamins", hour=9, priority="medium", frequency="daily")
    rex.add_task(task)

    new_task = scheduler.mark_task_complete(task)

    assert task.completed is True
    assert new_task is not None
    assert new_task.completed is False
    assert new_task.date == DAY + datetime.timedelta(days=1)
    # Important attributes are preserved
    assert new_task.title == task.title
    assert new_task.time == task.time
    assert new_task.priority == task.priority
    assert new_task.frequency == "daily"
    # It was added to the same pet (and not to the other one)
    assert any(new_task is t for t in rex.get_tasks())
    assert len(rex.get_tasks()) == 2
    assert luna.get_tasks() == []


def test_completing_weekly_task_creates_task_seven_days_later(rex, scheduler):
    task = make_task(1, "Bath time", frequency="weekly")
    rex.add_task(task)

    new_task = scheduler.mark_task_complete(task)

    assert new_task.date == DAY + datetime.timedelta(days=7)
    assert new_task.completed is False


def test_completing_same_recurring_task_twice_does_not_create_duplicate(rex, scheduler):
    task = make_task(1, "Give vitamins", frequency="daily")
    rex.add_task(task)

    scheduler.mark_task_complete(task)
    second_result = scheduler.mark_task_complete(task)

    assert second_result is None
    assert len(rex.get_tasks()) == 2


def test_generate_recurring_tasks_does_not_duplicate_existing_next_task(rex, scheduler):
    task = make_task(1, "Give vitamins", frequency="daily")
    rex.add_task(task)
    scheduler.mark_task_complete(task)

    assert scheduler.generate_recurring_tasks() == []
    assert len(rex.get_tasks()) == 2


def test_completing_non_recurring_task_does_not_create_new_task(rex, scheduler):
    task = make_task(1, "One-time vet visit")  # frequency defaults to "once"
    rex.add_task(task)

    result = scheduler.mark_task_complete(task)

    assert task.completed is True
    assert result is None
    assert len(rex.get_tasks()) == 1


# -----------------------------------------------------------------------------
# 4. Conflict detection
# -----------------------------------------------------------------------------
def test_two_pending_tasks_at_same_date_and_time_form_one_conflict(rex, luna, scheduler):
    rex.add_task(make_task(1, "Morning walk", hour=8))
    luna.add_task(make_task(2, "Give medication", hour=8))

    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    assert ids(conflicts[0]) == [1, 2]


def test_conflict_warning_includes_date_time_titles_and_pet_names(rex, luna, scheduler):
    rex.add_task(make_task(1, "Morning walk", hour=8))
    luna.add_task(make_task(2, "Give medication", hour=8))

    warnings = scheduler.get_conflict_warnings()

    assert len(warnings) == 1
    message = warnings[0]
    assert "08:00" in message
    assert "2026-01-01" in message
    assert "Morning walk (Rex)" in message
    assert "Give medication (Luna)" in message


def test_each_conflicting_time_slot_gets_its_own_warning(rex, luna, scheduler):
    rex.add_task(make_task(1, "Walk", hour=8))
    luna.add_task(make_task(2, "Meds", hour=8))
    rex.add_task(make_task(3, "Vet", hour=11))
    luna.add_task(make_task(4, "Grooming", hour=11))

    warnings = scheduler.get_conflict_warnings()

    assert len(warnings) == 2
    assert "08:00" in warnings[0]
    assert "11:00" in warnings[1]


def test_completed_tasks_are_excluded_from_conflicts(rex, luna, scheduler):
    rex.add_task(make_task(1, "Morning walk", hour=8))
    luna.add_task(make_task(2, "Give medication", hour=8, completed=True))

    assert scheduler.detect_conflicts() == []
    assert scheduler.get_conflict_warnings() == []


def test_same_date_but_different_time_is_not_a_conflict(rex, luna, scheduler):
    rex.add_task(make_task(1, "Walk", hour=8))
    luna.add_task(make_task(2, "Meds", hour=9))

    assert scheduler.detect_conflicts() == []


def test_same_time_but_different_date_is_not_a_conflict(rex, luna, scheduler):
    rex.add_task(make_task(1, "Walk", hour=8, date=DAY))
    luna.add_task(make_task(2, "Meds", hour=8, date=DAY + datetime.timedelta(days=1)))

    assert scheduler.detect_conflicts() == []


def test_no_conflicts_returns_empty_lists(populated):
    # 'populated' has all-different times, so nothing clashes
    assert populated.detect_conflicts() == []
    assert populated.get_conflict_warnings() == []


# -----------------------------------------------------------------------------
# 5. Empty task lists
# -----------------------------------------------------------------------------
def assert_scheduler_returns_empty_lists(scheduler):
    """Every Scheduler query should give [] (and not crash) when there are no tasks."""
    assert scheduler.sort_by_time() == []
    assert scheduler.filter_tasks() == []
    assert scheduler.filter_tasks(pet_name="Rex", completed=False) == []
    assert scheduler.detect_conflicts() == []
    assert scheduler.get_conflict_warnings() == []
    assert scheduler.generate_recurring_tasks() == []


def test_pet_with_no_tasks_returns_empty_lists(rex, scheduler):
    assert rex.get_tasks() == []
    assert_scheduler_returns_empty_lists(scheduler)


def test_owner_with_no_pets_returns_empty_lists(owner):
    assert owner.get_pets() == []
    assert owner.get_all_tasks() == []
    assert_scheduler_returns_empty_lists(Scheduler(owner))


def test_scheduler_without_owner_returns_empty_lists():
    assert_scheduler_returns_empty_lists(Scheduler())
