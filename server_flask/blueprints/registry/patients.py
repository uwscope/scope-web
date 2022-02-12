import copy
import flask
import flask_json
import http
import logging
import pymongo.collection
import time

import fake
from request_context import request_context
import scope.database.patients
import scope.database.patient.clinical_history
import scope.database.patient.patient_profile
import scope.database.patient.safety_plan
import scope.database.patient.values_inventory

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

    result_document["clinicalHistory"] = scope.database.patient.clinical_history.get_clinical_history(
        collection=patient_collection
    )
    result_document["profile"] = scope.database.patient.patient_profile.get_patient_profile(
        collection=patient_collection
    )
    result_document["safetyPlan"] = scope.database.patient.safety_plan.get_safety_plan(
        collection=patient_collection
    )
    result_document["valuesInventory"] = scope.database.patient.values_inventory.get_values_inventory(
        collection=patient_collection
    )

    return result_document


@patients_blueprint.route("/patients", methods=["GET"])
@flask_json.as_json
def get_patients():
    context = request_context()

    time_call_start = time.perf_counter()

    # List of documents from the patients collection
    patients = scope.database.patients.get_patients(
        database=context.database,
    )

    time_call_patients = time.perf_counter()

    # TODO: Remove fake data generation when this is fully implemented
    # Ensure fake data exists for each patient
    for patient_current in patients:
        patient_id = patient_current["_set_id"]
        if patient_id not in FAKE_PATIENT_MAP:
            FAKE_PATIENT_MAP[patient_id] = fake.getFakePatient()
            FAKE_PATIENT_MAP[patient_id]["identity"]["identityId"] = patient_id

    # Populate a document to return.
    # Initially based on fields that were in the fake data.
    time_start_patients = time.perf_counter()
    time_per_patient = []
    patient_documents = []
    for patient_current in patients:
        patient_id = patient_current["_set_id"]
        patient_collection = context.database.get_collection(patient_current["collection"])

        patient_document_current = FAKE_PATIENT_MAP[patient_id]
        patient_document_current = _frankenfake_document(
            fake_document=patient_document_current,
            patient_collection=patient_collection,
        )

        patient_documents.append(patient_document_current)

        time_per_patient.append(time.perf_counter())

    time_call_end = time.perf_counter()

    print("Time Call Patients: {}".format(time_call_patients - time_call_start), flush=True)
    print("Time Start Patients: {}".format(time_start_patients - time_call_start), flush=True)
    for time_per_patient_current in time_per_patient:
        print("Time Patient: {}".format(time_per_patient_current - time_call_start), flush=True)
    print("Time Call End: {}".format(time_call_end - time_call_start), flush=True)

    # TODO: We should require that a "patient"
    #       always have a "profile" document that includes "name" and "mrn".
    #
    # For now, we explicitly filter on patients being "valid".
    patient_documents_filtered = []
    for patient_document_current in patient_documents:
        filter_pass = (
            ("identity" in patient_document_current) and
            ("identityId" in patient_document_current["identity"]) and
            ("profile" in patient_document_current) and
            ("name" in patient_document_current["profile"]) and
            ("mrn" in patient_document_current["profile"])
        )
        if filter_pass:
            patient_documents_filtered.append(patient_document_current)

    patient_documents = patient_documents_filtered

    # Transition code to establish a "sparse" representation
    patient_documents_sparse = [
        {
            "identity": {
                "_type": "identity",
                "identityId": patient_document_current["identity"]["identityId"],
                "name": patient_document_current["profile"]["name"]
            },
        }
        for patient_document_current in patient_documents
    ]

    return {
        "patients": patient_documents,
        "patientsSparse": patient_documents_sparse,
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
