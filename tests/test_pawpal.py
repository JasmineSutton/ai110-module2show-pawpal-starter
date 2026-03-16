from pawpal_system import Pet, Task


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
