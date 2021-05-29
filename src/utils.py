import json
import pickle


def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_pickle(path):
    with open(path, 'rb') as handle:
        return pickle.load(handle)


def save_pickle(path, data):
    with open(path, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)


def load_configurations(paths):
    output = {}
    output["drop_data"] = load_json(paths["drop_data"])
    output["indicators"] = load_json(paths["indicators"])
    output["classifier"] = load_pickle(paths["classifier"])
    return output
