import pymongo

import scope.config
import scope.database.collection_utils as collection_utils
import scope.database.patient.activities
import scope.database.patient.activity_logs
import scope.database.patient.activity_schedules
import scope.database.patient.assessment_logs
import scope.database.patient.assessments
import scope.database.patient.case_reviews
import scope.database.patient.clinical_history
import scope.database.patient.mood_logs
import scope.database.patient.patient_profile
import scope.database.patient.safety_plan
import scope.database.patient.scheduled_activities
import scope.database.patient.scheduled_assessments
import scope.database.patient.sessions
import scope.database.patient.values
import scope.database.patient.values_inventory
import scope.database.patients
import scope.schema
import tests.testing_config

from blueprints.registry.patients import _construct_patient_document

TESTING_CONFIGS = tests.testing_config.ALL_CONFIGS

QUERY_PATIENTS = "patients"
QUERY_PATIENT = "patient/{patient_id}"
QUERY_PATIENTIDENTITIES = "patientidentities"


def test_patient_construct_patient_document(
    database_client: pymongo.database.Database,
):
    """
    Test that collection_utils.get_multiple_types is producing equivalent results.
    """

    # List of documents from the patient identities collection
    patient_identities = scope.database.patients.get_patient_identities(
        database=database_client,
    )

    # Construct a full patient document for each
    for patient_identity_current in patient_identities:
        patient_collection_current = database_client.get_collection(
            patient_identity_current["collection"]
        )

        document_constructed = _construct_patient_document(
            patient_identity=patient_identity_current,
            patient_collection=patient_collection_current,
        )

        assert document_constructed == {
            "_type": "patient",
            "identity": patient_identity_current,
            "activities": scope.database.patient.activities.get_activities(
                collection=patient_collection_current
            ),
            "activityLogs": scope.database.patient.activity_logs.get_activity_logs(
                collection=patient_collection_current
            ),
            "activitySchedules": scope.database.patient.activity_schedules.get_activity_schedules(
                collection=patient_collection_current
            ),
            "assessments": scope.database.patient.assessments.get_assessments(
                collection=patient_collection_current
            ),
            "assessmentLogs": scope.database.patient.assessment_logs.get_assessment_logs(
                collection=patient_collection_current
            ),
            "caseReviews": scope.database.patient.case_reviews.get_case_reviews(
                collection=patient_collection_current
            ),
            "clinicalHistory": scope.database.patient.clinical_history.get_clinical_history(
                collection=patient_collection_current
            ),
            "moodLogs": scope.database.patient.mood_logs.get_mood_logs(
                collection=patient_collection_current
            ),
            "profile": scope.database.patient.patient_profile.get_patient_profile(
                collection=patient_collection_current
            ),
            "safetyPlan": scope.database.patient.safety_plan.get_safety_plan(
                collection=patient_collection_current
            ),
            "scheduledAssessments": scope.database.patient.scheduled_assessments.get_scheduled_assessments(
                collection=patient_collection_current
            ),
            "scheduledActivities": scope.database.patient.scheduled_activities.get_scheduled_activities(
                collection=patient_collection_current
            ),
            "sessions": scope.database.patient.sessions.get_sessions(
                collection=patient_collection_current
            ),
            "values": scope.database.patient.values.get_values(
                collection=patient_collection_current
            ),
            "valuesInventory": scope.database.patient.values_inventory.get_values_inventory(
                collection=patient_collection_current
            ),
        }
