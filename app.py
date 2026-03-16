import streamlit as st

#ADDITION: Import backend classes used in this UI.
from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

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

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

#ADDITION: Persist owner object across reruns using session state.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name)

owner: Owner = st.session_state.owner
owner.name = owner_name
scheduler = Scheduler(owner)

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

#ADDITION: Collect fields used by Task model for backend wiring.
task_time = st.text_input("Time (HH:MM)", value="09:00")
frequency = st.selectbox("Frequency", ["once", "daily", "weekly"], index=0)

if st.button("Add task"):
    #ADDITION: Wire UI action to backend logic (Owner -> Pet -> Task).
    pet = owner.get_pet_by_name(pet_name)
    if pet is None:
        pet = Pet(name=pet_name, species=species)
        owner.add_pet(pet)
        st.success(f"Added pet '{pet_name}'.")

    task = Task(description=task_title, time=task_time, frequency=frequency)
    pet.add_task(task)
    st.success(f"Added task '{task_title}' for {pet.name}.")

    st.session_state.tasks = [
        {
            "title": t.description,
            "duration_minutes": int(duration),
            "priority": priority,
            "time": t.time,
            "frequency": t.frequency,
            "pet": t.pet_name,
            "completed": t.completed,
        }
        for t in scheduler.sort_by_time()
    ]

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    #REFACTOR: Keep starter instructions in-place as comments, then run real scheduler output below.
    # st.warning(
    #     "Not implemented yet. Next step: create your scheduling logic (classes/functions) and call it here."
    # )
    # st.markdown(
    #     """
    # Suggested approach:
    # 1. Design your UML (draft).
    # 2. Create class stubs (no logic).
    # 3. Implement scheduling behavior.
    # 4. Connect your scheduler here and display results.
    # """
    # )

    #ADDITION: Use Scheduler.sort_by_time() for polished ordered display.
    sorted_tasks = scheduler.sort_by_time()
    if sorted_tasks:
        st.table(
            [
                {
                    "pet": task.pet_name,
                    "task": task.description,
                    "time": task.time,
                    "frequency": task.frequency,
                    "completed": task.completed,
                    "date": task.due_date.isoformat(),
                }
                for task in sorted_tasks
            ]
        )
        st.success("Schedule generated from backend classes.")
    else:
        st.info("No tasks available to schedule yet.")

    #ADDITION: Surface conflict warnings from Scheduler.detect_conflicts().
    for warning in scheduler.detect_conflicts():
        st.warning(warning)
