# PawPal+ Security Notes

This document summarizes the security controls that were added to PawPal+ during development. These protections were not part of the original starter baseline; they were implemented as hardening work across the backend, UI, and local persistence flow.

Scope note: this is a local demo app, not a deployed service. The goal here was to handle input safely, keep local persistence predictable, and avoid obvious failure modes or data corruption during normal use.

---

## Security Posture Summary

The project now has a solid set of added security controls:

- Input is sanitized and validated at the backend boundary
- Task and pet counts are capped so in-memory growth cannot run wild
- Time, frequency, species, and priority all use allowlist validation
- The UI catches validation failures and shows readable error messages instead of raw tracebacks
- Owner, pet, and task data is saved locally in `data.json`
- JSON writes are now atomic, which lowers the chance of partially written save files
- Corrupted JSON is handled gracefully and surfaced to the user as a warning

---

## Implemented Controls Added During Development

### 1. Backend Input Validation

The backend in `pawpal_system.py` validates data at object construction time:

- `_sanitize()` strips whitespace, enforces maximum length, and removes HTML-like tags
- `_validate_time()` enforces strict `HH:MM` 24-hour format
- `Task.__post_init__()` validates description, time, pet name, frequency, duration, and priority
- `Pet.__post_init__()` validates pet name and species
- `Owner.__init__()` validates owner name
- `Owner.set_name()` now reuses that same validation path when the UI updates the owner name after initial load

Why this matters:

- Bad or malformed values are rejected before they can affect sorting, recurrence, persistence, or display
- The UI is not the only trust boundary here, since CLI code, tests, and JSON reloads also pass through backend validation

### 2. Resource Limits

The following limits are enforced in `pawpal_system.py`:

- `MAX_NAME_LENGTH = 100`
- `MAX_DESCRIPTION_LENGTH = 200`
- `MAX_TASKS_PER_PET = 50`
- `MAX_PETS_PER_OWNER = 20`

Why this matters:

- These limits prevent unbounded growth in a local in-memory app
- They also keep scheduling behavior like sorting, filtering, and conflict detection more predictable

### 3. UI-Side Safety and Error Handling

The Streamlit app in `app.py` reinforces the backend rules:

- `max_chars` is applied to owner name, pet name, task title, and time fields
- Task creation is wrapped in `try/except ValueError` so invalid input shows up as `st.error(...)` instead of a raw traceback
- The app uses sanitized model values in success messages and table output
- The app now shows a warning if persisted JSON could not be loaded cleanly

Why this matters:

- Users get immediate feedback instead of the app just blowing up
- The app stays usable even when invalid input is submitted
- Internal implementation details are less likely to leak through unhandled exceptions

### 4. Local JSON Persistence Hardening

Persistence is handled in `Owner.save_to_json()` and `Owner.load_from_json()`.

Hardening changes added for local persistence:

- `save_to_json()` now writes to a temporary file and then replaces the real file atomically
- `load_from_json()` catches corrupted or unreadable JSON and returns an empty owner instead of crashing
- When a load fails, `Owner.last_load_warning` is set so the UI can tell the user their saved data was ignored

Why this matters:

- Atomic writes reduce the chance of ending up with a half-written file if a save is interrupted
- Corruption is surfaced to the user instead of silently looking like a normal empty state

---

## Security Improvements Added After Review

Two additional issues came up during a later review and were fixed on top of the earlier hardening work.

### A. Owner name updates were bypassing validation

Earlier, `app.py` assigned `owner.name` directly when the owner name changed. That skipped the same backend validation path used during `Owner.__init__()`.

Fix:

- Added `Owner.set_name()`
- Updated `app.py` to call `owner.set_name(owner_name)` instead of assigning the attribute directly

### B. JSON persistence needed safer write and load behavior

Earlier, JSON was written directly to the target file, and corrupted JSON quietly fell back to an empty owner.

Fix:

- Added atomic save behavior using a temporary file plus replace operation
- Added `last_load_warning` on `Owner` so the app can warn the user when saved data could not be loaded

---

## Reasonable Remaining Limits for a Local Demo

No extra production-grade controls are really required for this project’s stated scope, but these limits are still worth being honest about:

- Conflict detection only checks exact matching time slots, not partially overlapping durations
- The JSON file is local plain text and is not encrypted
- The app assumes a single local user and does not try to handle concurrent file writes across multiple processes
- `_sanitize()` removes HTML-like tags, but the bigger protection against rendered script content is still the app’s normal text rendering path

For a local classroom demo, I think those are reasonable tradeoffs.

---

## Test Verification

The following behaviors are covered by automated tests in `tests/test_pawpal.py`:

- Task completion
- Task addition
- Chronological sorting
- Priority-first sorting
- Daily recurrence
- Weekly recurrence
- Recurrence preserving duration and priority
- Exact-match conflict detection
- No-conflict scenarios
- Duplicate pet name rejection
- Invalid time rejection
- Empty owner schedule handling
- JSON save/load success
- Missing JSON file handling
- Owner rename validation reuse
- Corrupted JSON handling with warning state
- Next-available-slot success and no-gap cases

Current status: **19 tests pass**.

---

## Framework Mapping

The project’s controls line up reasonably well with the following ideas:

- **OWASP A03:2021 (Injection)**
  - Allowlist validation
  - Sanitization of text fields
  - Strict time parsing

- **OWASP A04:2021 (Insecure Design)**
  - Task and pet count limits
  - Graceful error handling
  - Safer file write behavior for persistence

- **NIST SP 800-53 SI-10 (Information Input Validation)**
  - Validation of names, times, frequencies, species, priorities, and durations

- **NIST SP 800-53 AC-3 (Access Enforcement / Resource Limits)**
  - Resource caps on pets and tasks
