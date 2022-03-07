import flask
import pymongo.collection
import pymongo.database
from typing import cast

import authorization_utils
import request_utils
import scope.database.patients


class RequestContext:
    @property
    def database(self) -> pymongo.database.Database:
        # noinspection PyUnresolvedReferences
        return cast(
            pymongo.database.Database,
            flask.current_app.database_must_not_be_directly_accessed,
        )

    def patient_collection(self, *, patient_id: str) -> pymongo.collection.Collection:
        # Use patient ID to confirm validity and obtain collection
        # TODO: As part of authentication, determine if we can cache this.
        #       Otherwise, maybe an annotation or enhance context to reduce code repetition.
        patient_identity_document = scope.database.patients.get_patient_identity(
            database=self.database,
            patient_id=patient_id,
        )
        if patient_identity_document is None:
            request_utils.abort_patient_not_found()

        # Obtain patient collection
        patient_collection = self.database.get_collection(
            patient_identity_document["collection"]
        )

        return patient_collection


def authorized_for_everything() -> RequestContext:
    request_context = RequestContext()

    if flask.current_app.config.get("AUTHORIZATION_DISABLED_FOR_TESTING", False):
        return request_context

    authenticated_identities = authorization_utils.authenticated_identities(
        database=request_context.database
    )

    authorized = False

    # Providers have access to all patients.
    if authenticated_identities.provider_identity:
        authorized = True

    if not authorized:
        request_utils.abort_not_authorized()

    return request_context


def authorized_for_patient(patient_id: str) -> RequestContext:
    request_context = RequestContext()

    if flask.current_app.config.get("AUTHORIZATION_DISABLED_FOR_TESTING", False):
        return request_context

    authenticated_identities = authorization_utils.authenticated_identities(
        database=request_context.database
    )

    authorized = False

    # Providers have access to all patients.
    if authenticated_identities.provider_identity:
        authorized = True

    # A patient has access to their own data.
    if authenticated_identities.patient_identity:
        authenticated_patient_id = authenticated_identities.patient_identity[
            scope.database.patients.PATIENT_IDENTITY_SEMANTIC_SET_ID
        ]

        if authenticated_patient_id == patient_id:
            authorized = True

    if not authorized:
        request_utils.abort_not_authorized()

    return request_context


def authorization_unverified() -> RequestContext:
    return RequestContext()
