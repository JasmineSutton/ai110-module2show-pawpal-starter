# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- I included the following classes with the following responsibilities:

 `Owner` holds a list of pets and serves as the entry point for all data. `Pet` holds a list of tasks and is responsible for adding them. `Task` is a pure data object representing a single care action, with a time, frequency, and completion state. `Scheduler` takes an `Owner` and provides sorting, filtering, and conflict detection across all pets and tasks. The three user-facing capabilities mapped directly to these classes: adding a pet goes through `Owner.add_pet()`, scheduling a walk goes through `Pet.add_task()`, and seeing today's tasks goes through `Scheduler.print_schedule()`.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, the design changed during implementation. The original Task class did not include `duration_minutes` or `priority` fields, but the Streamlit UI was already collecting both from the user. Once this gap was identified, both fields were added to the Task dataclass with validation, and `mark_complete()` was updated to carry them forward into recurring task instances. A duplicate-pet-name guard was also added to `Owner.add_pet()` after realizing that `get_pet_by_name()` would silently return the wrong pet if two pets shared a name.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers time (HH:MM), due date, frequency (once/daily/weekly), priority (low/medium/high), and duration in minutes. Time and due date were prioritized first because a working sort and today-only filter were the minimum needed to show a usable daily schedule. Priority and duration were added next so the backend could eventually be extended to rank or fit tasks into available windows.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

- Tradeoff: conflict detection checks exact date/time matches, not duration overlaps.
- Why this is reasonable: the model stores point-in-time tasks, so exact-match checks are simple, understandable, and useful at this stage.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

AI was used throughout: for design brainstorming (generating the initial UML class diagram), reviewing the code for missing relationships and logic bottlenecks, planning persistence and advanced scheduling changes in Agent Mode, refactoring suggestions (such as adding `get_todays_tasks()`, `sort_by_priority_then_time()`, and `find_next_available_slot()`), and verifying that all checklist steps were complete. The most useful prompts were specific and structural — for example, asking "do you see any missing relationships or potential logic bottlenecks?" or giving Agent Mode a concrete implementation goal for JSON persistence produced an actionable plan rather than a vague suggestion.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

When AI flagged that `get_all_tasks()` rebuilds from scratch on every call as a performance bottleneck, the suggestion to add caching was not adopted. For a scheduler managing at most 20 pets × 50 tasks (1,000 items), the overhead is negligible and caching would add complexity and a potential staleness bug. The decision was verified by reading the constant definitions (`MAX_PETS_PER_OWNER = 20`, `MAX_TASKS_PER_PET = 50`) and confirming the data size never justifies the added complexity.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

Seventeen behaviors were tested across the final system. These included task completion, task addition, chronological sorting, priority-first sorting, daily recurrence, weekly recurrence, recurrence preserving duration and priority, exact-match conflict detection, no-conflict cases, duplicate pet name protection, invalid time validation, empty schedules, JSON save/load behavior, missing-file handling, and the new next-available-slot algorithm in both success and no-gap scenarios. These tests were important because the project now has more than simple task storage: it includes recurrence rules, persistence, scheduling heuristics, and user-facing safety checks that could fail silently without automated coverage.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

Confidence level: 4/5. All 17 tests are passing, including the new persistence and advanced scheduling behaviors. The edge cases I would test next are partially overlapping tasks with different durations, corrupted `data.json` contents, owner-name edits that include invalid characters after initial creation, and next-available-slot searches that need to skip more than seven days.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The Owner → Pet → Task hierarchy came together cleanly. Each class has a single responsibility, data flows in one direction, and the Scheduler never reaches past the Owner into Pet or Task internals directly. The recurring task pattern (`mark_complete()` returning the next instance) is also a design detail that works well — it keeps Task self-contained rather than requiring the Scheduler to know recurrence rules.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

The `mark_complete()` pattern requires the caller to manually re-attach the returned task to a pet. This works in `main.py` and the Streamlit UI, but it is easy to call `mark_complete()` and forget to add the result, silently breaking the recurrence chain. In a next iteration, the Scheduler would own a `complete_task(task, pet)` method that handles both steps atomically so the caller cannot forget.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Designing the class structure before writing logic made the implementation straightforward — when the UML relationships were clear, each method had an obvious home and the code followed naturally. Working with AI reinforced that the most useful prompts are specific and structural ("what relationships are missing?") rather than open-ended ("make this better"), because specific questions produce actionable answers that can be evaluated against the actual code.

## 6. Lead Architect Lessons

**a. Lessons learned**

- What did you learn about being the "lead architect" while collaborating with powerful AI tools?

The biggest lesson was that AI can generate many plausible code changes quickly, but it does not own the architecture. As the lead architect, I had to decide where logic belonged, which suggestions increased complexity too much, which APIs needed to stay backward compatible, and when a recommendation solved the wrong problem. For example, I kept `sort_by_time()` for compatibility, added `sort_by_priority_then_time()` as a separate method, and rejected caching because the dataset is too small to justify the added complexity.

**b. Practical takeaway**

- How did that change the way you worked with AI during the project?

It changed my prompts from broad requests into bounded engineering tasks. Instead of asking AI to "improve the scheduler," I asked it to inspect relationships, plan persistence, or identify edge cases. That made AI act more like an accelerant for specific decisions, while I stayed responsible for the system boundaries, tradeoffs, verification, and final merge choices.

## 7. Prompt Comparison

**a. Comparison task**

- Which complex algorithmic task did you choose for comparison?

The task chosen for comparison was the weekly-rescheduling and next-available-slot logic, because both require clear handling of dates, durations, and scheduling constraints.

**b. Model comparison**

- Which model provided the more modular or "Pythonic" solution, and why?

A true multi-model comparison was not completed inside this VS Code environment because only one model was available through Copilot during implementation. To avoid inventing evidence, I am not claiming results from Claude or Gemini that I did not actually run. The useful takeaway from the prompts I did run is that the more constrained prompt produced the more modular solution: it encouraged small helper methods, preserved backward compatibility, and separated persistence from scheduling logic instead of blending everything into one large method.
