# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

==============================================================
  Today's Schedule - Monday, November 02, 2026
  Owner: Gustavo
==============================================================
Time     Pet       Task                        Status
--------------------------------------------------------------
07:30 AM Buddy     Morning walk                [ ] Pending
09:00 AM Whiskers  Give medication             [x] Done
03:30 PM Whiskers  Play session                [ ] Pending
06:00 PM Buddy     Evening feeding             [ ] Pending
==============================================================

Scheduling conflicts found: 0

## 🧪 Testing PawPal+

Run the automated test suite from the project folder:

```bash
python -m pytest
```

`python -m pytest` is used (instead of plain `pytest`) so Python can find `pawpal_system.py`
from the `tests/` folder.

### What the tests cover

The tests live in `tests/test_pawpal.py`:

- **Task completion:** `mark_complete()` changes a task from pending to completed.
- **Adding tasks to pets:** `Pet.add_task()` increases the pet's task count.
- **Chronological sorting:** `Scheduler.sort_by_time()` orders tasks added out of order, sorts by
  date before time, uses priority to break ties, and does not modify the original lists.
- **Filtering by pet and completion status:** `Scheduler.filter_tasks()` by pet name (case-insensitive),
  `completed=True`, `completed=False`, both together, an unknown pet, and no filters.
- **Daily and weekly recurring tasks:** `Scheduler.mark_task_complete()` creates a pending task
  one day (daily) or seven days (weekly) later on the same pet, keeping the title, time and priority.
  A non-recurring task creates nothing new.
- **Duplicate recurrence prevention:** completing the same task twice, or calling
  `generate_recurring_tasks()` afterwards, does not create a second copy.
- **Scheduling conflict detection:** two pending tasks at the same date and time form one conflict;
  warnings include the date, time, titles and pet names; completed tasks and different dates or
  times are not conflicts.
- **Empty task lists:** a pet with no tasks, an owner with no pets, and a `Scheduler` with no owner
  all return empty lists without errors.

### Test output

```
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.7.0
rootdir: D:\FAU\CEN5035\PawPawl\ai110-module2show-pawpal-starter
plugins: anyio-4.12.1
collected 28 items

tests\test_pawpal.py ............................                        [100%]

============================= 28 passed in 0.05s ==============================
```

### Confidence Level

⭐⭐⭐⭐☆ (4 out of 5)

All 28 tests pass, and they cover every `Scheduler` feature (sorting, filtering, recurrence,
duplicate prevention, conflict detection) with both normal cases and edge cases such as empty
lists, completed tasks and unknown pet names. One star is held back because some behavior is not
tested yet: the Streamlit interface in `app.py`, input validation errors (for example an empty
title or invalid priority), removing pets or tasks, standalone tasks added directly to the
scheduler, and duration-based overlaps (conflict detection only checks exact date and time).

## 📐 Smarter Scheduling

The `Scheduler` class in `pawpal_system.py` adds four algorithmic features on top of the
basic task lists. It works through the `Owner`, so it always sees every pet's current tasks.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | By date, then time, then priority (high first) |
| Filtering | `Scheduler.filter_tasks()` | By pet name and/or completion status |
| Conflict handling | `Scheduler.detect_conflicts()`, `Scheduler.get_conflict_warnings()` | Exact same date and time |
| Recurring tasks | `Scheduler.mark_task_complete()`, `Scheduler._create_next_occurrence()` | Daily (+1 day) or weekly (+7 days) |

### 1. Sorting

**Method:** `Scheduler.sort_by_time(tasks=None)`

Returns a **new** list of tasks in chronological order, earliest first. It uses Python's
`sorted()` with a lambda key of `(date, time, priority)`: the date comes first so multi-day
schedules stay in order, the time orders tasks within a day, and priority breaks ties
(`high` before `medium` before `low`). The original task lists are never changed. If you
pass a list of tasks it sorts that list, otherwise it sorts every task the scheduler can see.
`Scheduler.sort_tasks()` is kept as a shortcut that calls `sort_by_time()`.

```python
scheduler = Scheduler(owner)
for task in scheduler.sort_by_time():
    print(task.time, task.title)
```

### 2. Filtering

**Method:** `Scheduler.filter_tasks(pet_name=None, completed=None)`

Starts from the sorted task list, so results always come back in chronological order, then
narrows it down:

- `pet_name`: keeps only tasks that belong to a pet with that name (case-insensitive).
  Standalone tasks added directly to the scheduler belong to no pet, so they are excluded
  whenever a pet name is given.
- `completed`: `True` keeps finished tasks, `False` keeps pending ones, `None` ignores status.
- Both filters can be combined, and with neither the method returns every task.

```python
scheduler.filter_tasks(pet_name="Rex")                      # all of Rex's tasks
scheduler.filter_tasks(completed=False)                     # everything still pending
scheduler.filter_tasks(pet_name="Luna", completed=False)    # Luna's pending tasks
```

### 3. Recurring tasks

**Methods:** `Scheduler.mark_task_complete(task)` and the private helper
`Scheduler._create_next_occurrence(task)`. `Scheduler.generate_recurring_tasks()` uses the
same helper.

A task is recurring when its `frequency` is `"daily"` or `"weekly"` (see `Task`).
`mark_task_complete()` calls the task's `mark_complete()` and then asks
`_create_next_occurrence()` for the next one:

1. If the task is not recurring, nothing is created.
2. The next date is the task's date plus a `datetime.timedelta`: 1 day for daily, 7 days for weekly.
3. The new task is a copy made with `dataclasses.replace()`. It keeps the title, time,
   priority, type, frequency and description, gets a new unique `task_id`, and has
   `completed=False`.
4. It is added to the **same pet** that owned the original task.

`mark_task_complete()` returns the new task, or `None` if none was created.
`generate_recurring_tasks()` does the same for every task that is already completed and
recurring, and returns the list of new tasks.

**Duplicate prevention:** before creating a task, `_create_next_occurrence()` checks whether
a task with the same title, type, date and time already exists. If it does, nothing is
created, so completing the same task twice (or calling `generate_recurring_tasks()`
afterwards) never produces duplicates.

```python
walk = Task(1, "Give vitamins", "medication", today, time(8, 0), "high", frequency="daily")
pet.add_task(walk)
next_walk = scheduler.mark_task_complete(walk)   # next_walk.date == today + 1 day
```

In the Streamlit app, use the **Mark a task complete** dropdown and **Mark complete** button
to trigger this.

### 4. Conflict detection

**Methods:** `Scheduler.detect_conflicts()` and `Scheduler.get_conflict_warnings()`

`detect_conflicts()` makes one pass over the tasks and groups the **pending** ones
(`completed=False`) in a dictionary keyed by `(date, time)`. Any key holding two or more
tasks is a conflict. It returns a list of conflicting groups (each group is a list of
tasks), earliest first, and returns an empty list when there are none. It never raises an
exception. Because each task is visited once and dictionary lookups are constant time, the
grouping is O(n).

`get_conflict_warnings()` turns each group into a readable message, including the pet name
when the task belongs to a pet, and returns an empty list when there are no conflicts:

```
Conflict at 08:00 on 2026-11-02: Morning walk (Buddy), Give medication (Whiskers)
```

Completed tasks are ignored, so a finished task never causes a conflict. The Streamlit app
shows these messages as warnings after you add a task and when you click **Generate schedule**.

> **Limitation:** conflict detection only checks for an **exact date-and-time match**. It does
> not look at task durations, so two tasks whose durations overlap but start at different
> times are not flagged.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
