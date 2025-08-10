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

### Daily Actions overall
- mood tracker - input list of moods for today


### Actions on a task
## AdvancedSingleTaskWidget – Activity Reference (Concise)

### User actions
- Toggle task status: Set to pending, in_progress, completed, or cancelled.
- Add tracker value: Enter a value (type depends on value_type) and optional notes.
- Snooze alarm (when ringing): Snoozes for 10 minutes and records a snooze entry.
- Stop alarm (when ringing): Marks task as completed and records a stop entry.
- Read Web Search: Read the summary of the requested daily web search.
- Remove widget: Remove from dashboard (via widget header action).

### Activity fields (updated by actions)
- status: Task state (pending | in_progress | completed | cancelled).
- progress: Numeric progress (0–100). Auto-derived when status changes (0/50/100).
- value: Latest tracker entry value.
- time_added: ISO timestamp of the latest tracker entry.
- notes: Optional note for the tracker entry.
- snooze_count: Total times the alarm was snoozed today.
- activity_history: Array of entries capturing snooze/stop actions with timestamps and counts.
- started_at: ISO timestamp set when alarm is stopped.

### Related widget_config (affects behavior/display)
- alarm_times: List of HH:MM times that can trigger the alarm window.
- target_value: Goal/target value shown for the tracker.
- value_type: Type for the value input (number | text | decimal).
- value_unit: Unit label for the value (e.g., kg, steps).

- 
