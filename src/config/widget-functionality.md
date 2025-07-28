# Widget Functionality Documentation

This document provides detailed functionality explanations for all widgets in the Brainboard system.

## Medium Sized Widgets (10x8 or 8x10)

### Everyday Web Search
**Purpose**: Daily search 
**Key Features**:
- Onload - call an api to check how many web searches are scheduled today. 
    - Create widgets for each
- For each web search scheduled for today :
    - Call an api with today's date, search term and get the result 
    - It will have heading, subheading, text, images, probably some chart data.
    - Display it appropriately with formatting

### Every Day Task List
**Purpose**: Daily task management and tracking system
**Key Features**:
- Only single widget allowed
- Add mission Button - with form
    - FORM:
        - Title, 
        - Frequency
        - Category
        - Color coded with the category color for each task 
        - Importance
        - Priority
        - Due date
        - Goal
    - Add mission free text field - autofills the form
        - Calls an api to fetch data model as result
        - Auto fills the form
    - Call an api to fetch the actual monthly detailed schedule given the form.
- Onload - Calls an api to fetch the list of today's tasks. - displays the list.
- Task completion tracking
    - Checkbox for each task
    - Call an api to update the task 
- Progress visualization 
    - Each task will have attributes for each day when added to today's todo list such as -
        - Explanation for picking today
            - List of critical reasons
            - List of medium reasons
            - List of green reasons
            - Is it in today's top 3?
        - Progress health till now
            - Category wise health
            - Task weightage in its category
            - Frequency done, frequency hoped
            - Milestones covered
        - % of goal we will cover if we do it today
            - Upcoming milestones
            - Progress of goal percentage
            - Countdown timer until milestone reached
            - Motivational line
        - % of backlog increase if we don't do it today

### Monthly Calendar
**Purpose**: Monthly calendar view and planning interface
**Key Features**:
- Only single widget allowed
- Onload create the Monthly calendar grid for current month
- Calendar navigation
- Each past day shall have information depicted visually without text
    - Percent of task list from that day that was completed
    - Were top 3 tasks completed?
    - Milestones achieved
    - Other achievements / highlights
- Future day - 
    - Event reminders
    - Upcoming milestones 
    - Critical tasks incoming in next week
    - Free days upcoming
- Reminder system

### Habit List Trackers
**Purpose**: Track and monitor daily habits for personal development
**Key Features**:
- Habit creation - exactly like mission with an additional 'habit' flag
- Type of habit tracking - schedule
- Streak counting
- Statistics and insights
- Reminder system
- Onload - fetch all habit tracker widgets added 
- For each habit widget added:
    - List of habit tasks added to this habit widget 
        - Progress for each 
    - Chart showing improevemtn from past 5 weeks
- Color coded with the category color for each task 
- Single item tracker needed to be attached?


### AI Task History
**Purpose**: AI-powered task history and insights
**Key Features**:
- Everyday our AI will run some things 
- This widget will show all actions the AI took today to help the user.
- It may be user requested or scheduled

### Web Search Chart
**Purpose**: Visualize web search patterns and trends
**Key Features**:
- Fetch how many web search chart widgets are scheduled for today.
- Ife yes, create widgets for each
    - Fetch the chart data for the given web search chart
    - Fetch another api for Trend analysis - some insights and charts in a pretty way

### Notifications
**Purpose**: Centralized notification center
**Key Features**:
- Summary list of notifications 
- Types expandable: 
    - Notification grouped from phone
    - Widget-specific alerts
    - Priority task reminders
- Dismiss and snooze options
- Notification preferences

## Small Sized Widgets (8x6)

### Reminders
**Purpose**: Quick reminder management for immediate tasks
**Key Features**:
- Quick reminder creation
- Fetch all the reminders.  - create widgets for all
    - Time-based alerts - ping hard. create a countdown timer and add alarms if critical and snoozed a lot. things like that.
- Priority levels
- Reminder categories
- Quick actions (complete, snooze, dismiss)

### Single Item Tracker
**Purpose**: Track single items like smoke/gym/weight
**Key Features**:
- fetch list of items for today - display the field at that time.
- Data entry form. 1-2 fields max - when added, check the item and remove widget after some time.
- Progress visualization
- Tiny Historical data chart

### This Hour
**Purpose**: Hourly task and time tracking
**Key Features**:
- Current hour focus
- Time remaining display
- Message animation to capture attention
- Check today's schedule and see if any extra messages need to be announced.

