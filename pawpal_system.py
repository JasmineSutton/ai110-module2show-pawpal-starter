from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any, List, Optional

# --- Security Constants (OWASP A03 / NIST AC-3) ---
MAX_NAME_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 200
MAX_TASKS_PER_PET = 50
MAX_PETS_PER_OWNER = 20
ALLOWED_FREQUENCIES = {"once", "daily", "weekly"}
ALLOWED_PRIORITIES = {"low", "medium", "high"}
PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


def _sanitize(value: str, max_length: int = MAX_NAME_LENGTH) -> str:
    """Strip whitespace, enforce length limit, and remove dangerous characters.

    Addresses OWASP A03:2021 (Injection) and NIST SI-10 (Information Input Validation).
    """
    cleaned = value.strip()
    if len(cleaned) > max_length:
        raise ValueError(
            f"Input exceeds maximum length of {max_length} characters."
        )
    # Remove HTML/script tags to prevent XSS if rendered in a web UI
    cleaned = re.sub(r"<[^>]*>", "", cleaned)
    return cleaned


def _validate_time(time_str: str) -> str:
    """Validate that a time string matches HH:MM 24-hour format.

    Addresses OWASP A03:2021 (Injection) and NIST SI-10 (Information Input Validation).
    """
    sanitized = time_str.strip()
    if not TIME_PATTERN.match(sanitized):
        raise ValueError(
            f"Invalid time format '{sanitized}'. Expected HH:MM (00:00-23:59)."
        )
    return sanitized


def _time_to_minutes(time_str: str) -> int:
	"""Convert HH:MM into total minutes since midnight."""
	hours, minutes = time_str.split(":")
	return int(hours) * 60 + int(minutes)


def _minutes_to_time(total_minutes: int) -> str:
	"""Convert total minutes since midnight into HH:MM."""
	hours, minutes = divmod(total_minutes, 60)
	return f"{hours:02d}:{minutes:02d}"


#ADDITION: Create Task dataclass with required fields and completion method.
@dataclass
class Task:
	description: str
	time: str
	frequency: str = "once"
	completed: bool = False
	pet_name: str = ""
	due_date: date = field(default_factory=date.today)
	#DESIGN-CHANGE: Added duration and priority so the backend captures what the UI collects.
	duration_minutes: int = 15
	priority: str = "medium"

	def __post_init__(self) -> None:
		"""Validate all fields on creation.

		Security: OWASP A03:2021 (Injection), NIST SI-10 (Information Input Validation).
		"""
		self.description = _sanitize(self.description, MAX_DESCRIPTION_LENGTH)
		self.time = _validate_time(self.time)
		self.pet_name = _sanitize(self.pet_name, MAX_NAME_LENGTH)

		normalized_freq = self.frequency.strip().lower()
		if normalized_freq not in ALLOWED_FREQUENCIES:
			raise ValueError(
				f"Invalid frequency '{self.frequency}'. "
				f"Allowed values: {', '.join(sorted(ALLOWED_FREQUENCIES))}."
			)
		self.frequency = normalized_freq

		#DESIGN-CHANGE: Validate duration and priority on creation.
		if not isinstance(self.duration_minutes, int) or self.duration_minutes < 1:
			raise ValueError("Duration must be a positive integer (minutes).")
		normalized_priority = self.priority.strip().lower()
		if normalized_priority not in ALLOWED_PRIORITIES:
			raise ValueError(
				f"Invalid priority '{self.priority}'. "
				f"Allowed values: {', '.join(sorted(ALLOWED_PRIORITIES))}."
			)
		self.priority = normalized_priority

	#ADDITION added description/time/frequency/completed status and mark_complete().
	def mark_complete(self) -> Optional["Task"]:
		"""Mark task complete and return next recurring task when applicable."""
		self.completed = True

		#ADDITION: Generate next task for daily/weekly frequencies
		if self.frequency == "daily":
			return Task(
				description=self.description,
				time=self.time,
				frequency=self.frequency,
				completed=False,
				pet_name=self.pet_name,
				due_date=self.due_date + timedelta(days=1),
				duration_minutes=self.duration_minutes,
				priority=self.priority,
			)
		if self.frequency == "weekly":
			return Task(
				description=self.description,
				time=self.time,
				frequency=self.frequency,
				completed=False,
				pet_name=self.pet_name,
				due_date=self.due_date + timedelta(days=7),
				duration_minutes=self.duration_minutes,
				priority=self.priority,
			)
		return None

	def to_dict(self) -> dict[str, Any]:
		"""Return a JSON-serializable representation of this task."""
		return {
			"description": self.description,
			"time": self.time,
			"frequency": self.frequency,
			"completed": self.completed,
			"pet_name": self.pet_name,
			"due_date": self.due_date.isoformat(),
			"duration_minutes": self.duration_minutes,
			"priority": self.priority,
		}

	@classmethod
	def from_dict(cls, data: dict[str, Any]) -> "Task":
		"""Create a task from a dictionary loaded from JSON."""
		return cls(
			description=data["description"],
			time=data["time"],
			frequency=data.get("frequency", "once"),
			completed=data.get("completed", False),
			pet_name=data.get("pet_name", ""),
			due_date=date.fromisoformat(data.get("due_date", date.today().isoformat())),
			duration_minutes=int(data.get("duration_minutes", 15)),
			priority=data.get("priority", "medium"),
		)


