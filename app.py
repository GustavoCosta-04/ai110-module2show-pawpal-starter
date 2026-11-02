import datetime

import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Streamlit reruns this whole script on every interaction, so objects must live in
# st.session_state to survive. Only create them if they don't exist yet.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_id=1, name="Jordan", email="jordan@example.com")

if "scheduler" not in st.session_state:
    # Shares the same Owner object, so it always sees the owner's current pets and tasks.
    st.session_state.scheduler = Scheduler(st.session_state.owner)

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

owner = st.session_state.owner
scheduler = st.session_state.scheduler


def pet_name_for(task):
    """Return the name of the pet that owns the given task."""
    for pet in owner.get_pets():
        if any(task is t for t in pet.get_tasks()):
            return pet.name
    return "Unknown"


def task_rows(tasks):
    """Turn Task objects into simple rows for st.table."""
    return [
        {
            "Date": str(t.date),
            "Time": t.time.strftime("%H:%M"),
            "Pet": pet_name_for(t),
            "Task": t.title,
            "Duration": t.description,
            "Priority": t.priority,
            "Done": "Yes" if t.completed else "No",
        }
        for t in tasks
    ]


st.subheader("Quick Demo Inputs")
owner_name = st.text_input("Owner name", value="Jordan")
if owner_name.strip():
    owner.name = owner_name.strip()

pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
pet_age = st.number_input("Pet age (years)", min_value=0, max_value=40, value=1)

if st.button("Add pet"):
    try:
        new_pet_id = max((p.pet_id for p in owner.get_pets()), default=0) + 1
        new_pet = Pet(
            pet_id=new_pet_id,
            name=pet_name.strip(),
            species=species,
            age=int(pet_age),
            owner_id=owner.owner_id,
        )
        owner.add_pet(new_pet)
        st.success(f"Added {new_pet.name} the {new_pet.species}.")
    except ValueError as error:
        st.error(str(error))

if owner.get_pets():
    st.write(f"Pets owned by {owner.name}:")
    st.table(
        [
            {"Name": p.name, "Species": p.species, "Age": p.age, "Tasks": len(p.get_tasks())}
            for p in owner.get_pets()
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Pick a pet and add tasks. They are stored on the pet and fed to the scheduler.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5, col6 = st.columns(3)
with col4:
    # st.selectbox hands back a COPY of the chosen option, so select by pet_id
    # and look up the real Pet object stored in the owner afterwards.
    pets_by_id = {p.pet_id: p for p in owner.get_pets()}
    selected_pet_id = st.selectbox(
        "Pet", list(pets_by_id), format_func=lambda pet_id: pets_by_id[pet_id].name
    )
    selected_pet = pets_by_id.get(selected_pet_id)
with col5:
    task_date = st.date_input("Date", value=datetime.date.today())
with col6:
    task_time = st.time_input("Time", value=datetime.time(8, 0))

if st.button("Add task"):
    if selected_pet is None:
        st.error("Add a pet first, then choose it for this task.")
    else:
        try:
            new_task_id = max((t.task_id for t in scheduler.get_all_tasks()), default=0) + 1
            new_task = Task(
                task_id=new_task_id,
                title=task_title.strip(),
                task_type="general",
                date=task_date,
                time=task_time,
                priority=priority,
                description=f"{int(duration)} min",
            )
            selected_pet.add_task(new_task)
            st.success(f"Added '{new_task.title}' for {selected_pet.name}.")
        except ValueError as error:
            st.error(str(error))

pending_tasks = scheduler.filter_tasks(completed=False)
if pending_tasks:
    # Select by task_id (selectbox returns copies), then look up the real Task.
    tasks_by_id = {t.task_id: t for t in pending_tasks}
    complete_id = st.selectbox(
        "Mark a task complete",
        list(tasks_by_id),
        format_func=lambda i: (
            f"{tasks_by_id[i].title} ({pet_name_for(tasks_by_id[i])}) - "
            f"{tasks_by_id[i].date} {tasks_by_id[i].time.strftime('%H:%M')}"
        ),
    )
    if st.button("Mark complete"):
        done_task = tasks_by_id[complete_id]
        next_task = scheduler.mark_task_complete(done_task)
        st.success(f"Completed '{done_task.title}'.")
        if next_task is not None:
            st.info(f"Next {next_task.frequency} occurrence scheduled for {next_task.date}.")

conflict_warnings = scheduler.get_conflict_warnings()
for message in conflict_warnings:
    st.warning(message)

if owner.get_all_tasks():
    st.write("Current tasks (sorted by date and time):")
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        pet_filter = st.selectbox(
            "Filter by pet", ["All pets"] + [p.name for p in owner.get_pets()]
        )
    with filter_col2:
        status_filter = st.selectbox("Filter by status", ["All", "Pending", "Completed"])

    # The Scheduler does the filtering and sorting; None means "don't filter on this".
    filtered_tasks = scheduler.filter_tasks(
        pet_name=None if pet_filter == "All pets" else pet_filter,
        completed={"All": None, "Pending": False, "Completed": True}[status_filter],
    )
    if filtered_tasks:
        st.table(task_rows(filtered_tasks))
    else:
        st.info("No tasks match these filters.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Shows one day's tasks in time order and checks every pet's tasks for conflicts.")

schedule_date = st.date_input("Schedule date", value=datetime.date.today())

if st.button("Generate schedule"):
    daily_tasks = scheduler.get_daily_tasks(schedule_date)
    if not daily_tasks:
        st.info(f"No tasks scheduled for {schedule_date}.")
    else:
        st.success(f"{len(daily_tasks)} task(s) scheduled for {schedule_date}.")
        st.table(task_rows(daily_tasks))
    if conflict_warnings:
        st.caption("Scheduling conflicts are listed in the warnings above the task table.")
    else:
        st.success("No scheduling conflicts.")
