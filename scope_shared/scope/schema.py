import pathlib

from jschon import URI, JSONSchema, create_catalog

schema_dir = pathlib.Path(__file__).parent / "schemas"

catalog = create_catalog("2020-12")

# NOTE: For the subschemas to work, the schemas must be loaded in either "$ref" dependency order, or the base URI-to-directory mapping on the catalog needs to be set up (`.add_directory`) as shown below.

catalog.add_directory(URI("https://uwscope.org/schemas/"), schema_dir)


patient_schema = JSONSchema.loadf(schema_dir / "patient.json")

# TODO: Load other schemas below as API endpoints are added.
identity_schema = JSONSchema.loadf(schema_dir / "identity.json")
patient_profile_schema = JSONSchema.loadf(schema_dir / "patient-profile.json")
values_inventory_schema = JSONSchema.loadf(schema_dir / "values-inventory.json")
clinical_history_schema = JSONSchema.loadf(schema_dir / "clinical-history.json")
safety_plan_schema = JSONSchema.loadf(schema_dir / "safety-plan.json")
sessions_schema = JSONSchema.loadf(schema_dir / "sessions.json")
session_schema = JSONSchema.loadf(schema_dir / "session.json")
case_reviews_schema = JSONSchema.loadf(schema_dir / "case-reviews.json")
case_review_schema = JSONSchema.loadf(schema_dir / "case-review.json")
assessment_logs_schema = JSONSchema.loadf(schema_dir / "assessment-logs.json")
assessment_log_schema = JSONSchema.loadf(schema_dir / "assessment-log.json")
activities_schema = JSONSchema.loadf(schema_dir / "activities.json")
activity_schema = JSONSchema.loadf(schema_dir / "activity.json")
