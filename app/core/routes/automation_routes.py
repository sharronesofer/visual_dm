"""
Routes for managing automation, background tasks, and scheduled jobs.
"""

from flask import Blueprint, jsonify, request, current_app
from app.core.utils.scheduler_utils import SchedulerManager
from app.core.scheduler import scheduler as task_scheduler
from app.core.managers.task_manager import TaskManager, TaskPriority, TaskStatus
from datetime import datetime
from typing import Dict, Any, Optional
from flask_apispec import use_kwargs, marshal_with, doc
from marshmallow import Schema, fields
from app.core.schemas.automation import (
    JobSchema,
    TaskSchema,
    TaskSubmitSchema,
    TaskStatusSchema,
    ScheduledJobSchema,
    JobTriggerSchema,
)
from app.core.routes.monitoring import send_scheduled_monitoring_report

automation_bp = Blueprint("automation", __name__)

# Initialize managers
task_manager = TaskManager()
scheduler_manager = None


def init_automation(app):
    """Initialize automation components."""
    global scheduler_manager
    scheduler_manager = SchedulerManager(app)
    # Register daily monitoring report email job if not already present
    job_id = "daily_monitoring_report_email"
    existing_jobs = scheduler_manager.get_all_jobs()
    if job_id not in existing_jobs:
        scheduler_manager.scheduler.add_job(
            func=lambda: send_scheduled_monitoring_report(fmt="csv"),
            trigger="cron",
            id=job_id,
            hour=8,
            minute=0,
            replace_existing=True,
        )


# Register init_automation to be called after app creation
automation_bp.record_once(lambda state: init_automation(state.app))


# --- Schema Definitions ---
class JobListResponse(Schema):
    """Response schema for job listing."""

    status = fields.String(required=True)
    jobs = fields.Dict(keys=fields.String(), values=fields.Nested(JobSchema))


class TaskListResponse(Schema):
    """Response schema for task listing."""

    status = fields.String(required=True)
    tasks = fields.Dict(keys=fields.String(), values=fields.Nested(TaskSchema))


# --- Background Tasks ---
@automation_bp.route("/tasks", methods=["POST"])
@doc(
    description="Submit a new background task for execution.",
    tags=["Background Tasks"],
    params={
        "function": {"description": "Function name to execute", "required": True},
        "args": {"description": "List of positional arguments", "required": False},
        "kwargs": {"description": "Dictionary of keyword arguments", "required": False},
        "priority": {
            "description": "Task priority (critical, high, normal, low, background)",
            "required": False,
        },
        "max_retries": {
            "description": "Maximum number of retry attempts",
            "required": False,
        },
        "scheduled_for": {
            "description": "ISO datetime for scheduled execution",
            "required": False,
        },
    },
    responses={
        201: {"description": "Task created successfully"},
        400: {"description": "Invalid request parameters"},
        500: {"description": "Server error"},
    },
)
@use_kwargs(TaskSubmitSchema)
@marshal_with(TaskSchema)
def submit_task():
    """Submit a new background task."""
    data = request.get_json()

    # Convert priority string to enum
    priority_map = {
        "critical": TaskPriority.CRITICAL,
        "high": TaskPriority.HIGH,
        "normal": TaskPriority.NORMAL,
        "low": TaskPriority.LOW,
        "background": TaskPriority.BACKGROUND,
    }

    priority = priority_map.get(
        data.get("priority", "normal").lower(), TaskPriority.NORMAL
    )

    # Parse scheduled_for if provided
    scheduled_for = None
    if "scheduled_for" in data:
        scheduled_for = datetime.fromisoformat(data["scheduled_for"])

    task_id = task_manager.submit_task(
        data["function"],
        *data.get("args", []),
        priority=priority,
        max_retries=data.get("max_retries", 3),
        scheduled_for=scheduled_for,
        **data.get("kwargs", {})
    )

    return (
        jsonify(
            {
                "status": "success",
                "task_id": task_id,
                "task": task_manager.get_task(task_id),
            }
        ),
        201,
    )


