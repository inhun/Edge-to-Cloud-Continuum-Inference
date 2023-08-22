import json


def load_config(filename):
    config = {}
    with open(filename, 'r', encoding='utf-8') as f:
        config = json.load(f)

    return config




