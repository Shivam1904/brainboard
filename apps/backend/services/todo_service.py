"""
Todo Widget Service
Business logic for todo task management
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import logging

from models.database_models import TodoTask, DashboardWidget
from models.schemas.todo_schemas import TaskFrequency, TaskPriority, TodoWidgetStatsResponse

logger = logging.getLogger(__name__)

class TodoService:
    """Service for todo widget business logic"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def should_show_task_today(self, task: TodoTask, target_date: Optional[date] = None) -> bool:
        """
        Determine if a task should appear today based on its frequency
        
        Args:
            task: TodoTask object
            target_date: Target date (defaults to today)
            
        Returns:
            Boolean indicating if task should be shown
        """
        if target_date is None:
            target_date = date.today()
        
        # For one-time tasks
        if task.frequency == TaskFrequency.ONCE:
            if not task.is_done:
                if task.due_date is None:
                    return True
                return task.due_date <= target_date
            return False
        
        # For recurring tasks
        if not task.is_recurring:
            return not task.is_done
        
        # Daily tasks always show (unless completed today)
        if task.frequency == TaskFrequency.DAILY:
            if task.last_completed_date == target_date:
                return False  # Already completed today
            return True
        
        # Weekly tasks - show every 7 days
        if task.frequency == TaskFrequency.WEEKLY:
            days_since_creation = (target_date - task.created_at.date()).days
            if task.last_completed_date:
                days_since_completion = (target_date - task.last_completed_date).days
                return days_since_completion >= 7
            return days_since_creation % 7 == 0
        
        # Monthly tasks - show every 30 days
        if task.frequency == TaskFrequency.MONTHLY:
            days_since_creation = (target_date - task.created_at.date()).days
            if task.last_completed_date:
                days_since_completion = (target_date - task.last_completed_date).days
                return days_since_completion >= 30
            return days_since_creation % 30 == 0
        
        return True
    
    def get_today_tasks(self, widget_id: str, target_date: Optional[date] = None) -> List[TodoTask]:
        """
        Get tasks that should appear today for a widget
        
        Args:
            widget_id: Widget ID
            target_date: Target date (defaults to today)
            
        Returns:
            List of TodoTask objects that should be shown today
        """
        if target_date is None:
            target_date = date.today()
        
        # Get all tasks for this widget
        all_tasks = self.db.query(TodoTask).filter(
            TodoTask.dashboard_widget_id == widget_id
        ).all()
        
        # Filter tasks based on frequency logic
        today_tasks = []
        for task in all_tasks:
            if self.should_show_task_today(task, target_date):
                today_tasks.append(task)
        
        # Sort by priority (high to low), then by due date, then by creation time
        today_tasks.sort(key=lambda t: (
            -(t.priority or 3),  # Higher priority first
            t.due_date or date.max,  # Earlier due dates first
            t.created_at
        ))
        
        return today_tasks
    
    def calculate_stats(self, tasks: List[TodoTask]) -> TodoWidgetStatsResponse:
        """
        Calculate statistics for a list of tasks
        
        Args:
            tasks: List of TodoTask objects
            
        Returns:
            TodoWidgetStatsResponse with calculated statistics
        """
        total_tasks = len(tasks)
        completed_tasks = sum(1 for task in tasks if task.is_done)
        pending_tasks = total_tasks - completed_tasks
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Group by priority
        tasks_by_priority = {}
        for priority in [1, 2, 3, 4, 5]:
            tasks_by_priority[str(priority)] = sum(1 for t in tasks if (t.priority or 3) == priority)
        
        # Group by category
        tasks_by_category = {}
        for task in tasks:
            category = task.category or "uncategorized"
            tasks_by_category[category] = tasks_by_category.get(category, 0) + 1
        
        return TodoWidgetStatsResponse(
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            pending_tasks=pending_tasks,
            completion_rate=completion_rate,
            tasks_by_priority=tasks_by_priority,
            tasks_by_category=tasks_by_category
        )
    
    def mark_task_complete(self, task: TodoTask, is_done: bool) -> TodoTask:
        """
        Mark a task as complete or incomplete with proper tracking
        
        Args:
            task: TodoTask object to update
            is_done: New completion status
            
        Returns:
            Updated TodoTask object
        """
        old_status = task.is_done
        task.is_done = is_done
        
        # Update completion tracking
        if not old_status and is_done:
            task.last_completed_date = date.today()
            logger.info(f"Task {task.id} marked complete on {date.today()}")
        elif old_status and not is_done:
            # If unchecking, we keep the last_completed_date for tracking
            pass
        
        task.updated_at = datetime.utcnow()
        return task
