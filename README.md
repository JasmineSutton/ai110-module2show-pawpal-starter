# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

- `Scheduler.sort_by_time()` orders tasks by date and time.
- `Scheduler.filter_tasks()` supports filtering by completion state and pet name.
- `Scheduler.detect_conflicts()` returns warnings for tasks that share the same date/time.
- `Task.mark_complete()` creates the next task instance for daily and weekly tasks.

## Testing PawPal+

Run tests with:

```bash
python -m pytest
```

Current tests cover:

- Task completion updates status and recurrence behavior.
- Adding a task increases a pet's task count.
- Tasks are sorted chronologically.
- Duplicate times are flagged as conflicts.

## Confidence Level

4/5

## Features

- Sorting by time
- Conflict warnings
- Daily/weekly recurrence
- Filtering by completion status or pet name

## Updated UML

```mermaid
classDiagram
	class Owner {
		+name: str
		+pets: List~Pet~
		+add_pet(pet)
		+get_pet_by_name(pet_name)
		+get_all_tasks()
	}

	class Pet {
		+name: str
		+species: str
		+tasks: List~Task~
		+add_task(task)
	}

	class Task {
		+description: str
		+time: str
		+frequency: str
		+completed: bool
		+pet_name: str
		+due_date: date
		+mark_complete()
	}

	class Scheduler {
		+owner: Owner
		+get_all_tasks()
		+print_schedule()
		+sort_by_time()
		+filter_tasks(completed, pet_name)
		+detect_conflicts()
	}

	Owner "1" --> "many" Pet
	Pet "1" --> "many" Task
	Scheduler "1" --> "1" Owner
```

## Demo

Add your final Streamlit screenshot here after manual browser verification.