@automation_bp.route("/tasks/<task_id>", methods=["GET"])
@doc(
    description="Get the status and details of a specific task.",
    tags=["Background Tasks"],
    params={"task_id": {"description": "ID of the task to retrieve", "required": True}},
    responses={
        200: {"description": "Task details retrieved successfully"},
        404: {"description": "Task not found"},
    },
)
@marshal_with(TaskSchema)
def get_task_status(task_id: str):
    """Get task status and details."""
    task = task_manager.get_task(task_id)
    if not task:
        return jsonify({"status": "error", "message": "Task not found"}), 404

    return jsonify({"status": "success", "task": task}), 200


@automation_bp.route("/tasks", methods=["GET"])
@doc(
    description="Get a list of all tasks and their statuses.",
    tags=["Background Tasks"],
    responses={200: {"description": "Tasks retrieved successfully"}},
)
@marshal_with(TaskListResponse)
def list_tasks():
    """List all tasks."""
    tasks = task_manager.get_all_tasks()
    return jsonify({"status": "success", "tasks": tasks}), 200


@automation_bp.route("/tasks/<task_id>/cancel", methods=["POST"])
@doc(
    description="Cancel a pending or running task.",
    tags=["Background Tasks"],
    params={"task_id": {"description": "ID of the task to cancel", "required": True}},
    responses={
        200: {"description": "Task cancelled successfully"},
        404: {"description": "Task not found or cannot be cancelled"},
    },
)
@marshal_with(TaskStatusSchema)
def cancel_task(task_id: str):
    """Cancel a task."""
    success = task_manager.cancel_task(task_id)
    if not success:
        return (
            jsonify(
                {"status": "error", "message": "Task not found or cannot be cancelled"}
            ),
            404,
        )

    return jsonify({"status": "success", "message": "Task cancelled successfully"}), 200


