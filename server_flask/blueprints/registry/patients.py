import copy
import flask
import flask_json
import http
import pymongo.collection

import fake
from request_context import request_context
import scope.database.patients
import scope.database.patient.patient_profile


FAKE_PATIENT_MAP = {}

patients_blueprint = flask.Blueprint(
    "patients_blueprint", __name__,
)


def _frankenfake_document(
    *,
    fake_document: dict,
    patient_collection: pymongo.collection.Collection
) -> dict:
    result_document = copy.deepcopy(fake_document)

    # result_document["profile"] = scope.database.patient.patient_profile.get_patient_profile(
    #     collection=patient_collection
    # )

    return result_document


@patients_blueprint.route("/patients", methods=["GET"])
@flask_json.as_json
def get_patients():
    context = request_context()

    # List of documents from the patients collection
    patients = scope.database.patients.get_patients(
        database=context.database,
    )

    # TODO: Remove fake data generation when this is fully implemented
    # Ensure fake data exists for each patient
    for patient_current in patients:
        patient_id = patient_current["_set_id"]
        if patient_id not in FAKE_PATIENT_MAP:
            FAKE_PATIENT_MAP[patient_id] = fake.getFakePatient()
            FAKE_PATIENT_MAP[patient_id]["identity"]["identityId"] = patient_id

    # Populate a document to return.
    # Initially based on fields that were in the fake data.
    patient_documents = {}
    for patient_current in patients:
        patient_id = patient_current["_set_id"]
        patient_collection = context.database.get_collection(patient_current["collection"])

        patient_document_current = FAKE_PATIENT_MAP[patient_id]
        patient_document_current = _frankenfake_document(
            fake_document=patient_document_current,
            patient_collection=patient_collection,
        )

        patient_documents[patient_id] = patient_document_current

    return {
        "patients": list(patient_documents.values())
    }


@patients_blueprint.route(
    "/patient/<string:patient_id>",
    methods=["GET"],
)
@flask_json.as_json
def get_patient(patient_id):
    # TODO: Require authentication

    context = request_context()

    # Use patient ID to confirm validity and obtain collection
    # TODO: As part of authentication, determine if we can cache this.
    #       Otherwise, maybe an annotation or enhance context to reduce code repetition.
    patient_document = scope.database.patients.get_patient(
        database=context.database,
        patient_id=patient_id,
    )
    if patient_document is None:
        flask.abort(http.HTTPStatus.NOT_FOUND)

    # Obtain patient collection
    patient_collection = context.database.get_collection(patient_document["collection"])

    # TODO: Remove fake data generation when this is fully implemented
    # Ensure fake data exists for each patient
    if patient_id not in FAKE_PATIENT_MAP:
        FAKE_PATIENT_MAP[patient_id] = fake.getFakePatient()
        FAKE_PATIENT_MAP[patient_id]["identity"]["identityId"] = patient_id

    # Populate a document to return.
    # Initially based on fields that were in the fake data.
    patient_document = FAKE_PATIENT_MAP[patient_id]
    patient_document = _frankenfake_document(
        fake_document=patient_document,
        patient_collection=patient_collection,
    )

    return patient_document
