import flask
import flask_json
import http
import json
import random
from pathlib import Path


APP_CONFIG_ASSESSMENTS_PATH = "./app_config/assessments"
APP_CONFIG_LIFE_AREAS_PATH = "./app_config/life_areas"
APP_CONFIG_RESOURCES_PATH = "./app_config/resources"
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
    with open(quotes_path) as quotes_file:
        quotes_json = json.load(quotes_file)

    return {
        "quote": random.choice(quotes_json),
    }
