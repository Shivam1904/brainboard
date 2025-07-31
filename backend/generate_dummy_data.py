#!/usr/bin/env python3
"""
Generate realistic dummy data for the backend by directly inserting into all tables.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import asyncio
import json
import uuid
from datetime import datetime, timedelta, date
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from models.base import Base
from models.dashboard_widget_details import DashboardWidgetDetails
from models.alarm_details import AlarmDetails
from models.daily_widget import DailyWidget
from models.alarm_item_activity import AlarmItemActivity
from models.todo_details import TodoDetails
from models.todo_item_activity import TodoItemActivity
from models.single_item_tracker_details import SingleItemTrackerDetails
from models.single_item_tracker_item_activity import SingleItemTrackerItemActivity
from models.websearch_details import WebSearchDetails
from models.websearch_item_activity import WebSearchItemActivity
from models.websearch_summary_ai_output import WebSearchSummaryAIOutput
from db.engine import DATABASE_URL

# ============================================================================
# DATA GENERATION
# ============================================================================
async def generate_dummy_data():
    """Generate realistic dummy data for all tables."""
    print("🔧 Generating dummy data for all tables...")
    
    # Create engine
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
    )
    
    # Create session factory
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    
    async with engine.begin() as conn:
        # Clear existing data
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        # ============================================================================
        # 1. GENERATE DASHBOARD_WIDGET_DETAILS (Parent table)
        # ============================================================================
        print("📊 Creating dashboard widgets...")
        dashboard_widgets = []
        
        widget_configs = [
            {
                "user_id": "user_001",
                "widget_type": "alarm",
                "frequency": "daily",
                "importance": 0.9,
                "title": "Morning Wake Up",
                "category": "Health",
                "is_permanent": True,
                "created_by": "user_001"
            },
            {
                "user_id": "user_001", 
                "widget_type": "alarm",
                "frequency": "daily",
                "importance": 0.7,
                "title": "Lunch Break",
                "category": "Work",
                "is_permanent": False,
                "created_by": "user_001"
            },
            {
                "user_id": "user_001",
                "widget_type": "alarm", 
                "frequency": "daily",
                "importance": 0.8,
                "title": "Evening Exercise",
                "category": "Health",
                "is_permanent": True,
                "created_by": "user_001"
            },
            {
                "user_id": "user_002",
                "widget_type": "alarm",
                "frequency": "daily", 
                "importance": 0.6,
                "title": "Team Standup",
                "category": "Work",
                "is_permanent": True,
                "created_by": "user_002"
            },
            {
                "user_id": "user_001",
                "widget_type": "alarm",
                "frequency": "weekly",
                "importance": 0.5,
                "title": "Weekly Review",
                "category": "Productivity",
                "is_permanent": False,
                "created_by": "user_001"
            },
            {
                "user_id": "user_001",
                "widget_type": "todo-task",
                "frequency": "daily",
                "importance": 0.8,
                "title": "Daily Tasks",
                "category": "Work",
                "is_permanent": True,
                "created_by": "user_001"
            },
            {
                "user_id": "user_001",
                "widget_type": "todo-habit",
                "frequency": "daily",
                "importance": 0.7,
                "title": "Habits Tracker",
                "category": "Health",
                "is_permanent": True,
                "created_by": "user_001"
            },
            {
                "user_id": "user_001",
                "widget_type": "todo-event",
                "frequency": "weekly",
                "importance": 0.6,
                "title": "Weekly Events",
                "category": "Productivity",
                "is_permanent": False,
                "created_by": "user_001"
            },
            {
                "user_id": "user_001",
                "widget_type": "singleitemtracker",
                "frequency": "daily",
                "importance": 0.8,
                "title": "Weight Tracker",
                "category": "Health",
                "is_permanent": True,
                "created_by": "user_001"
            },
            {
                "user_id": "user_001",
                "widget_type": "websearch",
                "frequency": "daily",
                "importance": 0.7,
                "title": "AI Trends 2024",
                "category": "Research",
                "is_permanent": False,
                "created_by": "user_001"
            },
            {
                "user_id": "user_001",
                "widget_type": "websearch",
                "frequency": "weekly",
                "importance": 0.6,
                "title": "Latest Tech News",
                "category": "Research",
                "is_permanent": False,
                "created_by": "user_001"
            },
            {
                "user_id": "user_002",
                "widget_type": "websearch",
                "frequency": "daily",
                "importance": 0.8,
                "title": "Machine Learning Papers",
                "category": "Research",
                "is_permanent": True,
                "created_by": "user_002"
            },
            {
                "user_id": "user_001",
                "widget_type": "singleitemtracker",
                "frequency": "daily",
                "importance": 0.7,
                "title": "Steps Tracker",
                "category": "Health",
                "is_permanent": True,
                "created_by": "user_001"
            },
            {
                "user_id": "user_002",
                "widget_type": "singleitemtracker",
                "frequency": "daily",
                "importance": 0.6,
                "title": "Reading Tracker",
                "category": "Productivity",
                "is_permanent": False,
                "created_by": "user_002"
            }
        ]
        
        for config in widget_configs:
            widget = DashboardWidgetDetails(**config)
            dashboard_widgets.append(widget)
            session.add(widget)
        
        await session.commit()
        print(f"✅ Created {len(dashboard_widgets)} dashboard widgets")
        
        # ============================================================================
        # 2. GENERATE ALARM_DETAILS (Child of DashboardWidgetDetails)
        # ============================================================================
        print("⏰ Creating alarm details...")
        alarm_details = []
        
        alarm_configs = [
            {
                "widget_id": dashboard_widgets[0].id,  # Morning Wake Up
                "title": "Morning Wake Up",
                "description": "Time to start the day!",
                "alarm_times": ["07:00", "07:15"],
                "target_value": "Wake up early",
                "is_snoozable": True,
                "created_by": "user_001"
            },
            {
                "widget_id": dashboard_widgets[1].id,  # Lunch Break
                "title": "Lunch Break",
                "description": "Take a break and eat lunch",
                "alarm_times": ["12:00", "12:30"],
                "target_value": "Healthy lunch",
                "is_snoozable": True,
                "created_by": "user_001"
            },
            {
                "widget_id": dashboard_widgets[2].id,  # Evening Exercise
                "title": "Evening Exercise",
                "description": "Time for your daily workout",
                "alarm_times": ["18:00", "18:30"],
                "target_value": "30 min workout",
                "is_snoozable": False,
                "created_by": "user_001"
            },
            {
                "widget_id": dashboard_widgets[3].id,  # Team Standup
                "title": "Team Standup",
                "description": "Daily team meeting",
                "alarm_times": ["09:00"],
                "target_value": "Attend meeting",
                "is_snoozable": False,
                "created_by": "user_002"
            },
            {
                "widget_id": dashboard_widgets[4].id,  # Weekly Review
                "title": "Weekly Review",
                "description": "Review weekly progress and plan next week",
                "alarm_times": ["16:00"],
                "target_value": "Complete weekly review",
                "is_snoozable": True,
                "created_by": "user_001"
            }
        ]
        
        for config in alarm_configs:
            alarm = AlarmDetails(**config)
            alarm_details.append(alarm)
            session.add(alarm)
        
        await session.commit()
        print(f"✅ Created {len(alarm_details)} alarm details")
        
        # ============================================================================
        # 3. GENERATE TODO_DETAILS (Child of DashboardWidgetDetails)
        # ============================================================================
        print("📋 Creating todo details...")
        todo_details = []
        
        today = date.today()
        todo_configs = [
            {
                "widget_id": dashboard_widgets[5].id,  # Daily Tasks
                "title": "Daily Tasks",
                "todo_type": "todo-task",
                "description": "Complete daily work tasks",
                "due_date": today,
                "created_by": "user_001"
            },
            {
                "widget_id": dashboard_widgets[6].id,  # Habits Tracker
                "title": "Habits Tracker",
                "todo_type": "todo-habit",
                "description": "Track daily habits and routines",
                "due_date": None,
                "created_by": "user_001"
            },
            {
                "widget_id": dashboard_widgets[7].id,  # Weekly Events
                "title": "Weekly Events",
                "todo_type": "todo-event",
                "description": "Track weekly events and milestones",
                "due_date": today + timedelta(days=7),
                "created_by": "user_001"
            }
        ]
        
        for config in todo_configs:
            todo = TodoDetails(**config)
            todo_details.append(todo)
            session.add(todo)
        
        await session.commit()
        print(f"✅ Created {len(todo_details)} todo details")
        
        # ============================================================================
        # 4. GENERATE SINGLEITEMTRACKER_DETAILS (Child of DashboardWidgetDetails)
        # ============================================================================
        print("📊 Creating single item tracker details...")
        tracker_details = []
        
        tracker_configs = [
            {
                "widget_id": dashboard_widgets[8].id,  # Weight Tracker
                "title": "Weight Tracker",
                "value_type": "decimal",
                "value_unit": "kg",
                "target_value": "70.0",
                "created_by": "user_001"
            },
            {
                "widget_id": dashboard_widgets[9].id,  # Steps Tracker
                "title": "Steps Tracker",
                "value_type": "number",
                "value_unit": "steps",
                "target_value": "10000",
                "created_by": "user_001"
            },
            {
                "widget_id": dashboard_widgets[10].id,  # Reading Tracker
                "title": "Reading Tracker",
                "value_type": "number",
                "value_unit": "pages",
                "target_value": "30",
                "created_by": "user_002"
            }
        ]
        
        for config in tracker_configs:
            tracker = SingleItemTrackerDetails(**config)
            tracker_details.append(tracker)
            session.add(tracker)
        
        await session.commit()
        print(f"✅ Created {len(tracker_details)} single item tracker details")
        
        # ============================================================================
        # 4. GENERATE WEBSEARCH_DETAILS (Child of DashboardWidgetDetails)
        # ============================================================================
        print("🔍 Creating websearch details...")
        websearch_details = []
        
        websearch_configs = [
            {
                "widget_id": dashboard_widgets[11].id,  # AI Trends 2024
                "title": "AI Trends 2024",
                "created_by": "user_001"
            },
            {
                "widget_id": dashboard_widgets[12].id,  # Latest Tech News
                "title": "Latest Tech News",
                "created_by": "user_001"
            },
            {
                "widget_id": dashboard_widgets[13].id,  # Machine Learning Papers
                "title": "Machine Learning Papers",
                "created_by": "user_002"
            }
        ]
        
        for config in websearch_configs:
            websearch = WebSearchDetails(**config)
            websearch_details.append(websearch)
            session.add(websearch)
        
        await session.commit()
        print(f"✅ Created {len(websearch_details)} websearch details")
        
        # ============================================================================
        # 5. GENERATE DAILY_WIDGETS (Daily widget selections)
        # ============================================================================
        print("📅 Creating daily widgets...")
        daily_widgets = []
        
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        daily_widget_configs = [
            # Today's daily widgets
            {
                "widget_ids": [dashboard_widgets[0].id],  # Morning + Lunch
                "widget_type": "alarm",
                "priority": "HIGH",
                "reasoning": "Important daily routines for health and work",
                "date": today,
                "is_active": True,
                "created_by": "user_001"
            },
            {
                "widget_ids": [dashboard_widgets[2].id],  # Evening Exercise
                "widget_type": "alarm",
                "priority": "MEDIUM",
                "reasoning": "Daily exercise routine",
                "date": today,
                "is_active": True,
                "created_by": "user_001"
            },
            {
                "widget_ids": [dashboard_widgets[5].id],  # Daily Tasks
                "widget_type": "todo-task",
                "priority": "HIGH",
                "reasoning": "Daily task management",
                "date": today,
                "is_active": True,
                "created_by": "user_001"
            },
            {
                "widget_ids": [dashboard_widgets[6].id],  # Habits
                "widget_type": "todo-habit",
                "priority": "HIGH",
                "reasoning": "Daily habit tracking",
                "date": today,
                "is_active": True,
                "created_by": "user_001"
            },
            {
                "widget_ids": [dashboard_widgets[7].id],  # Events
                "widget_type": "todo-event",
                "priority": "MEDIUM",
                "reasoning": "Weekly event tracking",
                "date": today,
                "is_active": True,
                "created_by": "user_001"
            },
            {
                "widget_ids": [dashboard_widgets[8].id],  # Weight Tracker
                "widget_type": "singleitemtracker",
                "priority": "HIGH",
                "reasoning": "Daily weight tracking for health goals",
                "date": today,
                "is_active": True,
                "created_by": "user_001"
            },
            {
                "widget_ids": [dashboard_widgets[9].id],  # Steps Tracker
                "widget_type": "singleitemtracker",
                "priority": "MEDIUM",
                "reasoning": "Daily step tracking for fitness",
                "date": today,
                "is_active": True,
                "created_by": "user_001"
            },
            {
                "widget_ids": [dashboard_widgets[11].id],  # AI Trends 2024
                "widget_type": "websearch",
                "priority": "MEDIUM",
                "reasoning": "Daily AI trends research",
                "date": today,
                "is_active": True,
                "created_by": "user_001"
            },
            {
                "widget_ids": [dashboard_widgets[13].id],  # Machine Learning Papers
                "widget_type": "websearch",
                "priority": "HIGH",
                "reasoning": "Daily ML research for academic work",
                "date": today,
                "is_active": True,
                "created_by": "user_002"
            },
            # Yesterday's daily widgets
            {
                "widget_ids": [dashboard_widgets[0].id],  # Morning + Standup
                "widget_type": "alarm",
                "priority": "HIGH",
                "reasoning": "Daily morning routine and team meeting",
                "date": yesterday,
                "is_active": True,
                "created_by": "user_001"
            },
            # Tomorrow's daily widgets
            {
                "widget_ids": [dashboard_widgets[0].id],  # Morning + Weekly Review
                "widget_type": "alarm",
                "priority": "HIGH",
                "reasoning": "Morning routine and weekly planning",
                "date": tomorrow,
                "is_active": True,
                "created_by": "user_001"
            }
        ]
        
        for config in daily_widget_configs:
            daily_widget = DailyWidget(**config)
            daily_widgets.append(daily_widget)
            session.add(daily_widget)
        
        await session.commit()
        print(f"✅ Created {len(daily_widgets)} daily widgets")
        
        # ============================================================================
        # 5. GENERATE ALARM_ITEM_ACTIVITIES (Activity tracking)
        # ============================================================================
        print("📈 Creating alarm activities...")
        alarm_activities = []
        
        activity_configs = [
            # Today's activities
            {
                "daily_widget_id": daily_widgets[0].id,  # Today's high priority group
                "widget_id": dashboard_widgets[0].id,  # Morning Wake Up
                "alarmdetails_id": alarm_details[0].id,
                "started_at": datetime.combine(today, datetime.strptime("07:00", "%H:%M").time()),
                "snoozed_at": datetime.combine(today, datetime.strptime("07:05", "%H:%M").time()),
                "snooze_until": datetime.combine(today, datetime.strptime("07:15", "%H:%M").time()),
                "snooze_count": 1,
                "created_by": "user_001"
            },
            {
                "daily_widget_id": daily_widgets[0].id,  # Today's high priority group
                "widget_id": dashboard_widgets[1].id,  # Lunch Break
                "alarmdetails_id": alarm_details[1].id,
                "started_at": datetime.combine(today, datetime.strptime("12:00", "%H:%M").time()),
                "snoozed_at": None,
                "snooze_until": None,
                "snooze_count": 0,
                "created_by": "user_001"
            },
            {
                "daily_widget_id": daily_widgets[1].id,  # Today's medium priority group
                "widget_id": dashboard_widgets[2].id,  # Evening Exercise
                "alarmdetails_id": alarm_details[2].id,
                "started_at": datetime.combine(today, datetime.strptime("18:00", "%H:%M").time()),
                "snoozed_at": None,
                "snooze_until": None,
                "snooze_count": 0,
                "created_by": "user_001"
            },
            # Yesterday's activities
            {
                "daily_widget_id": daily_widgets[3].id,  # Yesterday's group
                "widget_id": dashboard_widgets[0].id,  # Morning Wake Up
                "alarmdetails_id": alarm_details[0].id,
                "started_at": datetime.combine(yesterday, datetime.strptime("07:00", "%H:%M").time()),
                "snoozed_at": datetime.combine(yesterday, datetime.strptime("07:03", "%H:%M").time()),
                "snooze_until": datetime.combine(yesterday, datetime.strptime("07:10", "%H:%M").time()),
                "snooze_count": 2,
                "created_by": "user_001"
            },
            {
                "daily_widget_id": daily_widgets[3].id,  # Yesterday's group
                "widget_id": dashboard_widgets[3].id,  # Team Standup
                "alarmdetails_id": alarm_details[3].id,
                "started_at": datetime.combine(yesterday, datetime.strptime("09:00", "%H:%M").time()),
                "snoozed_at": None,
                "snooze_until": None,
                "snooze_count": 0,
                "created_by": "user_002"
            }
        ]
        
        for config in activity_configs:
            activity = AlarmItemActivity(**config)
            alarm_activities.append(activity)
            session.add(activity)
        
        await session.commit()
        print(f"✅ Created {len(alarm_activities)} alarm activities")
        
        # ============================================================================
        # 6. GENERATE TODO_ITEM_ACTIVITIES (Todo activity tracking)
        # ============================================================================
        print("📋 Creating todo activities...")
        todo_activities = []
        
        todo_activity_configs = [
            # Today's activities
            {
                "daily_widget_id": daily_widgets[2].id,  # Today's todo-task group
                "widget_id": dashboard_widgets[5].id,  # Daily Tasks
                "tododetails_id": todo_details[0].id,
                "status": "in progress",
                "progress": 60,
                "created_by": "user_001"
            },
            {
                "daily_widget_id": daily_widgets[3].id,  # Today's todo-habit group
                "widget_id": dashboard_widgets[6].id,  # Habits Tracker
                "tododetails_id": todo_details[1].id,
                "status": "completed",
                "progress": 100,
                "created_by": "user_001"
            },
            {
                "daily_widget_id": daily_widgets[4].id,  # Today's todo-event group
                "widget_id": dashboard_widgets[7].id,  # Weekly Events
                "tododetails_id": todo_details[2].id,
                "status": "pending",
                "progress": 0,
                "created_by": "user_001"
            }
        ]
        
        for config in todo_activity_configs:
            activity = TodoItemActivity(**config)
            todo_activities.append(activity)
            session.add(activity)
        
        await session.commit()
        print(f"✅ Created {len(todo_activities)} todo activities")
        
        # ============================================================================
        # 7. GENERATE SINGLEITEMTRACKER_ITEM_ACTIVITIES (Tracker activity tracking)
        # ============================================================================
        print("📊 Creating single item tracker activities...")
        tracker_activities = []
        
        tracker_activity_configs = [
            # Today's activities
            {
                "daily_widget_id": daily_widgets[6].id,  # Today's weight tracker group
                "widget_id": dashboard_widgets[8].id,  # Weight Tracker
                "singleitemtrackerdetails_id": tracker_details[0].id,
                "value": "72.5",
                "time_added": datetime.combine(today, datetime.strptime("08:00", "%H:%M").time()),
                "created_by": "user_001"
            },
            {
                "daily_widget_id": daily_widgets[7].id,  # Today's steps tracker group
                "widget_id": dashboard_widgets[9].id,  # Steps Tracker
                "singleitemtrackerdetails_id": tracker_details[1].id,
                "value": "8500",
                "time_added": datetime.combine(today, datetime.strptime("20:00", "%H:%M").time()),
                "created_by": "user_001"
            }
        ]
        
        for config in tracker_activity_configs:
            activity = SingleItemTrackerItemActivity(**config)
            tracker_activities.append(activity)
            session.add(activity)
        
        await session.commit()
        print(f"✅ Created {len(tracker_activities)} single item tracker activities")
        
        # ============================================================================
        # 8. GENERATE WEBSEARCH_ITEM_ACTIVITIES (WebSearch activity tracking)
        # ============================================================================
        print("🔍 Creating websearch activities...")
        websearch_activities = []
        
        websearch_activity_configs = [
            # Today's activities
            {
                "daily_widget_id": daily_widgets[8].id,  # Today's AI Trends group
                "widget_id": dashboard_widgets[11].id,  # AI Trends 2024
                "websearchdetails_id": websearch_details[0].id,
                "status": "completed",
                "reaction": "Great insights on AI trends!",
                "summary": "AI trends are evolving rapidly with focus on generative AI, edge computing, and responsible AI development.",
                "source_json": {
                    "sources": [
                        {"title": "AI Trends 2024 Report", "url": "https://example.com/ai-trends-2024"},
                        {"title": "Generative AI Market Analysis", "url": "https://example.com/gen-ai-market"}
                    ]
                },
                "created_by": "user_001"
            },
            {
                "daily_widget_id": daily_widgets[9].id,  # Today's ML Papers group
                "widget_id": dashboard_widgets[13].id,  # Machine Learning Papers
                "websearchdetails_id": websearch_details[2].id,
                "status": "pending",
                "reaction": None,
                "summary": None,
                "source_json": None,
                "created_by": "user_002"
            }
        ]
        
        for config in websearch_activity_configs:
            activity = WebSearchItemActivity(**config)
            websearch_activities.append(activity)
            session.add(activity)
        
        await session.commit()
        print(f"✅ Created {len(websearch_activities)} websearch activities")
        
        # ============================================================================
        # 9. GENERATE WEBSEARCH_SUMMARY_AI_OUTPUT (AI summary data)
        # ============================================================================
        print("🤖 Creating websearch AI output...")
        websearch_ai_outputs = []
        
        websearch_ai_configs = [
            {
                "widget_id": dashboard_widgets[11].id,  # AI Trends 2024
                "query": "AI trends 2024",
                "result_json": {
                    "summary": "AI trends in 2024 focus on generative AI, edge computing, and responsible AI development. Key areas include large language models, AI governance, and sustainable AI practices.",
                    "sources": [
                        {"title": "AI Trends 2024 Report", "url": "https://example.com/ai-trends-2024"},
                        {"title": "Generative AI Market Analysis", "url": "https://example.com/gen-ai-market"}
                    ],
                    "search_successful": True,
                    "results_count": 5,
                    "confidence_score": "0.85"
                },
                "ai_model_used": "gpt-3.5-turbo",
                "ai_prompt_used": "Summarize the latest AI trends for 2024 based on the provided search results.",
                "ai_response_time": "2.3s",
                "search_results_count": "5",
                "summary_length": "156",
                "sources_used": [
                    {"title": "AI Trends 2024 Report", "url": "https://example.com/ai-trends-2024"},
                    {"title": "Generative AI Market Analysis", "url": "https://example.com/gen-ai-market"}
                ],
                "generation_type": "ai_generated",
                "created_by": "user_001"
            },
            {
                "widget_id": dashboard_widgets[12].id,  # Latest Tech News
                "query": "latest technology news",
                "result_json": {
                    "summary": "Latest technology news highlights advancements in quantum computing, 5G deployment, and renewable energy technologies. Major tech companies are investing heavily in AI and machine learning.",
                    "sources": [
                        {"title": "Tech News Daily", "url": "https://example.com/tech-news"},
                        {"title": "Technology Review", "url": "https://example.com/tech-review"}
                    ],
                    "search_successful": True,
                    "results_count": 4,
                    "confidence_score": "0.82"
                },
                "ai_model_used": "gpt-3.5-turbo",
                "ai_prompt_used": "Summarize the latest technology news based on the provided search results.",
                "ai_response_time": "1.8s",
                "search_results_count": "4",
                "summary_length": "142",
                "sources_used": [
                    {"title": "Tech News Daily", "url": "https://example.com/tech-news"},
                    {"title": "Technology Review", "url": "https://example.com/tech-review"}
                ],
                "generation_type": "ai_generated",
                "created_by": "user_001"
            },
            {
                "widget_id": dashboard_widgets[13].id,  # Machine Learning Papers
                "query": "machine learning papers",
                "result_json": {
                    "summary": "Recent machine learning papers focus on transformer architectures, few-shot learning, and interpretable AI. Notable research includes attention mechanisms and neural network optimization.",
                    "sources": [
                        {"title": "ML Research Papers", "url": "https://example.com/ml-papers"},
                        {"title": "AI Conference Proceedings", "url": "https://example.com/ai-conference"}
                    ],
                    "search_successful": True,
                    "results_count": 6,
                    "confidence_score": "0.88"
                },
                "ai_model_used": "gpt-3.5-turbo",
                "ai_prompt_used": "Summarize recent machine learning research papers based on the provided search results.",
                "ai_response_time": "3.1s",
                "search_results_count": "6",
                "summary_length": "178",
                "sources_used": [
                    {"title": "ML Research Papers", "url": "https://example.com/ml-papers"},
                    {"title": "AI Conference Proceedings", "url": "https://example.com/ai-conference"}
                ],
                "generation_type": "ai_generated",
                "created_by": "user_002"
            }
        ]
        
        for config in websearch_ai_configs:
            ai_output = WebSearchSummaryAIOutput(**config)
            websearch_ai_outputs.append(ai_output)
            session.add(ai_output)
        
        await session.commit()
        print(f"✅ Created {len(websearch_ai_outputs)} websearch AI outputs")
    
    await engine.dispose()
    
    # ============================================================================
    # SUMMARY
    # ============================================================================
    print("\n🎉 Dummy data generation complete!")
    print("=" * 50)
    print("📊 Generated data summary:")
    print(f"   📋 Dashboard Widgets: {len(dashboard_widgets)}")
    print(f"   ⏰ Alarm Details: {len(alarm_details)}")
    print(f"   📋 Todo Details: {len(todo_details)}")
    print(f"   📅 Daily Widgets: {len(daily_widgets)}")
    print(f"   📈 Alarm Activities: {len(alarm_activities)}")
    print(f"   📋 Todo Activities: {len(todo_activities)}")
    print(f"   📊 SingleItemTracker Activities: {len(tracker_activities)}")
    print(f"   🔍 WebSearch Activities: {len(websearch_activities)}")
    print(f"   🤖 WebSearch AI Outputs: {len(websearch_ai_outputs)}")
    print("\n🔗 All foreign key relationships satisfied!")
    print("\n📅 Date ranges:")
    print(f"   - Yesterday: {yesterday}")
    print(f"   - Today: {today}")
    print(f"   - Tomorrow: {tomorrow}")
    print("\n👥 Users: user_001, user_002")
    print("🎯 Widget Types: alarm, todo-habit, todo-task, todo-event, singleitemtracker, websearch")
    print("📊 Categories: Health, Work, Productivity, Research")

# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    asyncio.run(generate_dummy_data()) 