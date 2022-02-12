import sys
from pathlib import Path
from names_dataset import NameDataset
from unidecode import unidecode

NAME_DATASET_ENABLED = True

if NAME_DATASET_ENABLED:
    NAME_DATASET = NameDataset()
else:
    NAME_DATASET = None

PROJECT_PATH = Path(sys.path[0])
RESOURCES_PATH = PROJECT_PATH.joinpath('resources')
RESOURCES_NAME_RULES = RESOURCES_PATH.joinpath('name_rules.json')

EXPORTS_PATH = PROJECT_PATH.joinpath('exports')
EXPORTS_WARNING_PATH = EXPORTS_PATH.joinpath('___DO NOT SAVE HERE___.txt')


def hash_name(full_name):
    return unidecode(full_name.replace(' ', '').lower())


def is_recognized_name(first_name, last_name):
    if not NAME_DATASET_ENABLED:
        return True

    if first_name:
        name_dataset_result = NAME_DATASET.search(first_name.split(' ')[0])
        if name_dataset_result['first_name'] or name_dataset_result['last_name']:
            return True

    if last_name:
        name_dataset_result = NAME_DATASET.search(last_name.split(' ')[0])
        if name_dataset_result['first_name'] or name_dataset_result['last_name']:
            return True

    return False