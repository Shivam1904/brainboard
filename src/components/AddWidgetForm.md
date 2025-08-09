## AddWidgetForm – Field Reference (Concise)

### Form fields
- title: Widget title shown on the dashboard.
- description: Optional short text describing the widget.
- is_permanent: Marks the widget as permanent (hides Category and Frequency inputs).
- category: Widget category (productivity, health, job, information, entertainment, utilities).
- frequency_details: Frequency settings selected in the Frequency section (e.g., daily/weekly/monthly cadence).
- importance: Numeric importance score (preset in the form; may not be directly edited).

### widget_config fields
- include_progress_details: Toggle to enable Progress settings.
- selected_calendar: ID of the calendar to attach progress/todos to.
- streak_type: Streak tracking mode (none, daily, weekly, monthly).
- streak_count: Number of periods required to maintain the streak when streaks are enabled.
- milestones: List of milestones; each has text and due_date (YYYY-MM-DD).
- include_alarm_details: Toggle to enable Alarm settings.
- alarm_times: List of alarm times in HH:MM (24h) format.
- is_snoozable: Whether the alarm can be snoozed.
- include_tracker_details: Toggle to enable Tracker settings.
- value_type: Type of tracked value (number, text, boolean).
- value_unit: Unit/label for tracked values (e.g., kg, steps).
- target_value: Goal/target value for the tracker.
- include_websearch_details: Toggle to enable Web Search settings.
- search_query_detailed: Detailed search query text used by the web search widget.


## Daily Activity

### Actions on a task

- 
