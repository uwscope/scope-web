import copy
import flask
import flask_json
import pymongo.collection

import request_utils
from request_context import request_context
import scope.database.patient.case_reviews
import scope.database.patient.clinical_history
import scope.database.patient.patient_profile
import scope.database.patient.safety_plan
import scope.database.patient.sessions
import scope.database.patient.values_inventory
import scope.database.patients

patients_blueprint = flask.Blueprint(
    "patients_blueprint",
    __name__,
)


# # Transition code to establish a "sparse" representation
# patient_documents_sparse = [
#     {
#         "identity": {
#             "_type": "identity",
#             "identityId": patient_document_current["identity"]["identityId"],
#             "name": patient_document_current["profile"]["name"],
#             "MRN": patient_document_current["profile"]["MRN"],
#         },
#     }
#     for patient_document_current in patient_documents
# ]


def _construct_patient_document(
    *,
    patient_identity: dict,
    patient_collection: pymongo.collection.Collection,
) -> dict:
    patient_document = {}

    patient_document["_type"] = "patient"

    # Identity
    patient_document["identity"] = copy.deepcopy(patient_identity)

    # Profile
    profile = scope.database.patient.patient_profile.get_patient_profile(
        collection=patient_collection
    )
    if profile:
        patient_document["profile"] = profile

    # # Case reviews
    # case_reviews = scope.database.patient.case_reviews.get_case_reviews(
    #     collection=patient_collection
    # )
    # if case_reviews:
    #     patient_document["caseReviews"] = case_reviews

    # Clinical history
    clinical_history = scope.database.patient.clinical_history.get_clinical_history(
        collection=patient_collection
    )
    if clinical_history:
        patient_document["clinicalHistory"] = clinical_history

    # Safety plan
    safety_plan = scope.database.patient.safety_plan.get_safety_plan(
        collection=patient_collection
    )
    if safety_plan:
        patient_document["safetyPlan"] = safety_plan

    # Sessions
    sessions = scope.database.patient.sessions.get_sessions(
        collection=patient_collection
    )
    if sessions:
        patient_document["sessions"] = sessions

    # Values inventory
    values_inventory = scope.database.patient.values_inventory.get_values_inventory(
        collection=patient_collection
    )
    if values_inventory:
        patient_document["valuesInventory"] = values_inventory

    return patient_document


@patients_blueprint.route(
    "/patients",
    methods=["GET"],
)
@flask_json.as_json
def get_patients():
    # TODO require authentication

    context = request_context()
    database = context.database

    # List of documents from the patient identities collection
    patient_identities = scope.database.patients.get_patient_identities(
        database=context.database,
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
    # TODO: Require authentication

    context = request_context()
    database = context.database

    # List of documents from the patient identities collection
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
    )

    return {
        "patient": patient_document,
    }
