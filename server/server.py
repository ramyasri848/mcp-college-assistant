import json
from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
TASKS_DIR = BASE_DIR / "tasks"

DEPARTMENTS_FILE = DATA_DIR / "departments.json"
COURSES_FILE = DATA_DIR / "courses.json"
FAQ_FILE = DATA_DIR / "faqs.json"
TASKS_FILE = TASKS_DIR / "tasks.json"


mcp = FastMCP("College Assistant")


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


@mcp.resource("college://departments")
def get_departments():
    departments = load_json(DEPARTMENTS_FILE)

    return json.dumps(
        departments,
        indent=4
    )


@mcp.resource("college://departments/{department}")
def get_department(department: str):
    departments = load_json(DEPARTMENTS_FILE)

    department = department.upper()

    if department not in departments:
        return f"Department {department} was not found."

    return json.dumps(
        departments[department],
        indent=4
    )


@mcp.resource("college://courses/{department}")
def get_courses(department: str):
    courses = load_json(COURSES_FILE)

    department = department.upper()

    if department not in courses:
        return f"No courses found for {department}."

    return json.dumps(
        courses[department],
        indent=4
    )


@mcp.resource("college://faqs")
def get_faqs():
    faqs = load_json(FAQ_FILE)

    return json.dumps(
        faqs,
        indent=4
    )


@mcp.tool()
def create_task(title: str, due_date: str):
    tasks = load_json(TASKS_FILE)

    task = {
        "id": len(tasks) + 1,
        "title": title,
        "due_date": due_date,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }

    tasks.append(task)

    save_json(TASKS_FILE, tasks)

    return {
        "success": True,
        "message": "Task created successfully.",
        "task": task
    }


@mcp.tool()
def list_tasks():
    tasks = load_json(TASKS_FILE)

    return {
        "success": True,
        "tasks": tasks
    }


@mcp.tool()
def complete_task(task_id: int):
    tasks = load_json(TASKS_FILE)

    for task in tasks:
        if task["id"] == task_id:
            task["status"] = "completed"

            save_json(TASKS_FILE, tasks)

            return {
                "success": True,
                "message": "Task completed successfully.",
                "task": task
            }

    return {
        "success": False,
        "message": f"Task {task_id} was not found."
    }


@mcp.tool()
def delete_task(task_id: int):
    tasks = load_json(TASKS_FILE)

    original_length = len(tasks)

    tasks = [
        task for task in tasks
        if task["id"] != task_id
    ]

    if len(tasks) == original_length:
        return {
            "success": False,
            "message": f"Task {task_id} was not found."
        }

    save_json(TASKS_FILE, tasks)

    return {
        "success": True,
        "message": "Task deleted successfully."
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")