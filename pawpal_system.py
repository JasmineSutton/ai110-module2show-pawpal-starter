from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional


#ADDITION: Create Task dataclass with required fields and completion method.
@dataclass
class Task:
	description: str
	time: str
	frequency: str = "once"
	completed: bool = False
	pet_name: str = ""
	due_date: date = field(default_factory=date.today)

	#ADDITION added description/time/frequency/completed status and mark_complete().
	def mark_complete(self) -> Optional["Task"]:
		"""Mark task complete and return next recurring task when applicable."""
		self.completed = True

		#ADDITION: Generate next task for daily/weekly frequencies
		normalized_frequency = self.frequency.strip().lower()
		if normalized_frequency == "daily":
			return Task(
				description=self.description,
				time=self.time,
				frequency=self.frequency,
				completed=False,
				pet_name=self.pet_name,
				due_date=self.due_date + timedelta(days=1),
			)
		if normalized_frequency == "weekly":
			return Task(
				description=self.description,
				time=self.time,
				frequency=self.frequency,
				completed=False,
				pet_name=self.pet_name,
				due_date=self.due_date + timedelta(days=7),
			)
		return None


#ADDITION: Created Pet dataclass with task collection and add method.
@dataclass
class Pet:
	name: str
	species: str
	tasks: List[Task] = field(default_factory=list)

	def add_task(self, task: Task) -> None:
		"""Add a task to this pet."""
		#REFACTOR: Ensure each task knows its owning pet. Needed for filtering and UI output by pet name.
		if not task.pet_name:
			task.pet_name = self.name
		self.tasks.append(task)


#ADDITION: Owner now manages pets and can return all pet tasks through consume tasks through Owner -> Pet -> Task relationship.
class Owner:
	def __init__(self, name: str) -> None:
		self.name = name
		self.pets: List[Pet] = []

	def add_pet(self, pet: Pet) -> None:
		"""Add a pet to this owner."""
		self.pets.append(pet)

	def get_pet_by_name(self, pet_name: str) -> Optional[Pet]:
		"""Return a pet by name when found."""
		normalized_name = pet_name.strip().lower()
		for pet in self.pets:
			if pet.name.strip().lower() == normalized_name:
				return pet
		return None

	def get_all_tasks(self) -> List[Task]:
		"""Return all tasks across all pets."""
		all_tasks: List[Task] = []
		for pet in self.pets:
			all_tasks.extend(pet.tasks)
		return all_tasks


#ADDITION Scheduler exposes retrieval, sorting, filtering, and conflict checks.
class Scheduler:
	def __init__(self, owner: Owner) -> None:
		self.owner = owner

	def get_all_tasks(self) -> List[Task]:
		"""Return all tasks for the scheduler owner."""
		return self.owner.get_all_tasks()

	def print_schedule(self) -> str:
		"""Return a printable, time-sorted schedule string."""
		lines = ["Today's Schedule"]
		for task in self.sort_by_time():
			status = "Done" if task.completed else "Pending"
			lines.append(
				f"- {task.due_date.isoformat()} {task.time} | {task.pet_name} | {task.description} | {task.frequency} | {status}"
			)
		return "\n".join(lines)

	def sort_by_time(self) -> List[Task]:
		"""Sort tasks chronologically by date and HH:MM time."""
		return sorted(self.get_all_tasks(), key=lambda task: (task.due_date, task.time))

	def filter_tasks(
		self, completed: Optional[bool] = None, pet_name: Optional[str] = None
	) -> List[Task]:
		"""Filter tasks by completion status and/or pet name."""
		filtered_tasks = self.get_all_tasks()
		if completed is not None:
			filtered_tasks = [
				task for task in filtered_tasks if task.completed == completed
			]
		if pet_name:
			normalized_name = pet_name.strip().lower()
			filtered_tasks = [
				task
				for task in filtered_tasks
				if task.pet_name.strip().lower() == normalized_name
			]
		return filtered_tasks

	def detect_conflicts(self) -> List[str]:
		"""Return warning messages for tasks that share exact date/time."""
		by_time_slot: dict[tuple[date, str], List[Task]] = {}
		for task in self.get_all_tasks():
			by_time_slot.setdefault((task.due_date, task.time), []).append(task)

		warnings: List[str] = []
		for (task_date, task_time), slot_tasks in by_time_slot.items():
			if len(slot_tasks) > 1:
				joined_descriptions = ", ".join(
					task.description for task in slot_tasks
				)
				warnings.append(
					f"Conflict at {task_date.isoformat()} {task_time}: {joined_descriptions}"
				)
		return warnings
