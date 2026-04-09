from pawpal_system import Owner, Pet, Scheduler, Task
from tabulate import tabulate


def _task_rows(tasks: list[Task]) -> list[dict[str, object]]:
	"""Format tasks for CLI table output."""
	return [
		{
			"time": task.time,
			"pet": task.pet_name,
			"task": task.description,
			"priority": task.priority,
			"duration": task.duration_minutes,
			"frequency": task.frequency,
			"status": "done" if task.completed else "pending",
		}
		for task in tasks
	]


def build_demo() -> None:
	owner = Owner("Jasmine")

	pet_one = Pet("Fenrir", "dog")
	pet_two = Pet("Luna", "cat")
	owner.add_pet(pet_one)
	owner.add_pet(pet_two)

	pet_one.add_task(
		Task(
			description="Evening walk",
			time="18:00",
			frequency="daily",
			duration_minutes=30,
			priority="medium",
		)
	)
	pet_two.add_task(
		Task(
			description="Feed Luna",
			time="09:00",
			frequency="daily",
			duration_minutes=15,
			priority="high",
		)
	)
	pet_one.add_task(
		Task(
			description="Morning walk",
			time="09:00",
			frequency="once",
			duration_minutes=20,
			priority="high",
		)
	)
	pet_two.add_task(
		Task(
			description="Brush coat",
			time="12:30",
			frequency="weekly",
			duration_minutes=25,
			priority="low",
		)
	)

	scheduler = Scheduler(owner)
	todays_tasks = scheduler.sort_by_priority_then_time(scheduler.get_todays_tasks())

	print("Today's Schedule")
	print(tabulate(_task_rows(todays_tasks), headers="keys", tablefmt="github"))

	conflict_warnings = scheduler.detect_conflicts()
	if conflict_warnings:
		print("\nConflict Warnings")
		for warning in conflict_warnings:
			print(f"- {warning}")

	next_slot = scheduler.find_next_available_slot(duration_minutes=30)
	if next_slot is not None:
		slot_date, slot_time = next_slot
		print(f"\nNext available 30-minute slot: {slot_date.isoformat()} at {slot_time}")

	recurring_task = pet_one.tasks[0]
	next_occurrence = recurring_task.mark_complete()
	if next_occurrence is not None:
		pet_one.add_task(next_occurrence)
		print("\nRecurring task completed; next occurrence created:")
		print(
			tabulate(
				_task_rows([next_occurrence]),
				headers="keys",
				tablefmt="github",
			)
		)


if __name__ == "__main__":
	build_demo()
