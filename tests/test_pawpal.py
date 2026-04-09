import pytest
from datetime import timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete() -> None:
	task = Task(description="Morning walk", time="08:00", frequency="once")

	task.mark_complete()

	assert task.completed is True


def test_add_task() -> None:
	pet = Pet(name="Fenrir", species="dog")
	task = Task(description="Feed", time="07:30", frequency="daily")

	pet.add_task(task)

	assert len(pet.tasks) == 1


def test_sort_by_time_orders_tasks() -> None:
	owner = Owner("Jasmine")
	pet = Pet(name="Fenrir", species="dog")
	owner.add_pet(pet)

	pet.add_task(Task(description="Evening walk", time="18:00"))
	pet.add_task(Task(description="Morning walk", time="08:00"))
	pet.add_task(Task(description="Lunch", time="12:00"))

	scheduler = Scheduler(owner)
	sorted_tasks = scheduler.sort_by_time()

	assert [task.time for task in sorted_tasks] == ["08:00", "12:00", "18:00"]


def test_daily_task_completion_creates_next_occurrence() -> None:
	task = Task(description="Feed", time="07:00", frequency="daily")

	next_task = task.mark_complete()

	assert task.completed is True
	assert next_task is not None
	assert next_task.completed is False
	assert next_task.due_date == task.due_date + timedelta(days=1)


def test_detect_conflicts_flags_duplicate_times() -> None:
	owner = Owner("Jasmine")
	pet_one = Pet(name="Fenrir", species="dog")
	pet_two = Pet(name="Luna", species="cat")
	owner.add_pet(pet_one)
	owner.add_pet(pet_two)

	pet_one.add_task(Task(description="Walk", time="09:00"))
	pet_two.add_task(Task(description="Feed", time="09:00"))

	scheduler = Scheduler(owner)
	conflicts = scheduler.detect_conflicts()

	assert len(conflicts) == 1
	assert "09:00" in conflicts[0]


def test_once_task_mark_complete_returns_none() -> None:
	task = Task(description="Vet visit", time="10:00", frequency="once")

	next_task = task.mark_complete()

	assert next_task is None


def test_weekly_task_completion_creates_next_occurrence() -> None:
	task = Task(description="Bath time", time="11:00", frequency="weekly")

	next_task = task.mark_complete()

	assert next_task is not None
	assert next_task.completed is False
	assert next_task.due_date == task.due_date + timedelta(days=7)


def test_recurring_task_preserves_priority_and_duration() -> None:
	task = Task(description="Feed", time="07:00", frequency="daily",
				duration_minutes=10, priority="high")

	next_task = task.mark_complete()

	assert next_task is not None
	assert next_task.duration_minutes == 10
	assert next_task.priority == "high"


def test_duplicate_pet_name_raises_error() -> None:
	owner = Owner("Jasmine")
	owner.add_pet(Pet(name="Fenrir", species="dog"))

	with pytest.raises(ValueError, match="Fenrir"):
		owner.add_pet(Pet(name="Fenrir", species="cat"))


def test_sort_by_time_empty_owner_returns_empty_list() -> None:
	owner = Owner("Jasmine")
	scheduler = Scheduler(owner)

	assert scheduler.sort_by_time() == []


def test_invalid_time_format_raises_error() -> None:
	with pytest.raises(ValueError):
		Task(description="Walk", time="9:00")


def test_no_conflicts_when_tasks_at_different_times() -> None:
	owner = Owner("Jasmine")
	pet = Pet(name="Fenrir", species="dog")
	owner.add_pet(pet)
	pet.add_task(Task(description="Morning walk", time="08:00"))
	pet.add_task(Task(description="Evening walk", time="18:00"))

	scheduler = Scheduler(owner)

	assert scheduler.detect_conflicts() == []


def test_sort_by_priority_then_time_orders_high_before_low() -> None:
	owner = Owner("Jasmine")
	pet = Pet(name="Fenrir", species="dog")
	owner.add_pet(pet)
	pet.add_task(Task(description="Low priority walk", time="08:00", priority="low"))
	pet.add_task(Task(description="High priority meds", time="10:00", priority="high"))
	pet.add_task(Task(description="High priority feed", time="09:00", priority="high"))

	scheduler = Scheduler(owner)
	sorted_tasks = scheduler.sort_by_priority_then_time()

	assert [task.description for task in sorted_tasks] == [
		"High priority feed",
		"High priority meds",
		"Low priority walk",
	]


def test_find_next_available_slot_returns_first_gap() -> None:
	owner = Owner("Jasmine")
	pet = Pet(name="Fenrir", species="dog")
	owner.add_pet(pet)
	pet.add_task(Task(description="Breakfast", time="08:00", duration_minutes=30))
	pet.add_task(Task(description="Walk", time="09:00", duration_minutes=30))

	scheduler = Scheduler(owner)
	next_slot = scheduler.find_next_available_slot(
		duration_minutes=30,
		earliest_time="08:00",
		latest_time="10:00",
		search_days=1,
	)

	assert next_slot is not None
	assert next_slot[1] == "08:30"


def test_find_next_available_slot_returns_none_when_window_is_full() -> None:
	owner = Owner("Jasmine")
	pet = Pet(name="Fenrir", species="dog")
	owner.add_pet(pet)
	pet.add_task(Task(description="Breakfast", time="08:00", duration_minutes=60))
	pet.add_task(Task(description="Walk", time="09:00", duration_minutes=60))

	scheduler = Scheduler(owner)
	next_slot = scheduler.find_next_available_slot(
		duration_minutes=30,
		earliest_time="08:00",
		latest_time="10:00",
		search_days=1,
	)

	assert next_slot is None


def test_save_and_load_preserves_owner_pet_and_task_data(tmp_path) -> None:
	file_path = tmp_path / "owner_data.json"
	owner = Owner("Jasmine")
	pet = Pet(name="Fenrir", species="dog")
	owner.add_pet(pet)
	pet.add_task(
		Task(
			description="Evening walk",
			time="18:00",
			frequency="daily",
			duration_minutes=30,
			priority="high",
		)
	)

	owner.save_to_json(str(file_path))
	loaded_owner = Owner.load_from_json(str(file_path))
	loaded_pet = loaded_owner.get_pet_by_name("Fenrir")

	assert loaded_owner.name == "Jasmine"
	assert loaded_pet is not None
	assert len(loaded_pet.tasks) == 1
	assert loaded_pet.tasks[0].description == "Evening walk"
	assert loaded_pet.tasks[0].duration_minutes == 30
	assert loaded_pet.tasks[0].priority == "high"


def test_load_from_missing_file_returns_default_owner(tmp_path) -> None:
	missing_file = tmp_path / "missing_data.json"
	loaded_owner = Owner.load_from_json(str(missing_file), default_name="Jasmine")

	assert loaded_owner.name == "Jasmine"
	assert loaded_owner.pets == []


def test_set_name_reuses_owner_validation() -> None:
	owner = Owner("Jasmine")
	owner.set_name("  <b>Casey</b>  ")

	assert owner.name == "Casey"


def test_load_from_corrupted_file_returns_empty_owner_with_warning(tmp_path) -> None:
	file_path = tmp_path / "corrupted.json"
	file_path.write_text("{not valid json", encoding="utf-8")

	loaded_owner = Owner.load_from_json(str(file_path), default_name="Jasmine")

	assert loaded_owner.name == "Jasmine"
	assert loaded_owner.pets == []
	assert loaded_owner.last_load_warning is not None
	assert "corrupted.json" in loaded_owner.last_load_warning