ALLOWED_SPECIES = {"dog", "cat", "other"}


#ADDITION: Created Pet dataclass with task collection and add method.
@dataclass
class Pet:
	name: str
	species: str
	tasks: List[Task] = field(default_factory=list)

	def __post_init__(self) -> None:
		"""Validate pet fields on creation.

		Security: OWASP A03:2021 (Injection), NIST SI-10 (Information Input Validation).
		"""
		self.name = _sanitize(self.name, MAX_NAME_LENGTH)
		normalized_species = self.species.strip().lower()
		if normalized_species not in ALLOWED_SPECIES:
			raise ValueError(
				f"Invalid species '{self.species}'. "
				f"Allowed values: {', '.join(sorted(ALLOWED_SPECIES))}."
			)
		self.species = normalized_species

	def add_task(self, task: Task) -> None:
		"""Add a task to this pet.

		Security: OWASP A04:2021 (Insecure Design) — enforces task count limit.
		"""
		if len(self.tasks) >= MAX_TASKS_PER_PET:
			raise ValueError(
				f"Cannot add more than {MAX_TASKS_PER_PET} tasks per pet."
			)
		#REFACTOR: Ensure each task knows its owning pet. Needed for filtering and UI output by pet name.
		if not task.pet_name:
			task.pet_name = self.name
		self.tasks.append(task)

	def to_dict(self) -> dict[str, Any]:
		"""Return a JSON-serializable representation of this pet."""
		return {
			"name": self.name,
			"species": self.species,
			"tasks": [task.to_dict() for task in self.tasks],
		}

	@classmethod
	def from_dict(cls, data: dict[str, Any]) -> "Pet":
		"""Create a pet from a dictionary loaded from JSON."""
		pet = cls(name=data["name"], species=data["species"])
		for task_data in data.get("tasks", []):
			pet.add_task(Task.from_dict(task_data))
		return pet


#ADDITION: Owner now manages pets and can return all pet tasks through consume tasks through Owner -> Pet -> Task relationship.
class Owner:
	def __init__(self, name: str) -> None:
		# Security: OWASP A03:2021 (Injection), NIST SI-10 (Information Input Validation).
		self.name = _sanitize(name, MAX_NAME_LENGTH)
		self.pets: List[Pet] = []
		self.last_load_warning: Optional[str] = None

	def set_name(self, name: str) -> None:
		"""Update the owner name using the same validation as initial creation."""
		self.name = _sanitize(name, MAX_NAME_LENGTH)

	def add_pet(self, pet: Pet) -> None:
		"""Add a pet to this owner.

		Security: OWASP A04:2021 (Insecure Design) — enforces pet count limit.
		"""
		if len(self.pets) >= MAX_PETS_PER_OWNER:
			raise ValueError(
				f"Cannot add more than {MAX_PETS_PER_OWNER} pets per owner."
			)
		#DESIGN-CHANGE: Reject duplicate pet names to prevent ambiguous lookups.
		if self.get_pet_by_name(pet.name) is not None:
			raise ValueError(
				f"A pet named '{pet.name}' already exists for this owner."
			)
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

	def to_dict(self) -> dict[str, Any]:
		"""Return a JSON-serializable representation of this owner."""
		return {
			"name": self.name,
			"pets": [pet.to_dict() for pet in self.pets],
		}

	def save_to_json(self, file_path: str = "data.json") -> None:
		"""Persist the owner, pets, and tasks to a JSON file."""
		path = Path(file_path)
		path.parent.mkdir(parents=True, exist_ok=True)
		temp_path = path.with_name(f"{path.name}.tmp")
		try:
			temp_path.write_text(
				json.dumps(self.to_dict(), indent=2),
				encoding="utf-8",
			)
			temp_path.replace(path)
		except OSError:
			if temp_path.exists():
				temp_path.unlink()
			raise

	@classmethod
	def load_from_json(
		cls, file_path: str = "data.json", default_name: str = "Jasmine"
	) -> "Owner":
		"""Load owner data from JSON or return an empty owner if unavailable."""
		path = Path(file_path)
		if not path.exists():
			return cls(default_name)

		try:
			payload = json.loads(path.read_text(encoding="utf-8"))
			owner = cls(payload.get("name", default_name))
			for pet_data in payload.get("pets", []):
				owner.add_pet(Pet.from_dict(pet_data))
			return owner
		except (json.JSONDecodeError, OSError, KeyError, TypeError, ValueError) as exc:
			owner = cls(default_name)
			owner.last_load_warning = (
				f"Could not load saved data from {path.name}: {exc}. "
				"Starting with empty data."
			)
			return owner


