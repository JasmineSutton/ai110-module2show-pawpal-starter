from pawpal_system import Owner, Pet, Scheduler, Task


#ADDITION: Built required sample flow and algorithm demonstrations of owner, two pets, multiple tasks, sorting, conflicts, and recurrence checks.
def build_demo() -> None:
	owner = Owner("Jordan")

	pet_one = Pet("Mochi", "dog")
	pet_two = Pet("Luna", "cat")
	owner.add_pet(pet_one)
	owner.add_pet(pet_two)

	#ADDITION: Intentionally add out-of-order tasks and one same-time conflict to test.
	pet_one.add_task(Task(description="Evening walk", time="18:00", frequency="daily"))
	pet_two.add_task(Task(description="Feed Luna", time="09:00", frequency="daily"))
	pet_one.add_task(Task(description="Morning walk", time="09:00", frequency="once"))
	pet_two.add_task(Task(description="Brush coat", time="12:30", frequency="weekly"))

	scheduler = Scheduler(owner)

	print(scheduler.print_schedule())

	conflict_warnings = scheduler.detect_conflicts()
	if conflict_warnings:
		print("\nConflict Warnings")
		for warning in conflict_warnings:
			print(f"- {warning}")

	recurring_task = pet_one.tasks[0]
	next_occurrence = recurring_task.mark_complete()
	if next_occurrence is not None:
		pet_one.add_task(next_occurrence)
		print("\nRecurring task completed; next occurrence created:")
		print(
			f"- {next_occurrence.description} at {next_occurrence.time} on {next_occurrence.due_date.isoformat()}"
		)


if __name__ == "__main__":
	build_demo()
