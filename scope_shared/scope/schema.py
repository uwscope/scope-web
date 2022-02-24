import jschon
import json
from pathlib import Path
from typing import Optional

# Declare each schema in order to support code analysis/completion
activity_schema: Optional[jschon.JSONSchema] = None
activities_schema: Optional[jschon.JSONSchema] = None
activity_log_schema: Optional[jschon.JSONSchema] = None
activity_logs_schema: Optional[jschon.JSONSchema] = None
assessment_schema: Optional[jschon.JSONSchema] = None
assessments_schema: Optional[jschon.JSONSchema] = None
assessment_log_schema: Optional[jschon.JSONSchema] = None
assessment_logs_schema: Optional[jschon.JSONSchema] = None
case_review_schema: Optional[jschon.JSONSchema] = None
case_reviews_schema: Optional[jschon.JSONSchema] = None
clinical_history_schema: Optional[jschon.JSONSchema] = None
contact_schema: Optional[jschon.JSONSchema] = None
enums_schema: Optional[jschon.JSONSchema] = None
life_area_schema: Optional[jschon.JSONSchema] = None
life_areas_schema: Optional[jschon.JSONSchema] = None
life_area_value_schema: Optional[jschon.JSONSchema] = None
life_area_value_activity_schema: Optional[jschon.JSONSchema] = None
log_schema: Optional[jschon.JSONSchema] = None
mood_log_schema: Optional[jschon.JSONSchema] = None
mood_logs_schema: Optional[jschon.JSONSchema] = None
patient_schema: Optional[jschon.JSONSchema] = None
patient_identity_schema: Optional[jschon.JSONSchema] = None
patient_profile_schema: Optional[jschon.JSONSchema] = None
provider_identity_schema: Optional[jschon.JSONSchema] = None
referral_status_schema: Optional[jschon.JSONSchema] = None
regexes: Optional[jschon.JSONSchema] = None
safety_plan_schema: Optional[jschon.JSONSchema] = None
scheduled_activity_schema: Optional[jschon.JSONSchema] = None
scheduled_activities_schema: Optional[jschon.JSONSchema] = None
scheduled_assessments_schema: Optional[jschon.JSONSchema] = None
scheduled_assessment_schema: Optional[jschon.JSONSchema] = None
scheduled_item_schema: Optional[jschon.JSONSchema] = None
session_schema: Optional[jschon.JSONSchema] = None
sessions_schema: Optional[jschon.JSONSchema] = None
values_inventory_schema: Optional[jschon.JSONSchema] = None


def raise_for_invalid(*, schema: jschon.JSONSchema, document) -> None:
    """
    Verify a document matches a schema, raise an Error if it does not.
    """

    result = schema.evaluate(jschon.JSON(document))

    if not result.valid:
        raise ValueError(result.output("detailed"))


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
    "life_area_schema": "life-area.json",
    "life_areas_schema": "life-areas.json",
    "life_area_value_schema": "life-area-value.json",
    "life_area_value_activity_schema": "life-area-value-activity.json",
    "log_schema": "log.json",
    "mood_log_schema": "mood-log.json",
    "mood_logs_schema": "mood-logs.json",
    "patient_schema": "patient.json",
    "patient_identity_schema": "patient-identity.json",
    "patient_profile_schema": "patient-profile.json",
    "provider_identity_schema": "provider-identity.json",
    "referral_status_schema": "referral-status.json",
    "regexes": "datetime.json",
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


# Schemas need to be loaded in dependency order.
# The jschon method for doing this internally uses jschon.JSONSchema.loadf,
# which does not set an encoding and therefore failed for utf-8 schema content.
# We therefore use jschon.JSONSchema.loads with an explicit utf-8 encoding.
# Instead of attempting to manually maintain a loading order,
# we brute force loading generations of the dependency graph while ensuring we maintain progress.

CATALOG = jschon.create_catalog("2020-12")
schemas_remaining = [key_current for key_current in SCHEMAS.keys()]
progress = True
while progress:
    progress = False

    for schema_current in schemas_remaining:
        schema_path = Path(SCHEMA_DIR_PATH, SCHEMAS[schema_current])
        with open(schema_path, encoding="utf-8") as f:
            schema_json = json.loads(f.read())

        try:
            schema = jschon.JSONSchema(
                schema_json,
                catalog=CATALOG,
            )
        except:
            # Schema construction failed, try again in the next generation

            # Although construction of the schema failed,
            # jschon will have already placed the schema in the catalog.
            # Schemas dependent on the failed schema will therefore think it is available.
            # Remove it from the catalog so that dependent schemas fail quickly.
            CATALOG.del_schema(jschon.URI(schema_json["$id"]))
        else:
            # Schema was successfully created
            globals()[schema_current] = schema

            progress = True
            schemas_remaining.remove(schema_current)
