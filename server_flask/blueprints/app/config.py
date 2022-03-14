import flask
import flask_json
import http
import json
import random
from pathlib import Path


APP_CONFIG_ASSESSMENTS_PATH = "./app_config/assessments"
APP_CONFIG_LIFE_AREAS_PATH = "./app_config/life_areas"
APP_CONFIG_PATIENT_RESOURCES_PATH = "./app_config/patient_resources"
APP_CONFIG_REGISTRY_RESOURCES_PATH = "./app_config/registry_resources"
APP_QUOTES_PATH = "./app_config/quotes.json"


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
            with open(path_current, encoding="utf-8") as config_file:
                config_json = json.load(config_file)
                content_assessments.append(config_json)

    # Load life areas configurations
    content_life_areas = []
    for path_current in Path(APP_CONFIG_LIFE_AREAS_PATH).iterdir():
        if path_current.match("*.json"):
            with open(path_current, encoding="utf-8") as config_file:
                config_json = json.load(config_file)
                content_life_areas.append(config_json)

    # Load patient resources configurations
    content_patient_resources = []
    for path_current in Path(APP_CONFIG_PATIENT_RESOURCES_PATH).iterdir():
        if path_current.match("*.json"):
            with open(path_current, encoding="utf-8") as config_file:
                config_json = json.load(config_file)
                content_patient_resources.append(config_json)

    # Load registry resources configurations
    content_registry_resources = []
    for path_current in Path(APP_CONFIG_REGISTRY_RESOURCES_PATH).iterdir():
        if path_current.match("*.json"):
            with open(path_current, encoding="utf-8") as config_file:
                config_json = json.load(config_file)
                content_registry_resources.append(config_json)

    result = {
        "auth": {
            "poolid": flask.current_app.config["COGNITO_POOLID"],
            "clientid": flask.current_app.config["COGNITO_CLIENTID"],
        },
        "content": {
            "assessments": content_assessments,
            "lifeAreas": content_life_areas,
            "patientresources": content_patient_resources,
            "registryresources": content_registry_resources,
        },
    }

    return result


@app_config_blueprint.route(
    "/quote",
    methods=["GET"],
)
@flask_json.as_json
def get_app_quote():
    """
    Obtain a quote to be used by client.
    """

    quotes_path = Path(APP_QUOTES_PATH)

    # Load quotes configurations
    with open(quotes_path, encoding="utf-8") as quotes_file:
        quotes_json = json.load(quotes_file)

    return {
        "quote": random.choice(quotes_json),
    }
