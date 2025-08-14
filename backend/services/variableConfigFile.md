lets create a config file that is being used here. 
each variable will have - 

name,
description
is_required
intent_type: adding | editing_config | editing_day_activity | analyzing | discussing
forEngine_try_harder: yes | no

forAI_fallback_suggestion_type : infer | ask | recommend | recommend_with_suggestion
forAI_fallback_suggestion : text 
    "AI should stringly suggest to the user that milestones are a good metric to have for gymming for example weight or steps or hours achieved"
    "AI should suggest to the user that reminder at a particular time of the day will help him do this task"
    "AI should infer from conversation what the title should be"
    "AI should infer from conversation what the title should be"

forDB_fetch_data_key : activity_log | all_task_list | today_list | task_details | task_activity
forDB_fetch_data_payload : { date_period, task_list, category_list, task_title }

forAI_intent_expectation_text : text 
    "When discussing, AI should do google searches and try to find gameplan for the user on the topic in mind and make some suggestions to the user" , 
    "Here is some more data about the habits of the user and what activity he has done for AI's benefit."

forEngine_validation
forEngine_structure
forTool_destination


