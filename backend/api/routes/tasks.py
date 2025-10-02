"""
Tasks API Routes
Endpoints for checking async task status
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from workers.celery_app import celery_app

router = APIRouter()


@router.get("/{task_id}", summary="Get task status")
async def get_task_status(task_id: str):
    """
    Get the status of an async task
    
    **States:**
    - PENDING: Task is waiting to be executed
    - PROGRESS: Task is currently running
    - SUCCESS: Task completed successfully
    - FAILURE: Task failed with an error
    - REVOKED: Task was cancelled
    """
    task = celery_app.AsyncResult(task_id)
    
    response = {
        "classification": "UNCLASSIFIED",
        "task_id": task_id,
        "state": task.state,
        "ready": task.ready(),
    }
    
    if task.state == "PENDING":
        response["status"] = "Task is pending execution"
    
    elif task.state == "PROGRESS":
        response["status"] = "Task is running"
        response["meta"] = task.info
    
    elif task.state == "SUCCESS":
        response["status"] = "Task completed successfully"
        response["result"] = task.result
    
    elif task.state == "FAILURE":
        response["status"] = "Task failed"
        response["error"] = str(task.info)
    
    else:
        response["status"] = f"Task state: {task.state}"
        if task.info:
            response["meta"] = task.info
    
    return response


@router.delete("/{task_id}", summary="Cancel task")
async def cancel_task(task_id: str):
    """
    Cancel a running task
    """
    task = celery_app.AsyncResult(task_id)
    
    if task.state in ["PENDING", "PROGRESS"]:
        task.revoke(terminate=True)
        return {
            "classification": "UNCLASSIFIED",
            "task_id": task_id,
            "status": "cancelled",
            "message": "Task cancellation requested"
        }
    else:
        return {
            "classification": "UNCLASSIFIED",
            "task_id": task_id,
            "status": "not_cancelled",
            "message": f"Task is in {task.state} state and cannot be cancelled"
        }


@router.get("/", summary="List recent tasks")
async def list_tasks(limit: int = 10):
    """
    List recent tasks (requires Celery events or result backend inspection)
    
    Note: This is a simplified implementation
    """
    return {
        "classification": "UNCLASSIFIED",
        "message": "Task listing requires Celery events monitoring",
        "note": "Use specific task IDs to check status"
    }
