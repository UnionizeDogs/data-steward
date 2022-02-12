import json
from haralyzer import HarParser, HarPage
import utility
from container import Container

def main():

    if utility.EXPORTS_PATH.exists():
        delete_directory(utility.EXPORTS_PATH)

    utility.EXPORTS_PATH.mkdir()

    if not utility.EXPORTS_WARNING_PATH.exists():
        with open(utility.EXPORTS_WARNING_PATH, "w") as warning_file:
            print('Do not save any changes to this directory, it will be overwritten by the next operation!',
                  file=warning_file)

    pages = []

    if utility.RESOURCES_PATH.exists():
        for item in utility.RESOURCES_PATH.iterdir():
            if item.is_file() and str(item).endswith('.har'):
                with open(item, 'r') as file:
                    pages.extend(HarParser(json.loads(file.read())).pages)

    container = Container(pages)

def delete_directory(target_path):
    if not target_path:
        raise Exception('Invalid target path provided!')

    for sub in target_path.iterdir():
        if sub.is_dir():
            delete_directory(sub)
        else:
            sub.unlink()
    target_path.rmdir()

main()