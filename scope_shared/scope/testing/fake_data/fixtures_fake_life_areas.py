import json
from pathlib import Path

APP_CONFIG_LIFE_AREAS_PATH = Path(__file__, "../../../../../server_flask/app_config/life_areas")

# TODO: still unclear how to handle references

def fake_life_areas_factory() -> dict:
    fake_life_areas = {}

    for path_current in Path(APP_CONFIG_LIFE_AREAS_PATH).iterdir():
        if path_current.match("*.json"):
            with open(path_current) as config_file:
                config_json = json.load(config_file)
                fake_life_areas[config_json["id"]] = config_json

    return fake_life_areas
