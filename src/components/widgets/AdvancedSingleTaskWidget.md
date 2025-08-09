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
