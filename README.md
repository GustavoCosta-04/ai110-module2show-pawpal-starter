# PawPal+ (Module 2 Project)

**PawPal+** is a pet care planning app built with Python and Streamlit. A pet owner can register
their pets, schedule care tasks, and see a clean, time-ordered daily plan, with warnings when two
tasks clash. The scheduling logic lives in plain, tested Python classes (`pawpal_system.py`), and the
Streamlit interface (`app.py`) is a thin layer on top of them.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan

## Features

Everything below is implemented in the current code.

- **Pet registration and management:** add pets with a name, species (dog, cat or other) and age.
  Pets are listed with their task counts, and the owner's name can be edited in the interface.
  The backend also supports removing pets and tasks (`Owner.remove_pet`, `Pet.remove_task`), but the
  interface does not expose that yet.
- **Task creation:** schedule a task for a chosen pet with a title, duration, priority
  (low, medium or high), date and time. Bad input (such as an empty title or no pet) is reported
  with an error message instead of crashing.
- **Task completion:** mark any pending task complete from the interface.
- **Chronological task sorting:** the task table is ordered by date, then time, then priority
  (`Scheduler.sort_by_time`).
- **Filtering by pet and completion status:** filter the task table by pet name and by
  All / Pending / Completed (`Scheduler.filter_tasks`).
- **Daily schedule generation:** pick a date and generate that day's schedule in time order
  (`Scheduler.get_daily_tasks`).
- **Recurring task generation:** completing a daily or weekly task automatically creates the next
  occurrence one day or seven days later on the same pet, without creating duplicates
  (`Scheduler.mark_task_complete`, `Scheduler.generate_recurring_tasks`).
- **Scheduling conflict detection and warnings:** pending tasks that share the exact same date and
  time are flagged with readable warnings that include the date, time, task titles and pet names
  (`Scheduler.detect_conflicts`, `Scheduler.get_conflict_warnings`).
- **Streamlit user interface:** a single-page app that keeps its data in `st.session_state`, so the
  owner, pets and tasks persist across reruns for the length of a browser session. Data is not saved
  to disk.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

### Run the command-line demo

```bash
python main.py
```

### Project layout

| Path | Purpose |
|------|---------|
| `pawpal_system.py` | The backend classes: `Owner`, `Pet`, `Task`, `Scheduler` |
| `app.py` | The Streamlit interface |
| `main.py` | A command-line demo of the backend features |
| `tests/test_pawpal.py` | The automated pytest suite |
| `diagrams/uml_final.mmd` | Final UML class diagram (Mermaid) |
| `diagrams/uml_draft.mmd` | Original draft of the UML diagram |

## 📸 Demo Walkthrough

### What you can do in the app

- **Add pets** with a name, species and age, and see them in the "Pets owned by ..." table.
- **Add tasks** for a selected pet with a title, duration, priority, date and time.
- **Review tasks** in a table that is always sorted chronologically, and narrow it with the
  "Filter by pet" and "Filter by status" dropdowns.
- **Mark tasks complete** with the "Mark a task complete" dropdown and button.
- **See conflict warnings** (yellow `st.warning` boxes) above the task table whenever two pending
  tasks share the same date and time.
- **Generate a daily schedule** for any date in the "Build Schedule" section.

### Example workflow

1. Start the app with `streamlit run app.py`.
2. Under **Quick Demo Inputs**, enter an owner name, a pet name, a species and an age, then click
   **Add pet**. The pet appears in the pets table.
3. Under **Tasks**, enter a title (for example "Morning walk"), a duration and a priority, choose
   the pet, set a date and time, and click **Add task**. A green confirmation appears and the task
   shows up in the **Current tasks** table.
4. Add a second task for another pet at the same date and time. A warning such as
   `Conflict at 08:00 on 2026-11-02: Morning walk (Buddy), Give medication (Whiskers)` appears
   above the table.
5. Use **Filter by pet** or **Filter by status** to focus the table, and **Mark complete** to finish
   a task. Completing a task removes it from the conflict check.
6. Under **Build Schedule**, choose a date and click **Generate schedule** to see that day's tasks in
   time order.

### How the smart features work

- **Sorting:** every table is built from the scheduler's sorted list, so tasks added in any order are
  shown earliest first. Ties on the same time are broken by priority, high first.
- **Filtering:** the interface passes the chosen pet name and completion status to
  `Scheduler.filter_tasks`, and the scheduler returns the matching tasks, still in time order.
