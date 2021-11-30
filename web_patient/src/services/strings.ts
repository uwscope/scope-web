const _strings = {
    Form_button_yes: 'Yes',
    Form_button_no: 'No',
    Form_button_next: 'Next',
    Form_button_back: 'Back',
    Form_button_submit: 'Submit',
    Form_button_add: 'Add',
    Form_button_save: 'Save',
    Form_button_cancel: 'Cancel',
    Form_button_close: 'Close',
    Form_button_ok: 'Okay',
    Form_submit_thankyou: 'Thank you',

    Navigation_home: 'Home',
    Navigation_careplan: 'Care plan',
    Navigation_progress: 'Progress',
    Navigation_profile: 'Profile',

    Home_quote_title: 'Quote of the day',
    Home_things_title: 'Requested by provider',
    Home_values_button_text: 'Complete values and activities inventory',
    Home_safety_button_text: 'Complete safety planning',
    Home_assessment_button_text: 'Complete ${assessment} assessment',
    Home_mood_button_text: 'Log your mood',
    Home_plan_title: 'My plan for today',
    Home_plan_done: 'You are all caught up! Make sure to celebrate your achievement!',

    Form_mood_logging_title: 'Mood Check-In',
    Form_mood_logging_mood_prompt: 'How would you rate your current mood?',
    Form_mood_logging_mood_help:
        'Use the slider to select your rating. 0 is low/very bad mood. 10 is high/very good mood.',
    Form_mood_logging_mood_bad: 'Low',
    Form_mood_logging_mood_neutral: 'Neutral',
    Form_mood_logging_mood_good: 'High',
    Form_mood_logging_comment_prompt: 'Do you have any other notes?',
    Form_mood_logging_comment_help:
        'You can use the space below to record notes about mood or any events that may be affecting your mood. This information will be available to your psychosocial care team.',
    Form_mood_submit_success:
        'Thank you for checking in. Your responses will be available to your psychosocial care team.',

    Form_assessment_checkin_title: 'Check-In',
    Form_assessment_score_column_name: 'Score',
    Form_assessment_comment_prompt: 'Do you have any other notes?',
    Form_assessment_comment_help:
        'You can use the space below to record notes about mood or any events that may be affecting your mood. This information will be available to your psychosocial care team.',
    Form_assessment_submit_success:
        'Thank you for checking in. Your responses will be available to your psychosocial care team.',

    Form_confirm_close: 'Are you sure you want to close without submitting?',

    Form_activity_logging_title: 'Activity Check-In',
    Form_activity_log_success_prompt: 'Were you able to complete the following activity?',
    Form_activity_log_success_yes: 'Yes, I did it',
    Form_activity_log_success_no: 'No, I did not do it',
    Form_activity_log_success_something_else: 'No, but I did something else',
    Form_activity_log_alternative_propmpt: 'What alternate activity did you do?',
    Form_activity_log_pleasure_prompt: 'Rate how much pleasure you experienced as you were doing this activity',
    Form_activity_log_pleasure_help: 'User the slider to select your rating. 0 is low. 10 is high.',
    Form_activity_log_accomplishment_prompt: 'Rate your sense of accomplishment after you did this activity',
    Form_activity_log_accomplishment_help: 'User the slider to select your rating. 0 is low. 10 is high.',
    Form_activity_log_rating_low: 'Low',
    Form_activity_log_rating_moderate: 'Moderate',
    Form_activity_log_rating_high: 'High',
    Form_activity_log_comment_prompt: 'Do you have any other notes?',
    Form_activity_log_comment_help:
        'You can use the space below to add a note to remind yourself about anything related to this activity. This information will be available to your psychosocial care team.',
    Form_activity_log_submit_success:
        'Thank you for checking in. Your responses will be available to your psychosocial care team.',

    Profile_inventory_title: 'My Values Inventory',
    Profile_inventory_subtitle: 'Values and activities that align with your life goals',

    Values_inventory_title: 'Values Inventory',
    Values_inventory_instruction1:
        'Staying active in things that are important to you is very important in maintaining your health and quality of life.',
    Values_inventory_instruction2:
        'The Life Areas, Values & Activities inventory will be useful in collaborating with your care team by identifying what values are important to you and what activities might be able to support those values.',
    Values_inventory_instruction3:
        'The inventory consists of five life areas. You can fill them out in any order you wish.',
    Values_inventory_instruction4: 'Tap on any life area to start filling the inventory.',
    Values_inventory_lifearea: 'Life area',
    Values_inventory_value_singular: 'value',
    Values_inventory_value_plural: 'values',
    Values_inventory_activity_singular: 'activity',
    Values_inventory_activity_plural: 'activities',

    Values_inventory_values_none: 'List one or more of your personal values that fit with this life area',
    Values_inventory_values_example_values: 'Example values',
    Values_inventory_values_header: 'Your values',
    Values_inventory_values_help:
        'Below are your values for this life area. Tap on a value to add or modify activities associated with the value, or add more values to this life area.',

    Values_inventory_value_item_example_activities: 'Example activities',
    Values_inventory_value_item_activities_none: 'List one or more activities associated with this value.',
    Values_inventory_value_item_examples:
        'Tell my child I love them every day\nMake a special breakfast for my child on Saturday\nTake my child to the park on Saturday\nPick up my child from school promptly each day',
    Values_inventory_value_item_activities_header: 'Your activities',
    Values_inventory_value_item_activities_help:
        'Below are your activities for this value. Tap on an activity to modify, or add more activities to this value.',

    Values_inventory_value_item_activities_enjoyment: 'Enjoyment',
    Values_inventory_value_item_activities_importance: 'Importance',

    Values_inventory_dialog_add_value: 'Add value',
    Values_inventory_dialog_add_value_label: 'Value name',

    Values_inventory_dialog_add_activity: 'Add activity',
    Values_inventory_dialog_add_activity_edit: 'Edit activity',
    Values_inventory_dialog_add_activity_name: 'Activity name',
    Values_inventory_dialog_add_activity_prompt:
        'For this activity, rate how much you enjoy doing it and how important it is for you to do it. 0 being low and 10 being high.',
    Values_inventory_dialog_add_activity_enjoyment: 'Enjoyment (0-10)',
    Values_inventory_dialog_add_activity_importance: 'Importance (0-10)',

    Profile_resources_title: 'My Resources',
    Profile_resources_subtitle: 'Shared documents and learning resources',

    Resources_title: 'My Resources',

    Progress_phq_assessment_title: 'PHQ-9 Assessments',
    Progress_gad_assessment_title: 'GAD-7 Assessments',
    Progress_activity_tracking_title: 'Activity Tracking',

    Activity_tracking_column_date: 'Date',
    Activity_tracking_column_name: 'Activity Name',
    Activity_tracking_column_completed: 'Completed',
    Activity_tracking_column_lifearea: 'Life Area',
    Activity_tracking_column_value: 'Value',
    Activity_tracking_column_pleasure: 'Pleasure',
    Activity_tracking_column_accomplishment: 'Accomplishment',
    Activity_tracking_column_comment: 'Note',
    Activity_tracking_success_yes: 'Yes',
    Activity_tracking_success_no: 'No',
    Activity_tracking_success_alt: 'Alt',

    Activity_tracking_log_lifearea_none: 'Uncategorized',
    Activity_tracking_log_value_none: 'Unspecified',
    Activity_tracking_no_data: 'There are no submitted activity data.',

    Assessment_progress_column_date: 'Date',
    Assessment_progress_column_total: 'Total',
    Assessment_progress_column_comment: 'Note',
    Assessment_progress_no_data: 'There are no submitted data for this assessment.',

    Progress_phq_assessment_detail_title: 'PHQ-9 Assessment',
    Progress_gad_assessment_detail_title: 'GAD-7 Assessment',

    Careplan_no_tasks: 'There are no planned activities for this day.',
    Careplan_view_calendar: 'Calendar view',
    Careplan_view_activity: 'Activity view',
    Careplan_activities_uncategorized: 'Uncategorized',
    Careplan_activity_item_value: 'Value',
    Careplan_activity_item_start_date: 'Starts',
    Careplan_activity_item_repeat: 'Repeats',

    Careplan_activity_item_edit: 'Edit',
    Careplan_activity_item_delete: 'Delete',
    Careplan_activity_item_activate: 'Activate',
    Careplan_activity_item_deactivate: 'Deativate',

    Careplan_add_activity: 'Add activity',

    Form_add_activity_title: 'Add activity',
    Form_edit_activity_title: 'Edit activity',
    Form_add_activity_choose_or: 'OR',
    Form_add_activity_describe: 'Describe the activity',

    Form_add_activity_describe_name: 'What is the name of the activity?',
    Form_add_activity_describe_name_label: 'Name',
    Form_add_activity_describe_name_help:
        'Write a descriptive name of the activity that helps you recognize what it is. You can choose an activity that you already identified from the values inventory.',
    Form_add_activity_describe_name_import_button: 'Choose from the values inventory',

    Form_add_activity_describe_name_import_dialog_title: 'Choose from the values inventory',

    Form_add_activity_describe_value: 'Which value is this activity best associated with?',
    Form_add_activity_describe_value_label: 'Value',
    Form_add_activity_describe_value_help:
        'If the value does not appear in this list, you can add them from the values inventory.',

    Form_add_activity_describe_lifearea: 'Which life area is this activity best associated with?',
    Form_add_activity_describe_lifearea_label: 'Life area',

    Form_add_activity_date: 'What date would you like to do/start this activity?',
    Form_add_activity_date_label: 'Activity start date',
    Form_add_activity_time: 'What time would you like to do this activity?',
    Form_add_activity_time_label: 'Activity time',
    Form_add_activity_reminder_section: 'Set reminder',
    Form_add_activity_reminder: 'Would you like a reminder for this activity?',
    Form_add_activity_reminder_time: 'When would you like to be reminded?',
    Form_add_activity_reminder_time_label: 'Reminder time',
    Form_add_activity_repetition_section: 'Set repetition',
    Form_add_activity_repetition: 'Would you like to repeat this activity?',
    Form_add_activity_repetition_days: 'On what days would you like to repeat this activity?',
    Form_add_activity_repetition_days_label: 'Repetition days',

    Form_add_activity_submit_success: 'Great! Your activity is saved.',

    Form_submit_error_message: 'Sorry! There was an error submitting your response. Please try again.',
    Form_submit_error_retry: 'Retry',
};

type Strings = typeof _strings;

export type StringId = keyof Strings;

export const getString = (key: StringId) => {
    const found = _strings[key];
    if (!found) {
        return 'MISSING STRING';
    } else {
        return found;
    }
};
