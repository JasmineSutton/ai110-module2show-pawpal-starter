from datetime import date
from pathlib import Path

import streamlit as st

from pawpal_system import (
    MAX_DESCRIPTION_LENGTH,
    MAX_NAME_LENGTH,
    Owner,
    Pet,
    Scheduler,
    Task,
)

DATA_FILE = Path(__file__).with_name("data.json")
PRIORITY_BADGES = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}
STATUS_BADGES = {True: "✅ Done", False: "🕒 Pending"}


def _task_icon(description: str) -> str:
    """Return an emoji that matches the task description."""
    lowered = description.lower()
    if "walk" in lowered:
        return "🐕"
    if "feed" in lowered or "meal" in lowered:
        return "🍽️"
    if "med" in lowered:
        return "💊"
    if "groom" in lowered or "brush" in lowered or "bath" in lowered:
        return "🛁"
    if "play" in lowered or "enrich" in lowered:
        return "🎾"
    return "📌"


def _build_task_rows(tasks: list[Task], include_date: bool = True) -> list[dict[str, object]]:
    """Format tasks for professional Streamlit table output."""
    rows: list[dict[str, object]] = []
    for task in tasks:
        row: dict[str, object] = {
            "task": f"{_task_icon(task.description)} {task.description}",
            "pet": task.pet_name,
            "priority": PRIORITY_BADGES[task.priority],
            "time": task.time,
            "duration (min)": task.duration_minutes,
            "frequency": task.frequency,
            "status": STATUS_BADGES[task.completed],
        }
        if include_date:
            row["date"] = task.due_date.isoformat()
        rows.append(row)
    return rows


def _persist_owner(owner: Owner) -> None:
    """Save the current owner state to disk and surface errors in the UI."""
    try:
        owner.save_to_json(str(DATA_FILE))
        owner.last_load_warning = None
    except OSError as exc:
        st.error(f"Could not save data to {DATA_FILE.name}: {exc}")


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

if "owner" not in st.session_state:
    st.session_state.owner = Owner.load_from_json(str(DATA_FILE))

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

st.title("🐾 PawPal+")
st.caption(f"Data file: {DATA_FILE.name}")

if owner.last_load_warning:
    st.warning(owner.last_load_warning)

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

st.subheader("Quick Demo Inputs")
# Security: Enforce max_chars on all text inputs (OWASP A03:2021 / NIST SI-10)
owner_name = st.text_input("Owner name", value=owner.name, max_chars=MAX_NAME_LENGTH)
pet_name = st.text_input("Pet name", value="Fenrir", max_chars=MAX_NAME_LENGTH)
species = st.selectbox("Species", ["dog", "cat", "other"])

if owner_name.strip() and owner_name != owner.name:
    try:
        owner.set_name(owner_name)
        _persist_owner(owner)
    except ValueError as exc:
        st.error(f"Invalid owner name: {exc}")

st.markdown("### Add Task")
st.caption("Create a task, assign a priority, and save it to persistent app data.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk", max_chars=MAX_DESCRIPTION_LENGTH)
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

task_time = st.text_input("Time (HH:MM)", value="09:00", max_chars=5)
frequency = st.selectbox("Frequency", ["once", "daily", "weekly"], index=0)

if st.button("Add task"):
    # Security: Catch validation errors raised by backend sanitization (OWASP A03 / NIST SI-10).
    try:
        pet = owner.get_pet_by_name(pet_name)
        if pet is None:
            pet = Pet(name=pet_name, species=species)
            owner.add_pet(pet)
            st.success(f"Added pet '{pet.name}'.")

        task = Task(
            description=task_title,
            time=task_time,
            frequency=frequency,
            duration_minutes=int(duration),
            priority=priority,
        )
        pet.add_task(task)
        _persist_owner(owner)
        st.success(f"Added task '{task.description}' for {pet.name}.")
    except ValueError as exc:
        st.error(f"Invalid input: {exc}")

st.divider()

st.subheader("Build Schedule")
st.caption("Choose whether to see today's tasks ordered by pure time or by priority first, then time.")

schedule_order = st.radio(
    "Schedule order",
    ["Priority then time", "Time only"],
    horizontal=True,
)

