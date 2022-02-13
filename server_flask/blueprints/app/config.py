import flask
import flask_json
import http
import json
from pathlib import Path

APP_CONFIG_ASSESSMENTS_PATH = "./app_config/assessments"
APP_CONFIG_LIFE_AREAS_PATH = "./app_config/life_areas"
APP_CONFIG_RESOURCES_PATH = "./app_config/resources"

app_config_blueprint = flask.Blueprint(
    "app_config_blueprint",
    __name__,
)


@app_config_blueprint.route(
    "/config",
    methods=["GET"],
)
@flask_json.as_json
def get_app_config():
    """
    Obtain application configuration to be used by client.
    """

    # Load assessments configurations
    content_assessments = []
    for path_current in Path(APP_CONFIG_ASSESSMENTS_PATH).iterdir():
        if path_current.match("*.json"):
            with open(path_current) as config_file:
                config_json = json.load(config_file)
                content_assessments.append(config_json)

    # Load life areas configurations
    content_life_areas = []
    for path_current in Path(APP_CONFIG_LIFE_AREAS_PATH).iterdir():
        if path_current.match("*.json"):
            with open(path_current) as config_file:
                config_json = json.load(config_file)
                content_life_areas.append(config_json)

    # Load resources configurations
    content_resources = []
    for path_current in Path(APP_CONFIG_RESOURCES_PATH).iterdir():
        if path_current.match("*.json"):
            with open(path_current) as config_file:
                config_json = json.load(config_file)
                content_resources.append(config_json)

    result = {
        "auth": {
            "poolid": flask.current_app.config["COGNITO_POOLID"],
            "clientid": flask.current_app.config["COGNITO_CLIENTID"],
        },
        "content": {
            "assessments": content_assessments,
            "lifeAreas": content_life_areas,
            "resources": content_resources,
        },
    }

    return result, http.HTTPStatus.OK
