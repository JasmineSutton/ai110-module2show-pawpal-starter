# PawPal+

PawPal+ is a Streamlit-based pet care scheduling application built around four core classes: `Owner`, `Pet`, `Task`, and `Scheduler`. The project supports task creation, recurrence, conflict detection, and daily schedule generation, and I used it to tighten backend validation, state handling, and local persistence so the scheduler behaves predictably under bad or edge-case input.

## What I changed

- implemented backend validation for names, times, species, priorities, frequencies, and durations
- added cleaner trust boundaries between the UI and the model layer
- hardened local JSON persistence with atomic writes and corrupted-file handling
- bounded resource usage with caps on pets, tasks, and field lengths
- added tests for scheduling behavior, recurrence, validation reuse, and persistence

## Security focus

The main hardening work in this project focused on:

- preventing malformed input from reaching scheduling logic
- preventing UI-driven updates from bypassing backend validation
- avoiding unbounded in-memory growth
- handling corrupted persisted data safely

## Repo contents

- `app.py` - Streamlit interface
- `pawpal_system.py` - backend model and scheduling logic
- `tests/test_pawpal.py` - automated tests
- `SECURITY_README.md` - detailed security hardening writeup
- case study document - summary of the hardening work

## Running the project

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m streamlit run app.py
```

## Running the tests

```bash
python -m pytest -q
```

## Notes

This project started as a scheduling app, but I used it to apply more disciplined backend validation, safer persistence behavior, and clearer model-layer trust boundaries than the starter version had.