- **Recurrence:** completing a task whose frequency is `daily` or `weekly` creates a new pending copy
  one or seven days later on the same pet. Completing the same task again does not create a second
  copy. The task form in the app does not have a frequency field yet, so recurring tasks are
  currently created in code; `main.py` demonstrates the behavior.
- **Conflict warnings:** pending tasks are grouped by `(date, time)`. Any group of two or more
  becomes one warning. Completed tasks are ignored.

### Sample CLI output

Actual output of `python main.py`. The first section uses today's date and the remaining sections
use the date they were run (2026-11-02 here), so your dates will differ.

```
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

==============================================================
  Sorting & Filtering Demo
==============================================================

Original order (as added):
  18:00  Rex      Evening walk      Pending
  12:00  Rex      Vet checkup       Pending
  07:30  Luna     Breakfast         Done
  09:15  Luna     Brush fur         Pending

Sorted by time:
  07:30  Luna     Breakfast         Done
  09:15  Luna     Brush fur         Pending
  12:00  Rex      Vet checkup       Pending
  18:00  Rex      Evening walk      Pending

Only Rex's tasks:
  12:00  Rex      Vet checkup       Pending
  18:00  Rex      Evening walk      Pending

Only completed tasks:
  07:30  Luna     Breakfast         Done

Only pending tasks:
  09:15  Luna     Brush fur         Pending
  12:00  Rex      Vet checkup       Pending
  18:00  Rex      Evening walk      Pending

Luna's pending tasks:
  09:15  Luna     Brush fur         Pending

==============================================================
  Recurring Tasks Demo
==============================================================

Completed tasks:
  Give vitamins daily   2026-11-02  Done: True
  Bath time     weekly  2026-11-02  Done: True

Newly generated occurrences:
  Give vitamins daily   2026-11-03  Done: False
  Bath time     weekly  2026-11-09  Done: False

Completing 'Give vitamins' again created: None
generate_recurring_tasks() created 0 new task(s)
Rex now has 4 tasks in total

==============================================================
  Conflict Detection Demo
==============================================================

Warnings found: 2
  WARNING: Conflict at 08:00 on 2026-11-02: Morning walk (Buddy), Give medication (Whiskers)
  WARNING: Conflict at 11:00 on 2026-11-02: Vet visit (Buddy), Nail trim (Whiskers)

14:00 is not listed: 'Play session' is completed, so it is excluded.
After completing Buddy's 08:00 and 11:00 tasks: 0 warning(s)
```

## 🏗️ Architecture

The system has four classes, defined in `pawpal_system.py`. The final UML class diagram is in
[`diagrams/uml_final.mmd`](diagrams/uml_final.mmd) (the original draft is kept in
`diagrams/uml_draft.mmd`).

| Class | Responsibility |
|-------|----------------|
| `Owner` | Represents the pet owner and holds their list of pets. Adds, removes and lists pets, and `get_all_tasks()` gathers the tasks of every pet. |
| `Pet` | A dataclass for one animal. Holds its own list of tasks and adds, removes and lists them. |
| `Task` | A dataclass for one care activity: title, type, date, time, priority, completion status, and optional recurrence (`frequency` of `once`, `daily` or `weekly`). `mark_complete()` marks it done. |
| `Scheduler` | The central manager. Reads tasks through the `Owner`, then sorts, filters, builds daily schedules, creates recurring tasks and detects conflicts. It can also hold standalone tasks added directly to it. |

**Relationships**

- An `Owner` has many `Pet`s, and a `Pet` has many `Task`s.
- A `Scheduler` is created with an `Owner` and reads every pet's tasks through
  `Owner.get_all_tasks()`, so it never keeps a separate copy of pet data.
- When the scheduler creates a recurring task, it adds it to the pet that owned the original.

`Task`, `Pet` and `Owner` validate their inputs and raise `ValueError` on bad data, which the
interface shows as an error message.

To preview the diagram in VS Code, paste its contents into a `mermaid` code block in a Markdown
file (with the Markdown Preview Mermaid Support extension), or open it with a Mermaid extension.

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
shows these messages as warnings above the task table whenever conflicts exist.

> **Limitation:** conflict detection only checks for an **exact date-and-time match**. It does
> not look at task durations, so two tasks whose durations overlap but start at different
> times are not flagged.

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

The tests cover the backend classes only. The Streamlit interface is not covered by automated tests.

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
