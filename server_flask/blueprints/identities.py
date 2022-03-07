import flask
import flask_json

import authorization_utils
import request_context
import request_utils
import scope.database.patients
import scope.database.providers

identities_blueprint = flask.Blueprint(
    "identities_blueprint",
    __name__,
)


@identities_blueprint.route(
    "/identities",
    methods=["GET"],
)
@flask_json.as_json
def get_identities():
    context = request_context.authorization_unverified()

    authenticated_identities = authorization_utils.authenticated_identities(
        database=context.database
    )

    if not any(
        [
            authenticated_identities.patient_identity,
            authenticated_identities.provider_identity,
        ]
    ):
        request_utils.abort_not_authorized()

    result = {}
    if authenticated_identities.patient_identity:
        result[
            scope.database.patients.PATIENT_IDENTITY_DOCUMENT_TYPE
        ] = authenticated_identities.patient_identity
    if authenticated_identities.provider_identity:
        result[
            scope.database.providers.PROVIDER_IDENTITY_DOCUMENT_TYPE
        ] = authenticated_identities.provider_identity

    return result


@identities_blueprint.route(
    "/identities/patientIdentity",
    methods=["GET"],
)
@flask_json.as_json
def get_patient_identity():
    context = request_context.authorization_unverified()

    authenticated_identities = authorization_utils.authenticated_identities(
        database=context.database
    )

    if not authenticated_identities.patient_identity:
        request_utils.abort_not_authorized()

    return {
        scope.database.patients.PATIENT_IDENTITY_DOCUMENT_TYPE: authenticated_identities.patient_identity
    }


@identities_blueprint.route(
    "/identities/providerIdentity",
    methods=["GET"],
)
@flask_json.as_json
def get_provider_identity():
    context = request_context.authorization_unverified()

    authenticated_identities = authorization_utils.authenticated_identities(
        database=context.database
    )

    if not authenticated_identities.provider_identity:
        request_utils.abort_not_authorized()

    return {
        scope.database.providers.PROVIDER_IDENTITY_DOCUMENT_TYPE: authenticated_identities.provider_identity
    }
