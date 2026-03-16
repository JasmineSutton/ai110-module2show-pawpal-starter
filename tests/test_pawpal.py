from datetime import timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


#ADDITION (Phase 2 - Required Test): Validate mark_complete updates status.
#ADDITION (Why): Checklist requires a focused completion-state test.
def test_mark_complete() -> None:
	task = Task(description="Morning walk", time="08:00", frequency="once")

	task.mark_complete()

	assert task.completed is True


#ADDITION (Phase 2 - Required Test): Validate task is added to pet list.
#ADDITION (Why): Checklist requires a task-count assertion after add_task().
def test_add_task() -> None:
	pet = Pet(name="Mochi", species="dog")
	task = Task(description="Feed", time="07:30", frequency="daily")

	pet.add_task(task)

	assert len(pet.tasks) == 1


#ADDITION (Phase 5 - Sorting Test): Validate scheduler returns tasks in chronological order.
#ADDITION (Why): Required to verify sorting correctness behavior.
def test_sort_by_time_orders_tasks() -> None:
	owner = Owner("Jordan")
	pet = Pet(name="Mochi", species="dog")
	owner.add_pet(pet)

	pet.add_task(Task(description="Evening walk", time="18:00"))
	pet.add_task(Task(description="Morning walk", time="08:00"))
	pet.add_task(Task(description="Lunch", time="12:00"))

	scheduler = Scheduler(owner)
	sorted_tasks = scheduler.sort_by_time()

	assert [task.time for task in sorted_tasks] == ["08:00", "12:00", "18:00"]


#ADDITION (Phase 5 - Recurrence Test): Validate daily completion creates the next-day task.
#ADDITION (Why): Required to verify recurring task behavior.
def test_daily_task_completion_creates_next_occurrence() -> None:
	task = Task(description="Feed", time="07:00", frequency="daily")

	next_task = task.mark_complete()

	assert task.completed is True
	assert next_task is not None
	assert next_task.completed is False
	assert next_task.due_date == task.due_date + timedelta(days=1)


#ADDITION (Phase 5 - Conflict Test): Validate scheduler flags duplicate time slots.
#ADDITION (Why): Required to verify conflict detection behavior.
def test_detect_conflicts_flags_duplicate_times() -> None:
	owner = Owner("Jordan")
	pet_one = Pet(name="Mochi", species="dog")
	pet_two = Pet(name="Luna", species="cat")
	owner.add_pet(pet_one)
	owner.add_pet(pet_two)

	pet_one.add_task(Task(description="Walk", time="09:00"))
	pet_two.add_task(Task(description="Feed", time="09:00"))

	scheduler = Scheduler(owner)
	conflicts = scheduler.detect_conflicts()

	assert len(conflicts) == 1
	assert "09:00" in conflicts[0]
