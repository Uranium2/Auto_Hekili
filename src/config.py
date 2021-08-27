import json
import os.path

import pydirectinput

from src.utils import get_key_mapping


def load_json_save():
    path = "config\\config.json"
    if not os.path.isfile(path):
        with open(path, "w+") as outfile:
            json.dump(
                {"config_path": path, "Class": "Death_Knight_Blood"},
                outfile,
                indent=4,
                sort_keys=True,
            )

    with open(path, "r") as f:
        config = json.load(f)
    return config


def save_config(config):
    with open(config["config_path"], "w+") as outfile:
        json.dump(config, outfile, indent=4, sort_keys=True)


def edit_config(key, value, config):
    config[key] = value
    save_config(config)


def load_config():
    pydirectinput.PAUSE = False
    config = load_json_save()
    get_key_mapping()  # To generate json if not exist
    return config