#ADDITION Scheduler exposes retrieval, sorting, filtering, and conflict checks.
class Scheduler:
	def __init__(self, owner: Owner) -> None:
		self.owner = owner

	def get_all_tasks(self) -> List[Task]:
		"""Return all tasks for the scheduler owner."""
		return self.owner.get_all_tasks()

	def print_schedule(self) -> str:
		"""Return a printable priority-first schedule string for today's tasks."""
		lines = ["Today's Schedule"]
		for task in self.sort_by_priority_then_time(self.get_todays_tasks()):
			status = "Done" if task.completed else "Pending"
			lines.append(
				f"- {task.time} | {task.pet_name} | {task.description} | {task.frequency} | {task.priority} | {status}"
			)
		if len(lines) == 1:
			lines.append("  (no tasks scheduled for today)")
		return "\n".join(lines)

	def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
		"""Sort tasks chronologically by date and HH:MM time."""
		tasks_to_sort = self.get_all_tasks() if tasks is None else tasks
		return sorted(tasks_to_sort, key=lambda task: (task.due_date, task.time))

	def sort_by_priority_then_time(
		self, tasks: Optional[List[Task]] = None
	) -> List[Task]:
		"""Sort tasks by priority tier first, then by date and time."""
		tasks_to_sort = self.get_all_tasks() if tasks is None else tasks
		return sorted(
			tasks_to_sort,
			key=lambda task: (PRIORITY_RANK[task.priority], task.due_date, task.time),
		)

	#DESIGN-CHANGE: Added method so "see today's tasks" only returns today's date.
	def get_todays_tasks(self) -> List[Task]:
		"""Return tasks whose due_date is today, sorted by time."""
		today = date.today()
		return self.sort_by_time(
			[t for t in self.get_all_tasks() if t.due_date == today]
		)

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

	def find_next_available_slot(
		self,
		duration_minutes: int,
		start_date: Optional[date] = None,
		earliest_time: str = "08:00",
		latest_time: str = "21:00",
		search_days: int = 7,
		step_minutes: int = 15,
	) -> Optional[tuple[date, str]]:
		"""Return the first open slot that fits the requested duration."""
		if duration_minutes < 1:
			raise ValueError("Duration must be at least 1 minute.")
		if search_days < 1:
			raise ValueError("search_days must be at least 1.")
		if step_minutes < 1:
			raise ValueError("step_minutes must be at least 1.")

		day_start = _time_to_minutes(_validate_time(earliest_time))
		day_end = _time_to_minutes(_validate_time(latest_time))
		if day_end <= day_start:
			raise ValueError("latest_time must be later than earliest_time.")

		first_day = start_date or date.today()
		for offset in range(search_days):
			candidate_date = first_day + timedelta(days=offset)
			candidate_start = day_start
			day_tasks = self.sort_by_time(
				[
					task
					for task in self.get_all_tasks()
					if task.due_date == candidate_date and not task.completed
				]
			)

			for task in day_tasks:
				task_start = _time_to_minutes(task.time)
				task_end = task_start + task.duration_minutes
				if candidate_start + duration_minutes <= task_start:
					return candidate_date, _minutes_to_time(candidate_start)
				if candidate_start < task_end:
					candidate_start = task_end
					remainder = candidate_start % step_minutes
					if remainder:
						candidate_start += step_minutes - remainder

			if candidate_start + duration_minutes <= day_end:
				return candidate_date, _minutes_to_time(candidate_start)

		return None


# --- 1b. Design Changes ---------------------------------------------------
# The following changes were made to address missing relationships and logic
# gaps discovered during a design review of the original starter code.
#
# 1. Added `duration_minutes` and `priority` fields to the Task dataclass.
#    WHY: The Streamlit UI (app.py) collected duration and priority from the
#    user but the Task model had no matching attributes.  The values were
#    stored only in the display dict and lost to the backend, meaning the
#    scheduler could never reason about how long a task takes or how
#    important it is.
#
# 2. Added `ALLOWED_PRIORITIES` constant and priority/duration validation
#    in Task.__post_init__.
#    WHY: Every user-supplied field should be validated at the system
#    boundary (OWASP A03 / NIST SI-10).  Without validation, invalid
#    priorities like "urgent" or negative durations would be silently
#    accepted.
#
# 3. Propagated `duration_minutes` and `priority` in Task.mark_complete()
#    when generating the next recurring task.
#    WHY: Recurring tasks created by mark_complete() previously lost
#    duration and priority, reverting to defaults.  The next occurrence
#    should carry the same values as the original.
#
# 4. Added duplicate-pet-name guard in Owner.add_pet().
#    WHY: get_pet_by_name() returns the first match; if two pets share a
#    name the second one becomes unreachable.  Rejecting duplicates up
#    front prevents ambiguous lookups.
#
# 5. Added Scheduler.get_todays_tasks() method.
#    WHY: print_schedule() was titled "Today's Schedule" but returned
#    tasks for all dates.  A dedicated method lets callers retrieve only
#    today's tasks, which is the expected behavior for "see today's
#    tasks."
# --------------------------------------------------------------------------
