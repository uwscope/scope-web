from pathlib import Path
import jschon

# Declare each schema in order to support code analysis/completion
activity_schema: jschon.JSONSchema
activities_schema: jschon.JSONSchema
activity_log_schema: jschon.JSONSchema
activity_logs_schema: jschon.JSONSchema
assessment_schema: jschon.JSONSchema
assessments_schema: jschon.JSONSchema
assessment_log_schema: jschon.JSONSchema
assessment_logs_schema: jschon.JSONSchema
case_review_schema: jschon.JSONSchema
case_reviews_schema: jschon.JSONSchema
clinical_history_schema: jschon.JSONSchema
contact_schema: jschon.JSONSchema
enums_schema: jschon.JSONSchema
identity_schema: jschon.JSONSchema
life_area_value_schema: jschon.JSONSchema
life_area_value_activity_schema: jschon.JSONSchema
log_schema: jschon.JSONSchema
mood_log_schema: jschon.JSONSchema
mood_logs_schema: jschon.JSONSchema
patient_schema: jschon.JSONSchema
patient_profile_schema: jschon.JSONSchema
referral_status_schema: jschon.JSONSchema
regexes: jschon.JSONSchema
safety_plan_schema: jschon.JSONSchema
scheduled_activity_schema: jschon.JSONSchema
scheduled_activities_schema: jschon.JSONSchema
scheduled_assessments_schema: jschon.JSONSchema
scheduled_assessment_schema: jschon.JSONSchema
scheduled_item_schema: jschon.JSONSchema
session_schema: jschon.JSONSchema
sessions_schema: jschon.JSONSchema
values_inventory_schema: jschon.JSONSchema

# Declare files from which to populate each schema
SCHEMA_DIR_PATH = Path(Path(__file__).parent, "./schemas")
SCHEMAS = {
    "activity_schema": "activity.json",
    "activities_schema": "activities.json",
    "activity_log_schema": "activity-log.json",
    "activity_logs_schema": "activity-logs.json",
    "assessment_schema": "assessment.json",
    "assessments_schema": "assessments.json",
    "assessment_log_schema": "assessment-log.json",
    "assessment_logs_schema": "assessment-logs.json",
    "case_review_schema": "case-review.json",
    "case_reviews_schema": "case-reviews.json",
    "clinical_history_schema": "clinical-history.json",
    "contact_schema": "contact.json",
    "enums_schema": "enums.json",
    "identity_schema": "identity.json",
    "life_area_value_schema": "life-area-value.json",
    "life_area_value_activity_schema": "life-area-value-activity.json",
    "log_schema": "log.json",
    "mood_log_schema": "mood-log.json",
    "mood_logs_schema": "mood-logs.json",
    "patient_schema": "patient.json",
    "patient_profile_schema": "patient-profile.json",
    "referral_status_schema": "referral-status.json",
    "regexes": "regexes.json",
    "safety_plan_schema": "safety-plan.json",
    "scheduled_activity_schema": "scheduled-activity.json",
    "scheduled_activities_schema": "scheduled-activities.json",
    "scheduled_assessments_schema": "scheduled-assessments.json",
    "scheduled_assessment_schema": "scheduled-assessment.json",
    "scheduled_item_schema": "scheduled-item.json",
    "session_schema": "session.json",
    "sessions_schema": "sessions.json",
    "values_inventory_schema": "values-inventory.json",
}

catalog = jschon.create_catalog("2020-12")

# Schemas need to be loaded in dependency order.
# The jschon method for doing this internally uses jschon.JSONSchema.loadf,
# which does not set an encoding and therefore failed for utf-8 schema content.
# We therefore use jschon.JSONSchema.loads with an explicit utf-8 encoding.
# Instead of attempting to manually maintain a loading order,
# we brute force loading generations of the dependency graph while ensuring we maintain progress.

schemas_remaining = [key_current for key_current in SCHEMAS.keys()]
progress = True
while progress:
    progress = False

    for schema_current in schemas_remaining:
        try:
            with open(Path(SCHEMA_DIR_PATH, SCHEMAS[schema_current]), encoding="utf-8") as f:
                schema = jschon.JSONSchema.loads(f.read())

                globals()[schema_current] = schema

            progress = True
            schemas_remaining.remove(schema_current)
        except jschon.exceptions.CatalogError as e:
            # A dependency was not available, try again in the next generation
            pass
