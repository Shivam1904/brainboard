"""
AI Dashboard Generation Logic
Simple frequency-based widget selection for daily dashboard generation
"""

import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from models.database_models import DashboardWidget, User
import random

logger = logging.getLogger(__name__)

class DashboardAI:
    """AI service for generating daily dashboard configurations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_daily_dashboard(self, user_id: str, target_date: date = None) -> List[DashboardWidget]:
        """
        Generate today's dashboard based on user's widget preferences and frequency settings
        
        Args:
            user_id: User identifier
            target_date: Date to generate dashboard for (defaults to today)
            
        Returns:
            List of dashboard widgets that should be shown today
        """
        if target_date is None:
            target_date = date.today()
            
        logger.info(f"Generating dashboard for user {user_id} on {target_date}")
        
        # Get user's active widgets
        active_widgets = self.db.query(DashboardWidget).filter(
            DashboardWidget.user_id == user_id,
            DashboardWidget.is_active == True
        ).all()
        
        if not active_widgets:
            logger.warning(f"No active widgets found for user {user_id}")
            return []
        
        # Filter widgets based on frequency and last shown date
        eligible_widgets = []
        for widget in active_widgets:
            if self.should_include_widget(widget, target_date):
                eligible_widgets.append(widget)
        
        # Simple selection logic (for now, include all eligible widgets)
        # Future enhancement: Consider importance, user patterns, bandwidth
        selected_widgets = self._select_widgets(eligible_widgets, target_date)
        
        # Update last_shown_date for selected widgets
        self._update_widget_last_shown(selected_widgets, target_date)
        
        logger.info(f"Selected {len(selected_widgets)} widgets for dashboard")
        return selected_widgets
    
    def should_include_widget(self, widget: DashboardWidget, target_date: date) -> bool:
        """
        Determine if a widget should be included based on frequency and last shown date
        
        Args:
            widget: DashboardWidget instance
            target_date: Date to check against
            
        Returns:
            Boolean indicating if widget should be included
        """
        if not widget.is_active:
            return False
        
        last_shown = widget.last_shown_date
        
        # If never shown, include it
        if last_shown is None:
            return True
        
        # Calculate days since last shown
        days_since_shown = (target_date - last_shown).days
        
        # Frequency-based logic
        if widget.frequency == "daily":
            # Show daily widgets if not shown today or if it's the same day
            return days_since_shown >= 0  # Changed from > 0 to >= 0
        elif widget.frequency == "weekly":
            # Show weekly widgets if not shown in the last 7 days
            return days_since_shown >= 7
        elif widget.frequency == "monthly":
            # Show monthly widgets if not shown in the last 30 days
            return days_since_shown >= 30
        else:
            # Unknown frequency, default to daily behavior
            logger.warning(f"Unknown frequency '{widget.frequency}' for widget {widget.id}")
            return days_since_shown >= 0  # Changed from > 0 to >= 0
    
    def _select_widgets(self, eligible_widgets: List[DashboardWidget], target_date: date) -> List[DashboardWidget]:
        """
        Select which eligible widgets to show (simple logic for now)
        
        Args:
            eligible_widgets: List of widgets that meet frequency criteria
            target_date: Target date for dashboard
            
        Returns:
            List of selected widgets
        """
        # Deduplicate todo and habit widgets - only keep one of each type
        deduplicated_widgets = []
        seen_types = set()
        
        # Sort by importance (if available) and creation date
        sorted_widgets = sorted(
            eligible_widgets,
            key=lambda w: (w.importance or 3, w.created_at),  # Default importance = 3
            reverse=True  # Higher importance first
        )
        
        for widget in sorted_widgets:
            # For todo and habit widgets, only include the first one (highest importance)
            if widget.widget_type in ["todo", "habittracker"]:
                if widget.widget_type not in seen_types:
                    deduplicated_widgets.append(widget)
                    seen_types.add(widget.widget_type)
            else:
                # For other widget types, include all (multiple websearch, alarm, etc. are allowed)
                deduplicated_widgets.append(widget)
        
        selected = deduplicated_widgets
        
        logger.info(f"Selected {len(selected)} widgets after deduplication (todo/habit widgets consolidated)")
        
        # Limit to reasonable number of widgets (max 8 for now)
        max_widgets = 8
        if len(selected) > max_widgets:
            # Keep highest importance widgets and add some randomness
            high_importance = [w for w in selected if (w.importance or 3) >= 4]
            medium_importance = [w for w in selected if (w.importance or 3) == 3]
            low_importance = [w for w in selected if (w.importance or 3) < 3]
            
            selected = high_importance[:4]  # Always include high importance
            
            # Add some medium importance randomly
            if len(selected) < max_widgets and medium_importance:
                remaining_slots = max_widgets - len(selected)
                selected.extend(random.sample(
                    medium_importance, 
                    min(remaining_slots, len(medium_importance))
                ))
            
            # Fill remaining with low importance if needed
            if len(selected) < max_widgets and low_importance:
                remaining_slots = max_widgets - len(selected)
                selected.extend(random.sample(
                    low_importance, 
                    min(remaining_slots, len(low_importance))
                ))
        
        return selected
    
    def _update_widget_last_shown(self, widgets: List[DashboardWidget], shown_date: date):
        """Update last_shown_date for selected widgets"""
        try:
            for widget in widgets:
                widget.last_shown_date = shown_date
            self.db.commit()
            logger.info(f"Updated last_shown_date for {len(widgets)} widgets")
        except Exception as e:
            logger.error(f"Failed to update widget last_shown_date: {e}")
            self.db.rollback()
    
    def get_dashboard_stats(self, user_id: str) -> Dict[str, Any]:
        """Get dashboard statistics for user"""
        try:
            total_widgets = self.db.query(DashboardWidget).filter(
                DashboardWidget.user_id == user_id
            ).count()
            
            active_widgets = self.db.query(DashboardWidget).filter(
                DashboardWidget.user_id == user_id,
                DashboardWidget.is_active == True
            ).count()
            
            today_widgets = len(self.generate_daily_dashboard(user_id))
            
            return {
                "total_widgets": total_widgets,
                "active_widgets": active_widgets,
                "today_widgets": today_widgets,
                "generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get dashboard stats: {e}")
            return {
                "total_widgets": 0,
                "active_widgets": 0,
                "today_widgets": 0,
                "error": str(e)
            }
