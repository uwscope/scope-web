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
    Form_button_delete: 'Delete',
    Form_submit_thankyou: 'Thank you',
    Form_error_text: 'Sorry, there was an error processing your request. Please try again.',

    Navigation_home: 'Home',
    Navigation_careplan: 'Activities',
    Navigation_progress: 'Progress',
    Navigation_resources: 'Tools',

    Home_quote_title: 'Quote of the day',
    Home_things_title: 'Requested by provider',
    Home_values_button_text: 'Complete Values and Activities Inventory',
    Home_safety_button_text: 'Complete Safety Plan',
    Home_assessment_button_text: 'Complete ${assessment} Check-In',
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
        'You can use the space below to record notes about mood or any events that may be affecting your mood. This information will be available to your clinical social worker.',
    Form_mood_submit_success:
        'Thank you for checking in. Your responses will be available to your clinical social worker.',

    Form_assessment_checkin_title: 'Check-In',
    Form_assessment_score_column_name: 'Score',
    Form_assessment_comment_prompt: 'Do you have any other notes?',
    Form_assessment_comment_help:
        'You can use this space to make some notes about anything that may have contributed to your symptoms. This information will be available to your clinical social worker.',
    Form_assessment_submit_success:
        'Thank you for checking in. Your responses will be available to your clinical social worker.',

    Form_confirm_close: 'Are you sure you want to close without submitting?',

    Form_activity_logging_title: 'Activity Check-In',
    Form_activity_log_success_prompt: 'Were you able to complete the following activity?',
    Form_activity_log_success_yes: 'Yes, I did it',
    Form_activity_log_success_no: 'No, I did not do it',
    Form_activity_log_success_something_else: 'No, but I did something else',
    Form_activity_log_alternative_propmpt: 'What alternate activity did you do?',
    Form_activity_log_pleasure_prompt: 'Rate how much pleasure you experienced as you were doing this activity',
    Form_activity_log_pleasure_help: 'Use the slider to select your rating. 0 is low. 10 is high.',
    Form_activity_log_accomplishment_prompt: 'Rate your sense of accomplishment after you did this activity',
    Form_activity_log_accomplishment_help: 'Use the slider to select your rating. 0 is low. 10 is high.',
    Form_activity_log_rating_low: 'Low',
    Form_activity_log_rating_moderate: 'Moderate',
    Form_activity_log_rating_high: 'High',
    Form_activity_log_comment_prompt: 'Do you have any other notes?',
    Form_activity_log_comment_help:
        'You can use this space to make some notes about how things went with this activity. This information will be available to your clinical social worker.',
    Form_activity_log_submit_success:
        'Thank you for checking in. Your responses will be available to your clinical social worker.',

    Resources_inventory_title: 'Values & Activities Inventory',
    Resources_inventory_subtitle: 'Values and activities that align with your life goals',

    values_inventory_home_title: 'Values & Activities Inventory',
    values_inventory_home_instruction1:
        'Staying active in things that are important to you is very important in maintaining your health and quality of life.',
    values_inventory_home_instruction2:
        'The Values & Activities inventory will be useful in collaborating with your care team by identifying what values are important to you and what activities might support those values.',
    values_inventory_home_instruction3:
        'The inventory consists of five life areas. You can fill them out in any order.',
    values_inventory_home_instruction4: 'Tap on any life area to start.',

    values_inventory_life_area_other_activities_name: 'Other Activities',
    values_inventory_life_area_other_activities_title: 'Activities Not Assigned To Values',
    values_inventory_life_area_other_activities_subprompt: 'As you identify personal values, assign these to support your values.',

    values_inventory_values_example_title: 'Example Values',
    values_inventory_values_empty_subprompt: 'List one or more of your personal values that fit with this life area.',
    values_inventory_values_identify_title: 'Identify Personal Values',
    values_inventory_values_identify_existing_title: 'Identified Personal Values',
    values_inventory_values_identify_more_title: 'Identify Additional Personal Values',

    Values_inventory_lifearea: 'Life area',
    values_inventory_value_count_singular: 'value',
    values_inventory_value_count_plural: 'values',
    values_inventory_activity_count_singular: 'activity',
    values_inventory_activity_count_plural: 'activities',

    Values_inventory_add_value: 'Add value',

    Values_inventory_values_example_values: 'Example values',

    Values_inventory_value_item_example_activities: 'Example activities',
    Values_inventory_value_item_activities_none: 'List one or more activities associated with this value.',

    values_inventory_add_activity: 'Add activity',
    values_inventory_value_activity_enjoyment: 'Enjoyment',
    values_inventory_value_activity_importance: 'Importance',

    Values_inventory_dialog_add_value: 'Add value',
    Values_inventory_dialog_add_value_label: 'Name your value',

    Values_inventory_dialog_edit_value: 'Edit value',

    values_inventory_activity_menu_delete: 'Delete',
    values_inventory_activity_menu_edit: 'Edit',
    values_inventory_activity_menu_add_schedule: 'Add Schedule',

    // Values_inventory_dialog_add_activity: 'Add activity',
    // Values_inventory_dialog_edit_activity: 'Edit activity',
    // Values_inventory_dialog_add_activity_label: 'Name your activity',
    // Values_inventory_dialog_add_activity_prompt:
    //     'For this activity, rate how much you enjoy doing it and how important it is for you to do it. 0 being low and 10 being high.',
    // Values_inventory_dialog_add_activity_enjoyment: 'Enjoyment (0-10)',
    // Values_inventory_dialog_add_activity_importance: 'Importance (0-10)',

    Resources_resources_title: 'Library',
    Resources_resources_subtitle: 'Shared documents and learning resources',

    Resources_title: 'Library',

    Progress_phq_assessment_title: 'Depression Check-In',
    Progress_gad_assessment_title: 'Anxiety Check-In',
    Progress_activity_tracking_title: 'Activity Tracking',
    Progress_mood_tracking_title: 'Mood Tracking',

    Activity_tracking_column_date: 'Date',
    Activity_tracking_column_name: 'Activity Name',
    Activity_tracking_column_completed: 'Completed',
    Activity_tracking_column_lifearea: 'Life Area',
    Activity_tracking_column_value: 'Value',
    Activity_tracking_column_alternative: 'Alternative',
    Activity_tracking_column_pleasure: 'Pleasure',
    Activity_tracking_column_accomplishment: 'Accomplishment',
    Activity_tracking_column_comment: 'Note',
    Activity_tracking_success_yes: 'Yes',
    Activity_tracking_success_no: 'No',
    Activity_tracking_success_alt: 'Alt',
    Activity_tracking_success_none: '--',

    Activity_tracking_log_lifearea_none: 'Uncategorized',
    Activity_tracking_log_value_none: 'Unspecified',
    Activity_tracking_no_data: 'There are no submitted activity data.',

    Mood_tracking_column_date: 'Date',
    Mood_tracking_column_mood: 'Mood',
    Mood_tracking_column_comment: 'Note',
    Mood_tracking_detail_title: 'Mood Entry',
    Mood_tracking_no_data: 'There are no submitted mood data.',

    Assessment_progress_column_date: 'Date',
    Assessment_progress_column_total: 'Total',
    Assessment_progress_column_comment: 'Note',
    Assessment_progress_no_data: 'There are no submitted data for this assessment.',

    Progress_phq_assessment_detail_title: 'Depression Assessment',
    Progress_gad_assessment_detail_title: 'Anxiety Assessment',

    Careplan_no_tasks: 'There are no planned activities for this day.',
    Careplan_view_calendar: 'Calendar view',
    Careplan_view_activity: 'Activity view',
    careplan_activities_other: 'Other Activities',
    Careplan_activity_item_value: 'Value',
    Careplan_activity_item_start_date: 'Starts',
    Careplan_activity_item_repeat: 'Repeats',

    Careplan_activity_item_edit: 'Edit',
    careplan_activity_item_delete: 'Delete',

    Careplan_add_activity: 'Add activity',

    Careplan_no_activities: 'You have no activities. Add one by tapping the button above!',

    form_add_activity_title: 'Add Activity',
    form_edit_activity_title: 'Edit Activity',
    form_add_activity_submit_success: 'Your activity is created.',
    form_edit_activity_submit_success: 'Your activity is updated.',
    form_add_activity_schedule_submit_success: 'Your activity is scheduled.',
    form_edit_activity_schedule_submit_success: 'Your activity schedule is updated.',

    // Form_add_activity_choose_or: 'OR',
    // Form_add_activity_describe: 'Describe the activity',

    form_add_edit_activity_name_prompt: 'What is the name of the activity?',
    // Form_add_activity_describe_name_label: 'Name',
    form_add_edit_activity_name_help: 'Write a descriptive name of the activity that helps you recognize what it is.',
    // 'Write a descriptive name of the activity that helps you recognize what it is. You can choose an activity that you already identified from the values inventory.',

    // Form_add_activity_describe_name_import_button: 'Choose from the values & activities inventory',
    // Form_add_activity_describe_name_import_dialog_title: 'Choose from the values & activities inventory',

    form_add_edit_activity_life_area_value_prompt: 'Which life area and value are best associated with this activity?',
    form_add_edit_activity_life_area_value_help: 'You can also identify values in the Values & Activity Inventory.',
    form_add_edit_activity_life_area_label: 'Life Area',
    form_add_edit_activity_life_area_help: 'Choose a life area.',
    form_add_edit_activity_value_label: 'Value',
    form_add_edit_activity_value_help:
        // TODO Activity Refactor
        // 'Then choose a value you have identified, or add a new value.',
        'Then choose a value you have identified.',
    form_add_edit_activity_add_value_button: 'Add Value',
    form_add_edit_activity_enjoyment_prompt: 'How much do you enjoy doing this activity?',
    form_add_edit_activity_enjoyment_help: '0 is low enjoyment and 10 is high enjoyment.',
    form_add_edit_activity_importance_prompt: 'How important it is for you to do this activity?',
    form_add_edit_activity_importance_help: '0 is low importance and 10 is high importance.',
    form_add_edit_activity_name_validation_not_unique: 'Activity already exists.',


    form_add_activity_schedule_title: 'Add Schedule',
    form_edit_activity_schedule_title: 'Edit Schedule',

    form_add_edit_activity_schedule_when_prompt:
        'When would you like to do this activity?',
    form_add_edit_activity_schedule_date_label:
        'Schedule Date',
    form_add_edit_activity_schedule_date_help:
        'Choose a date you would like to do this activity.',
    form_add_edit_activity_schedule_date_validation_invalid_format:
        'Invalid date format.',
    form_add_edit_activity_schedule_time_of_day_label:
        'Schedule Time',
    form_add_edit_activity_schedule_time_of_day_help:
        'Choose a time you would like to do this activity.',
    form_add_edit_activity_schedule_time_of_day_validation_invalid_format:
        'Invalid time format.',
    form_add_edit_activity_schedule_has_repetition_prompt:
        'Would you like to repeat this activity every week?',
    form_add_edit_activity_schedule_repeat_days_prompt:
        'On what days would you like to repeat this activity?',
    form_add_edit_activity_schedule_repetition_validation_no_days:
        'Select one or more days.',

    // Form_add_activity_describe_value_help:
    //     'If the value does not appear in this list, you can add them from the values inventory.',
    //
    // Form_add_activity_reminder_section: 'Set reminder',
    // Form_add_activity_reminder: 'Would you like a reminder for this activity?',
    // Form_add_activity_reminder_time: 'When would you like to be reminded?',
    // Form_add_activity_reminder_time_label: 'Reminder time',
    // Form_add_activity_repetition_section: 'Set repetition',
    //


    Form_submit_error_message: 'Sorry! There was an error submitting. Please try again.',
    Form_submit_error_retry: 'Retry',

    Resources_safety_plan_title: 'Safety Plan',
    Resources_safety_plan_subtitle: 'Coping strategies and support to help during crisis or high distress',
    Resources_about_us_title: 'About Us',
    Resources_about_us_subtitle: 'Learn about the study',
    Resources_crisis_resources_title: 'Crisis Help',
    Resources_crisis_resources_subtitle: 'Crisis resources and hotlines',
    Resources_logout_title: 'Log out',
    Resources_logout_subtitle: 'Log out of the app',

    Safetyplan_title: 'Safety Plan',
    Safetyplan_reasons_for_living_title: 'Reasons for living',
    Safetyplan_reasons_for_living_description: 'What are my reasons for living?',
    Safetyplan_warning_signs_title: 'Warning signs',
    Safetyplan_warning_signs_description:
        'What are some thoughts, images, mood, situation, or behavior that might trigger a crisis?',
    Safetyplan_coping_strategies_title: 'Internal coping strategies',
    Safetyplan_coping_strategies_description:
        'What are some things I can do to take my mind off my problems without contacting another person (relaxation techniques, physical activities)?',
    Safetyplan_social_distraction_person_title: 'Social distraction',
    Safetyplan_social_distraction_person_description: 'Who are the people that provide positive distraction?',
    Safetyplan_social_distraction_setting_title: 'Social settings',
    Safetyplan_social_distraction_setting_description: 'What are social settings that provide positive distraction?',
    Safetyplan_name: 'Name',
    Safetyplan_phone: 'Phone number',
    Safetyplan_people_help_title: 'Social support',
    Safetyplan_people_help_description: 'Who are the people I can ask for help?',
    Safetyplan_professional_help_title: 'Professional help',
    Safetyplan_professional_help_description: 'Who are the professionals I can contact during a crisis?',
    Safetyplan_agency_help_title: 'Professional service',
    Safetyplan_agency_help_description: 'What are the services or agencies I can contact during a crisis?',
    Safetyplan_clinician_name: 'Clinician name',
    Safetyplan_clinician_pager: 'Pager or emergency contact number',
    Safetyplan_local_care_name: 'Local urgent care service',
    Safetyplan_local_care_address: 'Service address',
    Safetyplan_local_care_phone: 'Service phone number',
    Safetyplan_add: 'Add another',
    Safetyplan_add_place: 'Add place',
    Safetyplan_add_person: 'Add person',
    Safetyplan_suicide_hotline_title: 'Suicide prevention lifeline phone',
    Safetyplan_suicide_hotline_phone: '1-800-273-TALK(8255)',
    Safetyplan_environment_title: 'Safe environment',
    Safetyplan_environment_description: 'What are some ways I can make the environment safe?',
    Safetyplan_submit_success:
        'Thank you for updating your safety plan. Your responses will be available to your clinical social worker.',
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
