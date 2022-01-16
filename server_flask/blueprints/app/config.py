import flask
import flask_json
import http
import json
from pathlib import Path

APP_CONFIG_ASSESSMENTS_PATH = "./app_config/assessments"
APP_CONFIG_LIFE_AREAS_PATH = "./app_config/life_areas"
APP_CONFIG_RESOURCES_PATH = "./app_config/resources"

app_config_blueprint = flask.Blueprint(
    "app_config_blueprint", __name__, url_prefix="/app"
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
    assessments = []
    for path_current in Path(APP_CONFIG_ASSESSMENTS_PATH).iterdir():
        if path_current.match("*.json"):
            with open(path_current) as config_file:
                config_json = json.load(config_file)
                assessments.append(config_json)

    # Load life areas configurations
    life_areas = []
    for path_current in Path(APP_CONFIG_LIFE_AREAS_PATH).iterdir():
        if path_current.match("*.json"):
            with open(path_current) as config_file:
                config_json = json.load(config_file)
                life_areas.append(config_json)

    # Load resources configurations
    resources = []
    for path_current in Path(APP_CONFIG_RESOURCES_PATH).iterdir():
        if path_current.match("*.json"):
            with open(path_current) as config_file:
                config_json = json.load(config_file)
                resources.append(config_json)

    result = {
        "assessments": assessments,
        "lifeAreas": life_areas,
        "resources": resources,
    }

    return result, http.HTTPStatus.OK
