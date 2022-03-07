import copy
import dataclasses
import pprint
import pymongo.database
import flask
import flask_json
import jwt
import re
from typing import Optional

from request_context import request_context
import request_utils
import scope.database.patients
import scope.database.providers

identity_blueprint = flask.Blueprint(
    "identity_blueprint",
    __name__,
)


@dataclasses.dataclass(frozen=True)
class VerifiedIdentities:
    patient_identity: Optional[str]
    provider_identity: Optional[str]


def _hot_mess_code(
    *,
    database: pymongo.database.Database,
) -> VerifiedIdentities:
    headers = flask.request.headers
    if "Authorization" not in headers:
        request_utils.abort_authorization_required()

    authorization_header = flask.request.headers["Authorization"]
    if not re.fullmatch("Bearer ([^\\s]+)", authorization_header):
        request_utils.abort_authorization_required()

    authorization_token = authorization_header.split()[1]

    pool_id = flask.current_app.config["COGNITO_POOLID"]
    pool_region = pool_id.split("_")[0]
    pool_client_id = flask.current_app.config["COGNITO_CLIENTID"]

    token_issuer = "https://cognito-idp.{region}.amazonaws.com/{userPoolId}".format(
        region=pool_region,
        userPoolId=pool_id,
    )

    jwks_url = "{tokenIssuer}/.well-known/jwks.json".format(
        tokenIssuer=token_issuer
    )

    jwks_client = jwt.PyJWKClient(jwks_url)
    signing_key = jwks_client.get_signing_key_from_jwt(authorization_token)

    pprint.pprint(signing_key)
    print("", flush=True)

    try:
        authorization_data = jwt.decode(
            jwt=authorization_token,
            key=signing_key.key,
            algorithms=["RS256"],
            audience=pool_client_id,
            iss=token_issuer,
            options={
                "verify_aud": True,
                "verify_exp": True,
                "verify_iss": True,
            }
        )
    except jwt.exceptions.InvalidTokenError:
        request_utils.abort_authorization_required()

    if authorization_data["token_use"] != "id":
        request_utils.abort_authorization_required()


    verified_cognito_id = authorization_data["sub"]



    verified_patient_identity = None
    patient_identities = scope.database.patients.get_patient_identities(
        database=database
    )
    for patient_identity_current in patient_identities:
        account_current = patient_identity_current.get("cognitoAccount", {})
        cognito_id_current = account_current.get("cognitoId", None)

        if cognito_id_current == verified_cognito_id:
            verified_patient_identity = patient_identity_current


    verified_provider_identity = None
    provider_identities = scope.database.providers.get_provider_identities(
        database=database
    )
    for provider_identity_current in provider_identities:
        account_current = provider_identity_current.get("cognitoAccount", {})
        cognito_id_current = account_current.get("cognitoId", None)

        if cognito_id_current == verified_cognito_id:
            verified_provider_identity = provider_identity_current

    return VerifiedIdentities(
        patient_identity=verified_patient_identity,
        provider_identity=verified_provider_identity,
    )


@identity_blueprint.route(
    "/identities",
    methods=["GET"],
)
@flask_json.as_json
def get_identities():
    context = request_context()

    verified_identities = _hot_mess_code(database=context.database)

    if not any([
        verified_identities.patient_identity,
        verified_identities.provider_identity,
    ]):
        request_utils.abort_authorization_required()

    result = {}
    if verified_identities.patient_identity:
        result[scope.database.patients.PATIENT_IDENTITY_DOCUMENT_TYPE] = verified_identities.patient_identity
    if verified_identities.provider_identity:
        result[scope.database.providers.PROVIDER_IDENTITY_DOCUMENT_TYPE] = verified_identities.provider_identity

    return result


@identity_blueprint.route(
    "/identities/patientIdentity",
    methods=["GET"],
)
@flask_json.as_json
def get_patient_identity():
    context = request_context()

    verified_identities = _hot_mess_code(database=context.database)

    if not verified_identities.patient_identity:
        request_utils.abort_authorization_required()

    return {
        scope.database.patients.PATIENT_IDENTITY_DOCUMENT_TYPE: verified_identities.patient_identity
    }


@identity_blueprint.route(
    "/identities/providerIdentity",
    methods=["GET"],
)
@flask_json.as_json
def get_provider_identity():
    context = request_context()

    verified_identities = _hot_mess_code(database=context.database)

    if not verified_identities.provider_identity:
        request_utils.abort_authorization_required()

    return {
        scope.database.providers.PROVIDER_IDENTITY_DOCUMENT_TYPE: verified_identities.provider_identity
    }
