import os
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

TASKS_DIR = os.path.join(Path.home(), ".todo")
TASKS_FILEPATH = os.path.join(TASKS_DIR, "tasks.json")


def get_tasks():
    """Get the tasks saved in the Json tasks file.

    :return: The tasks saved in the Json tasks file.
    :rtype: dict
    """
    if os.path.exists(TASKS_FILEPATH):
        with open(TASKS_FILEPATH, "r") as f:
            try:
                tasks = json.load(f)
            except Exception as e:
                logging.error(f"Json file corrupted : {TASKS_FILEPATH}")
                return False

            if isinstance(tasks, dict):
                return tasks
    return {}


def add_task(name):
    """Add a task to the tasks dict.

    :param name: The name of the task to add.
    :type name: str

    :return: True if the tasks are saved else False.
    :rtype: bool
    """
    tasks = get_tasks()

    if name in tasks.keys():
        logging.error("A task with the same name already exists.")
        return False

    tasks[name] = False
    _write_tasks_to_disk(tasks=tasks)
    return True


def remove_task(name):
    """Remove a task from the tasks dict.

    :param name: The name of the task to delete.
    :type name: str

    :return: True if the tasks are saved else False.
    :rtype: bool
    """
    tasks = get_tasks()

    if name not in tasks.keys():
        logging.error("The task does not exist.")
        return False

    del tasks[name]
    _write_tasks_to_disk(tasks=tasks)
    return True


def set_tasks_status(name, done=True):
    """Set the status of the tasks.

    :param name: The name of the task.
    :param done: The state of the task.
    :type name: str
    :type done: bool

    :return: True if the tasks are saved else False.
    :rtype: bool
    """
    tasks = get_tasks()

    if name not in tasks.keys():
        logging.error("The task does not exist.")
        return False

    tasks[name] = done
    _write_tasks_to_disk(tasks=tasks)
    return True


def _write_tasks_to_disk(tasks):
    """Save the tasks in a Json file.

    :param tasks: The tasks to save.
    :type tasks: dict
    """
    if not os.path.exists(TASKS_DIR):
        os.makedirs(TASKS_DIR)

    with open(TASKS_FILEPATH, "w") as f:
        json.dump(tasks, f, indent=4)
        logging.info("The tasks have been updated.")


if __name__ == '__main__':
    t = get_tasks()
    # t = add_task("Test")
    # t = set_tasks_status(name="Test")
    # t = remove_task(name="Test")
    print(t)
