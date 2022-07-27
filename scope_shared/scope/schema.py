import jschon
import json
from pathlib import Path
from typing import Optional

# Declare each schema in order to support code analysis/completion
activity_schema: Optional[jschon.JSONSchema] = None
activities_schema: Optional[jschon.JSONSchema] = None
activity_log_schema: Optional[jschon.JSONSchema] = None
activity_logs_schema: Optional[jschon.JSONSchema] = None
app_config_schema: Optional[jschon.JSONSchema] = None
app_content_config_schema: Optional[jschon.JSONSchema] = None
assessment_schema: Optional[jschon.JSONSchema] = None
assessments_schema: Optional[jschon.JSONSchema] = None
assessment_content_schema: Optional[jschon.JSONSchema] = None
assessment_contents_schema: Optional[jschon.JSONSchema] = None
assessment_log_schema: Optional[jschon.JSONSchema] = None
assessment_logs_schema: Optional[jschon.JSONSchema] = None
case_review_schema: Optional[jschon.JSONSchema] = None
case_reviews_schema: Optional[jschon.JSONSchema] = None
clinical_history_schema: Optional[jschon.JSONSchema] = None
contact_schema: Optional[jschon.JSONSchema] = None
document_schema: Optional[jschon.JSONSchema] = None
enums_schema: Optional[jschon.JSONSchema] = None
life_area_content_schema: Optional[jschon.JSONSchema] = None
life_area_contents_schema: Optional[jschon.JSONSchema] = None
life_area_value_schema: Optional[jschon.JSONSchema] = None
life_area_value_activity_schema: Optional[jschon.JSONSchema] = None
log_schema: Optional[jschon.JSONSchema] = None
mood_log_schema: Optional[jschon.JSONSchema] = None
mood_logs_schema: Optional[jschon.JSONSchema] = None
patient_schema: Optional[jschon.JSONSchema] = None
patients_schema: Optional[jschon.JSONSchema] = None
patient_identity_schema: Optional[jschon.JSONSchema] = None
patient_identities_schema: Optional[jschon.JSONSchema] = None
patient_profile_schema: Optional[jschon.JSONSchema] = None
patient_summary_schema: Optional[jschon.JSONSchema] = None
populate_config_schema: Optional[jschon.JSONSchema] = None
populate_config_account_schema: Optional[jschon.JSONSchema] = None
provider_identity_schema: Optional[jschon.JSONSchema] = None
provider_identities_schema: Optional[jschon.JSONSchema] = None
referral_status_schema: Optional[jschon.JSONSchema] = None
regexes: Optional[jschon.JSONSchema] = None
resource_content_schema: Optional[jschon.JSONSchema] = None
resource_contents_schema: Optional[jschon.JSONSchema] = None
safety_plan_schema: Optional[jschon.JSONSchema] = None
scheduled_activity_schema: Optional[jschon.JSONSchema] = None
scheduled_activities_schema: Optional[jschon.JSONSchema] = None
scheduled_assessments_schema: Optional[jschon.JSONSchema] = None
scheduled_assessment_schema: Optional[jschon.JSONSchema] = None
scheduled_item_schema: Optional[jschon.JSONSchema] = None
sentinel_schema: Optional[jschon.JSONSchema] = None
session_schema: Optional[jschon.JSONSchema] = None
sessions_schema: Optional[jschon.JSONSchema] = None
values_inventory_schema: Optional[jschon.JSONSchema] = None


# Declare files from which to populate each schema
SCHEMA_DIR_PATH = Path(Path(__file__).parent, "./schemas")
SCHEMAS = {
    # api,
    # Corresponds to flask input and output expectations
    "app_config_schema": "api/app-config.json",
    "app_content_config_schema": "api/app-content-config.json",
    "patient_schema": "api/patient.json",
    "patients_schema": "api/patients.json",
    "patient_summary_schema": "api/patient-summary.json",
    # config,
    # Corresponds to flask and aws config schemas
    "assessment_content_schema": "config/assessment-content.json",
    "assessment_contents_schema": "config/assessment-contents.json",
    "life_area_content_schema": "config/life-area-content.json",
    "life_area_contents_schema": "config/life-area-contents.json",
    "resource_content_schema": "config/resource-content.json",
    "resource_contents_schema": "config/resource-contents.json",
    # documents,
    # Corresponds to document(s) that live in database
    "activity_schema": "documents/activity.json",
    "activities_schema": "documents/activities.json",
    "activity_log_schema": "documents/activity-log.json",
    "activity_logs_schema": "documents/activity-logs.json",
    "assessment_schema": "documents/assessment.json",
    "assessments_schema": "documents/assessments.json",
    "assessment_log_schema": "documents/assessment-log.json",
    "assessment_logs_schema": "documents/assessment-logs.json",
    "case_review_schema": "documents/case-review.json",
    "case_reviews_schema": "documents/case-reviews.json",
    "clinical_history_schema": "documents/clinical-history.json",
    "mood_log_schema": "documents/mood-log.json",
    "mood_logs_schema": "documents/mood-logs.json",
    "patient_identity_schema": "documents/patient-identity.json",
    "patient_identities_schema": "documents/patient-identities.json",
    "patient_profile_schema": "documents/patient-profile.json",
    "provider_identity_schema": "documents/provider-identity.json",
    "provider_identities_schema": "documents/provider-identities.json",
    "safety_plan_schema": "documents/safety-plan.json",
    "scheduled_activity_schema": "documents/scheduled-activity.json",
    "scheduled_activities_schema": "documents/scheduled-activities.json",
    "scheduled_assessments_schema": "documents/scheduled-assessments.json",
    "scheduled_assessment_schema": "documents/scheduled-assessment.json",
    "sentinel_schema": "documents/sentinel.json",
    "session_schema": "documents/session.json",
    "sessions_schema": "documents/sessions.json",
    "values_inventory_schema": "documents/values-inventory.json",
    # documents/utils,
    # Contains subschemas referenced (using $ref) by schemas in documents
    "contact_schema": "documents/utils/contact.json",
    "life_area_value_schema": "documents/utils/life-area-value.json",
    "life_area_value_activity_schema": "documents/utils/life-area-value-activity.json",
    "log_schema": "documents/utils/log.json",
    "referral_status_schema": "documents/utils/referral-status.json",
    "scheduled_item_schema": "documents/utils/scheduled-item.json",
    # populate,
    # Corresponds to json schemas used by populate scripts
    "populate_config_schema": "populate/populate-config.json",
    # populate/utils,
    # Contains subschemas referenced (using $ref) by schemas in populate
    "populate_config_account_schema": "populate/utils/populate-config-account.json",
    # utils,
    # Contains helper enums and regexes used by other json schemas
    "enums_schema": "utils/enums.json",
    "regexes": "utils/datetime.json",
    "document_schema": "document.json",
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
        except (
            jschon.exceptions.CatalogError,
            TypeError,
        ):
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

# If schemas remain, they failed to parse
if len(schemas_remaining) > 0:
    for schema_current in schemas_remaining:
        schema_path = Path(SCHEMA_DIR_PATH, SCHEMAS[schema_current])
        with open(schema_path, encoding="utf-8") as f:
            schema_json = json.loads(f.read())

        try:
            schema = jschon.JSONSchema(
                schema_json,
                catalog=CATALOG,
            )
        except Exception as e:
            print("Error in schema: {}".format(schema_path))
            print(e)

    raise ValueError("Invalid schema detected")