# --- Scheduled Jobs ---
@automation_bp.route("/jobs", methods=["POST"])
@doc(
    description="Add a new scheduled job.",
    tags=["Scheduled Jobs"],
    params={
        "function": {"description": "Function name to schedule", "required": True},
        "trigger": {
            "description": "Trigger type (date, interval, cron)",
            "required": True,
        },
        "trigger_args": {
            "description": "Trigger configuration arguments",
            "required": True,
            "example": {
                "date": {"run_date": "2024-03-20T15:30:00"},
                "interval": {"weeks": 1, "days": 2, "hours": 3},
                "cron": {"year": "*", "month": "*/2", "day": "1", "hour": "5"},
            },
        },
    },
    responses={
        201: {"description": "Job scheduled successfully"},
        400: {"description": "Invalid request parameters"},
    },
)
@use_kwargs(JobTriggerSchema)
@marshal_with(ScheduledJobSchema)
def add_scheduled_job():
    """Add a new scheduled job."""
    data = request.get_json()

    try:
        scheduler_manager.add_job(
            data["function"], trigger=data["trigger"], **data.get("trigger_args", {})
        )
        return jsonify({"status": "success", "message": "Job added successfully"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@automation_bp.route("/jobs/<job_id>", methods=["DELETE"])
@doc(
    description="Remove a scheduled job.",
    tags=["Scheduled Jobs"],
    params={"job_id": {"description": "ID of the job to remove", "required": True}},
    responses={
        200: {"description": "Job removed successfully"},
        404: {"description": "Job not found"},
    },
)
def remove_scheduled_job(job_id: str):
    """Remove a scheduled job."""
    try:
        scheduler_manager.remove_job(job_id)
        return (
            jsonify({"status": "success", "message": "Job removed successfully"}),
            200,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 404


@automation_bp.route("/jobs/<job_id>/pause", methods=["POST"])
@doc(
    description="Pause a scheduled job.",
    tags=["Scheduled Jobs"],
    params={"job_id": {"description": "ID of the job to pause", "required": True}},
    responses={
        200: {"description": "Job paused successfully"},
        404: {"description": "Job not found"},
    },
)
def pause_job(job_id: str):
    """Pause a scheduled job."""
    try:
        scheduler_manager.pause_job(job_id)
        return jsonify({"status": "success", "message": "Job paused successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 404


@automation_bp.route("/jobs/<job_id>/resume", methods=["POST"])
@doc(
    description="Resume a paused job.",
    tags=["Scheduled Jobs"],
    params={"job_id": {"description": "ID of the job to resume", "required": True}},
    responses={
        200: {"description": "Job resumed successfully"},
        404: {"description": "Job not found"},
    },
)
def resume_job(job_id: str):
    """Resume a paused job."""
    try:
        scheduler_manager.resume_job(job_id)
        return (
            jsonify({"status": "success", "message": "Job resumed successfully"}),
            200,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 404


@automation_bp.route("/jobs/<job_id>", methods=["GET"])
@doc(
    description="Get details of a specific scheduled job.",
    tags=["Scheduled Jobs"],
    params={"job_id": {"description": "ID of the job to retrieve", "required": True}},
    responses={
        200: {"description": "Job details retrieved successfully"},
        404: {"description": "Job not found"},
    },
)
@marshal_with(ScheduledJobSchema)
def get_job(job_id: str):
    """Get job details."""
    job = scheduler_manager.get_job(job_id)
    if not job:
        return jsonify({"status": "error", "message": "Job not found"}), 404

    return jsonify({"status": "success", "job": job}), 200


@automation_bp.route("/jobs", methods=["GET"])
@doc(
    description="Get a list of all scheduled jobs.",
    tags=["Scheduled Jobs"],
    responses={200: {"description": "Jobs retrieved successfully"}},
)
@marshal_with(JobListResponse)
def list_jobs():
    """List all jobs."""
    jobs = scheduler_manager.get_all_jobs()
    return jsonify({"status": "success", "jobs": jobs}), 200


# --- Task Scheduler ---
@automation_bp.route("/scheduler/tasks", methods=["POST"])
@doc(
    description="Add a new periodic task to the task scheduler.",
    tags=["Task Scheduler"],
    params={
        "task_id": {"description": "Unique identifier for the task", "required": True},
        "function": {"description": "Function name to schedule", "required": True},
        "schedule": {
            "description": "Schedule configuration (cron expression or interval)",
            "required": True,
            "example": {"cron": "0 */2 * * *"},  # Every 2 hours
        },
    },
    responses={
        201: {"description": "Task scheduled successfully"},
        400: {"description": "Invalid request parameters"},
        409: {"description": "Task ID already exists"},
    },
)
def add_scheduled_task():
    """Add a new scheduled task."""
    data = request.get_json()

    success = task_scheduler.add_task(
        data["task_id"],
        data["function"],
        data["interval"],
        *data.get("args", []),
        **data.get("kwargs", {})
    )

    if not success:
        return jsonify({"status": "error", "message": "Task already exists"}), 400

    return jsonify({"status": "success", "message": "Task added successfully"}), 201


@automation_bp.route("/scheduler/tasks/<task_id>", methods=["DELETE"])
@doc(
    description="Remove a task from the task scheduler.",
    tags=["Task Scheduler"],
    params={"task_id": {"description": "ID of the task to remove", "required": True}},
    responses={
        200: {"description": "Task removed successfully"},
        404: {"description": "Task not found"},
    },
)
def remove_scheduled_task(task_id: str):
    """Remove a scheduled task."""
    success = task_scheduler.remove_task(task_id)
    if not success:
        return jsonify({"status": "error", "message": "Task not found"}), 404

    return jsonify({"status": "success", "message": "Task removed successfully"}), 200


@automation_bp.route("/scheduler/tasks/<task_id>/enable", methods=["POST"])
@doc(
    description="Enable a scheduled task.",
    tags=["Task Scheduler"],
    params={"task_id": {"description": "ID of the task to enable", "required": True}},
    responses={
        200: {"description": "Task enabled successfully"},
        404: {"description": "Task not found"},
    },
)
def enable_task(task_id: str):
    """Enable a scheduled task."""
    success = task_scheduler.enable_task(task_id)
    if not success:
        return jsonify({"status": "error", "message": "Task not found"}), 404

    return jsonify({"status": "success", "message": "Task enabled successfully"}), 200


@automation_bp.route("/scheduler/tasks/<task_id>/disable", methods=["POST"])
@doc(
    description="Disable a scheduled task.",
    tags=["Task Scheduler"],
    params={"task_id": {"description": "ID of the task to disable", "required": True}},
    responses={
        200: {"description": "Task disabled successfully"},
        404: {"description": "Task not found"},
    },
)
def disable_task(task_id: str):
    """Disable a scheduled task."""
    success = task_scheduler.disable_task(task_id)
    if not success:
        return jsonify({"status": "error", "message": "Task not found"}), 404

    return jsonify({"status": "success", "message": "Task disabled successfully"}), 200
