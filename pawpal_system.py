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
		pass


#ADDITION: Created Pet dataclass with task collection and add method.
@dataclass
class Pet:
	name: str
	species: str
	tasks: List[Task] = field(default_factory=list)

	def add_task(self, task: Task) -> None:
		"""Add a task to this pet."""
		pass


#ADDITION: Owner now manages pets and can return all pet tasks through consume tasks through Owner -> Pet -> Task relationship.
class Owner:
	def __init__(self, name: str) -> None:
		self.name = name
		self.pets: List[Pet] = []

	def add_pet(self, pet: Pet) -> None:
		"""Add a pet to this owner."""
		pass

	def get_pet_by_name(self, pet_name: str) -> Optional[Pet]:
		"""Return a pet by name when found."""
		pass

	def get_all_tasks(self) -> List[Task]:
		"""Return all tasks across all pets."""
		pass


#ADDITION Scheduler exposes retrieval, sorting, filtering, and conflict checks.
class Scheduler:
	def __init__(self, owner: Owner) -> None:
		self.owner = owner

	def get_all_tasks(self) -> List[Task]:
		"""Return all tasks for the scheduler owner."""
		pass

	def print_schedule(self) -> str:
		"""Return a printable, time-sorted schedule string."""
		pass

	def sort_by_time(self) -> List[Task]:
		"""Sort tasks chronologically by date and HH:MM time."""
		pass

	def filter_tasks(
		self, completed: Optional[bool] = None, pet_name: Optional[str] = None
	) -> List[Task]:
		"""Filter tasks by completion status and/or pet name."""
		pass

	def detect_conflicts(self) -> List[str]:
		"""Return warning messages for tasks that share exact date/time."""
		pass
