import flask
import flask_json

import request_context
import request_utils
import scope.database.providers

providers_blueprint = flask.Blueprint(
    "providers_blueprint",
    __name__,
)


@providers_blueprint.route(
    "/providers",
    methods=["GET"],
)
@flask_json.as_json
def get_providers():
    context = request_context.authorized_for_everything()
    database = context.database

    # List of documents from the provider identities collection
    provider_identities = scope.database.providers.get_provider_identities(
        database=database,
    )

    return {
        "providers": provider_identities,
    }


@providers_blueprint.route(
    "/provider/<string:provider_id>",
    methods=["GET"],
)
@flask_json.as_json
def get_provider(provider_id):
    context = request_context.authorized_for_everything()
    database = context.database

    # Document from the provider identities collection
    provider_identity = scope.database.providers.get_provider_identity(
        database=database,
        provider_id=provider_id,
    )
    if provider_identity is None:
        request_utils.abort_patient_not_found()

    return {
        "provider": provider_identity,
    }