if st.button("Generate schedule"):
    todays_tasks = scheduler.get_todays_tasks()
    today_token = date.today().isoformat()
    todays_conflicts = [warning for warning in scheduler.detect_conflicts() if today_token in warning]

    if todays_conflicts:
        for warning in todays_conflicts:
            st.warning(f"⚠️ Conflict: {warning}")

    if schedule_order == "Priority then time":
        display_tasks = scheduler.sort_by_priority_then_time(todays_tasks)
    else:
        display_tasks = scheduler.sort_by_time(todays_tasks)

    if display_tasks:
        st.table(_build_task_rows(display_tasks, include_date=False))
        st.success(
            f"Today's schedule: {len(display_tasks)} task(s) across {len(owner.pets)} pet(s)."
        )
    else:
        st.info("No tasks scheduled for today. Add tasks with today's date above.")

st.divider()

st.subheader("Find Next Available Slot")
st.caption("Advanced scheduling capability: find the first open slot that fits a requested duration.")

slot_col1, slot_col2, slot_col3 = st.columns(3)
with slot_col1:
    requested_duration = st.number_input("Requested duration", min_value=1, max_value=240, value=30)
with slot_col2:
    earliest_time = st.text_input("Earliest time", value="08:00", max_chars=5)
with slot_col3:
    latest_time = st.text_input("Latest time", value="21:00", max_chars=5)

if st.button("Find Next Slot"):
    try:
        next_slot = scheduler.find_next_available_slot(
            int(requested_duration),
            earliest_time=earliest_time,
            latest_time=latest_time,
        )
        if next_slot is None:
            st.warning("No available slot found in the next 7 days within those time bounds.")
        else:
            slot_date, slot_time = next_slot
            st.success(
                f"Next available {requested_duration}-minute slot: {slot_date.isoformat()} at {slot_time}."
            )
    except ValueError as exc:
        st.error(f"Could not search for a slot: {exc}")

st.divider()

st.subheader("Mark Task Complete")
st.caption("Completing a recurring task automatically schedules the next occurrence.")

all_tasks = scheduler.get_all_tasks()
incomplete_tasks = [task for task in all_tasks if not task.completed]

if incomplete_tasks:
    task_labels = [
        f"{_task_icon(task.description)} {task.pet_name} — {task.description} @ {task.time} ({PRIORITY_BADGES[task.priority]})"
        for task in incomplete_tasks
    ]
    selected_label = st.selectbox("Select a task to mark complete", task_labels)

    if st.button("Mark Complete"):
        selected_index = task_labels.index(selected_label)
        task_to_complete = incomplete_tasks[selected_index]
        pet = owner.get_pet_by_name(task_to_complete.pet_name)
        if pet is None:
            st.error(f"Could not find pet '{task_to_complete.pet_name}' to update.")
        else:
            next_task = task_to_complete.mark_complete()
            message = f"Completed '{task_to_complete.description}'."
            if next_task is not None:
                try:
                    pet.add_task(next_task)
                    message += f" Next occurrence added for {next_task.due_date.isoformat()}."
                except ValueError as exc:
                    st.warning(f"Task completed but next occurrence not added: {exc}")
            _persist_owner(owner)
            st.success(message)
else:
    st.info("No incomplete tasks to mark.")

st.divider()

st.subheader("Current Tasks")
st.caption("Filter and review the full saved task list with priority badges and status indicators.")

filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    pet_filter = st.selectbox("Filter by pet", ["All pets"] + [pet.name for pet in owner.pets])
with filter_col2:
    status_filter = st.selectbox("Filter by status", ["All tasks", "Pending only", "Completed only"])

completed_filter = None
if status_filter == "Pending only":
    completed_filter = False
elif status_filter == "Completed only":
    completed_filter = True

filtered_tasks = scheduler.filter_tasks(
    completed=completed_filter,
    pet_name=None if pet_filter == "All pets" else pet_filter,
)
display_tasks = scheduler.sort_by_priority_then_time(filtered_tasks)

if display_tasks:
    st.table(_build_task_rows(display_tasks))
    st.success(f"Showing {len(display_tasks)} task(s) from saved data.")
else:
    st.info("No tasks match the current filters.")
