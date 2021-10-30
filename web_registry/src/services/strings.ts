const _strings = {
    dialog_action_cancel: 'Cancel',
    dialog_action_save: 'Save',

    patient_detail_section_behavior_strategies_title: 'Behavioral Strategies',
    patient_detail_section_behavior_strategies_hash: 'behavioral',
    patient_detail_subsection_values_inventory_title: 'Values Inventory',
    patient_detail_subsection_values_inventory_hash: 'values',
    patient_detail_subsection_checklist_title: 'Behavioral Activation',
    patient_detail_subsection_checklist_hash: 'checklist',

    patient_values_inventory_assign_button: 'Assign',
    patient_values_inventory_assigned_button: 'Assigned',
    patient_values_inventory_assigned_date: 'Assigned on',
    patient_values_inventory_activity_date_header: 'Last edited',
    patient_values_inventory_activity_name_header: 'Activity',
    patient_values_inventory_activity_value_header: 'Value',
    patient_values_inventory_activity_lifearea_header: 'Life area',
    patient_values_inventory_activity_enjoyment_header: 'Enjoyment',
    patient_values_inventory_activity_importance_header: 'Importance',

    patient_progress_assessment_header_date: 'Date',
    patient_progress_assessment_header_comment: 'Note',
    patient_progress_assessment_action_add: 'Add Record',
    patient_progress_assessment_action_configure: 'Configure',
    patient_progress_assessment_dialog_configure_title: 'Configure Assessment',
    patient_progress_assessment_dialog_configure_frequency_label: 'Assessment Frequency',
    patient_progress_assessment_dialog_configure_dayofweek_label: 'Assessment Day of the Week',

    patient_progress_assessment_dialog_add_total_score_label: 'Submit total score only',
    patient_progress_assessment_dialog_comment_label: 'Note',
    patient_progress_assessment_record_comment_default: 'Added by CM',

    patient_progress_mood_header_date: 'Date',
    patient_progress_mood_header_mood: 'Mood Rating',
    patient_progress_mood_header_comment: 'Note',
    patient_progress_mood_empty: 'There are no mood ratings submitted for this patient.',

    patient_progress_medication_header_date: 'Date',
    patient_progress_medication_header_adherence: 'Took all medication for last 7 days',
    patient_progress_medication_header_comment: 'Question or Comment for Care Team',
    patient_progress_medication_empty: 'There are no medication tracking logs submitted for this patient.',
    patient_progress_medication_adherence_yes: 'Yes',
    patient_progress_medication_adherence_no: 'No',

    patient_progress_activity_hash: 'activity',
    patient_progress_activity_name: 'Activity Tracking',
    patient_progress_activity_header_activity: 'Activity',
    patient_progress_activity_header_date: 'Date',
    patient_progress_activity_header_success: 'Completed',
    patient_progress_activity_header_pleasure: 'Pleasure',
    patient_progress_activity_header_accomplishment: 'Accomplishment',
    patient_progress_activity_header_comment: 'Note',
    patient_progress_activity_success_yes: 'Yes, I did it',
    patient_progress_activity_success_no: 'No, I did not do it',
    patient_progress_activity_success_maybe: 'No, but I did something else',
    patient_progress_activity_empty: 'There are no activity tracking logs submitted for this patient.',

    patient_behavioral_checklist_components_header: 'BA Core Components',
    patient_behavioral_checklist_resources_header: 'Relevant Forms and Worksheets',
    patient_behavioral_checklist_not_completed: 'Not completed',
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
