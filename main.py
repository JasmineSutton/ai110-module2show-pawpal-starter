from pawpal_system import Owner, Pet, Scheduler, Task


#ADDITION: Built required sample flow for one owner, two pets, and at least three tasks.
def build_demo() -> None:
	owner = Owner("Jordan")

	pet_one = Pet("Mochi", "dog")
	pet_two = Pet("Luna", "cat")
	owner.add_pet(pet_one)
	owner.add_pet(pet_two)

	pet_one.add_task(Task(description="Morning walk", time="08:00", frequency="daily"))
	pet_two.add_task(Task(description="Feed Luna", time="12:30", frequency="daily"))
	pet_one.add_task(Task(description="Evening walk", time="18:00", frequency="daily"))

	scheduler = Scheduler(owner)

	print(scheduler.print_schedule())


if __name__ == "__main__":
	build_demo()
