import sys
from pathlib import Path
from names_dataset import NameDataset
from unidecode import unidecode

PROJECT_PATH = Path(sys.path[0])
PROJECT_RULES_DEFAULT = PROJECT_PATH.joinpath('rules_default.json')
RESOURCES_PATH = PROJECT_PATH.joinpath('resources')
RESOURCES_RULES = RESOURCES_PATH.joinpath('rules.json')

EXPORTS_PATH = PROJECT_PATH.joinpath('exports')
EXPORTS_WARNING_PATH = EXPORTS_PATH.joinpath('___DO NOT SAVE HERE___.txt')

class Cache:
    NAME_DATASET = None

def hash_name(full_name):
    if full_name:
        return unidecode(full_name.replace(' ', '').lower())
    else:
        return None


def is_recognized_name(first_name, last_name):
    if not Cache.NAME_DATASET:
        Cache.NAME_DATASET = NameDataset()

    if first_name:
        name_dataset_result = Cache.NAME_DATASET.search(first_name.split(' ')[0])
        if name_dataset_result['first_name'] or name_dataset_result['last_name']:
            return True

    if last_name:
        name_dataset_result = Cache.NAME_DATASET.search(last_name.split(' ')[0])
        if name_dataset_result['first_name'] or name_dataset_result['last_name']:
            return True

    return False