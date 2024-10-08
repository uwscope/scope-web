import copy
import flask
import flask_json
import pymongo.collection

import request_utils
import request_context
import scope.database.collection_utils
import scope.database.patient.activities
import scope.database.patient.activity_logs
import scope.database.patient.activity_schedules
import scope.database.patient.assessment_logs
import scope.database.patient.assessments
import scope.database.patient.case_reviews
import scope.database.patient.clinical_history
import scope.database.patient.mood_logs
import scope.database.patient.patient_profile
import scope.database.patient.review_marks
import scope.database.patient.safety_plan
import scope.database.patient.scheduled_activities
import scope.database.patient.scheduled_assessments
import scope.database.patient.sessions
import scope.database.patient.values
import scope.database.patient.values_inventory
import scope.database.patients

patients_blueprint = flask.Blueprint(
    "patients_blueprint",
    __name__,
)


def _construct_patient_document(
    *,
    patient_identity: dict,
    patient_collection: pymongo.collection.Collection,
    include_complete_details: bool = True,
) -> dict:
    patient_document = {}

    patient_document["_type"] = "patient"

    # Identity
    patient_document["identity"] = copy.deepcopy(patient_identity)

    if not include_complete_details:
        # Get multiple document types simultaneously
        documents_by_type = scope.database.collection_utils.get_multiple_types(
            collection=patient_collection,
            singleton_types=[
                scope.database.patient.clinical_history.DOCUMENT_TYPE,
                scope.database.patient.patient_profile.DOCUMENT_TYPE,
            ],
            set_types=[],  # No set types
        )

        # Clinical History
        patient_document["clinicalHistory"] = documents_by_type[
            scope.database.patient.clinical_history.DOCUMENT_TYPE
        ]

        # Profile
        patient_document["profile"] = documents_by_type[
            scope.database.patient.patient_profile.DOCUMENT_TYPE
        ]

        return patient_document

    # Get multiple document types simultaneously
    documents_by_type = scope.database.collection_utils.get_multiple_types(
        collection=patient_collection,
        singleton_types=[
            scope.database.patient.clinical_history.DOCUMENT_TYPE,
            scope.database.patient.patient_profile.DOCUMENT_TYPE,
            scope.database.patient.safety_plan.DOCUMENT_TYPE,
            scope.database.patient.values_inventory.DOCUMENT_TYPE,
        ],
        set_types=[
            scope.database.patient.activities.DOCUMENT_TYPE,
            scope.database.patient.activity_logs.DOCUMENT_TYPE,
            scope.database.patient.activity_schedules.DOCUMENT_TYPE,
            scope.database.patient.assessments.DOCUMENT_TYPE,
            scope.database.patient.assessment_logs.DOCUMENT_TYPE,
            scope.database.patient.case_reviews.DOCUMENT_TYPE,
            scope.database.patient.mood_logs.DOCUMENT_TYPE,
            scope.database.patient.review_marks.DOCUMENT_TYPE,
            scope.database.patient.scheduled_activities.DOCUMENT_TYPE,
            scope.database.patient.sessions.DOCUMENT_TYPE,
            scope.database.patient.values.DOCUMENT_TYPE,
        ],
    )

    # Activities
    patient_document["activities"] = documents_by_type[
        scope.database.patient.activities.DOCUMENT_TYPE
    ]

    # Activity Logs
    patient_document["activityLogs"] = documents_by_type[
        scope.database.patient.activity_logs.DOCUMENT_TYPE
    ]

    # Activity Schedules
    patient_document["activitySchedules"] = documents_by_type[
        scope.database.patient.activity_schedules.DOCUMENT_TYPE
    ]

    # Assessments
    patient_document["assessments"] = documents_by_type[
        scope.database.patient.assessments.DOCUMENT_TYPE
    ]

    # Assessment Logs
    patient_document["assessmentLogs"] = documents_by_type[
        scope.database.patient.assessment_logs.DOCUMENT_TYPE
    ]

    # Case Reviews
    patient_document["caseReviews"] = documents_by_type[
        scope.database.patient.case_reviews.DOCUMENT_TYPE
    ]

    # Clinical History
    patient_document["clinicalHistory"] = documents_by_type[
        scope.database.patient.clinical_history.DOCUMENT_TYPE
    ]

    # Mood Logs
    patient_document["moodLogs"] = documents_by_type[
        scope.database.patient.mood_logs.DOCUMENT_TYPE
    ]

    # Profile
    patient_document["profile"] = documents_by_type[
        scope.database.patient.patient_profile.DOCUMENT_TYPE
    ]

    # Review Marks
    patient_document["reviewMarks"] = documents_by_type[
        scope.database.patient.review_marks.DOCUMENT_TYPE
    ]

    # Safety Plan
    patient_document["safetyPlan"] = documents_by_type[
        scope.database.patient.safety_plan.DOCUMENT_TYPE
    ]

    # Scheduled Assessments
    # TODO: this access currently modifies documents, cannot be replaced
    patient_document[
        "scheduledAssessments"
    ] = scope.database.patient.scheduled_assessments.get_scheduled_assessments(
        collection=patient_collection
    )

    # Scheduled Activities
    patient_document["scheduledActivities"] = documents_by_type[
        scope.database.patient.scheduled_activities.DOCUMENT_TYPE
    ]

    # Sessions
    patient_document["sessions"] = documents_by_type[
        scope.database.patient.sessions.DOCUMENT_TYPE
    ]

    # Values
    patient_document["values"] = documents_by_type[
        scope.database.patient.values.DOCUMENT_TYPE
    ]

    # Values Inventory
    patient_document["valuesInventory"] = documents_by_type[
        scope.database.patient.values_inventory.DOCUMENT_TYPE
    ]

    return patient_document


@patients_blueprint.route(
    "/patients",
    methods=["GET"],
)
@flask_json.as_json
def get_patients():
    context = request_context.authorized_for_everything()
    database = context.database

    # List of documents from the patient identities collection
    patient_identities = scope.database.patients.get_patient_identities(
        database=database,
    )

    # Construct a full patient document for each
    patient_documents = []
    for patient_identity_current in patient_identities:
        patient_collection = database.get_collection(
            patient_identity_current["collection"]
        )

        patient_documents.append(
            _construct_patient_document(
                patient_identity=patient_identity_current,
                patient_collection=patient_collection,
                include_complete_details=False,
            )
        )

    return {
        "patients": patient_documents,
    }


@patients_blueprint.route(
    "/patient/<string:patient_id>",
    methods=["GET"],
)
@flask_json.as_json
def get_patient(patient_id):
    context = request_context.authorized_for_patient(patient_id=patient_id)
    database = context.database

    # Document from the patient identities collection
    patient_identity = scope.database.patients.get_patient_identity(
        database=context.database,
        patient_id=patient_id,
    )
    if patient_identity is None:
        request_utils.abort_patient_not_found()

    # Construct a full patient document
    patient_collection = database.get_collection(patient_identity["collection"])

    patient_document = _construct_patient_document(
        patient_identity=patient_identity,
        patient_collection=patient_collection,
        include_complete_details=True,
    )

    return {
        "patient": patient_document,
    }


@patients_blueprint.route(
    "/patientidentities",
    methods=["GET"],
)
@flask_json.as_json
def get_patient_identities():
    context = request_context.authorized_for_everything()
    database = context.database

    # List of documents from the patient identities collection
    patient_identities = scope.database.patients.get_patient_identities(
        database=database,
    )

    # Validate and normalize the response
    patient_identities = request_utils.set_get_response_validate(
        documents=patient_identities,
    )

    return {"patientidentities": patient_identities}
