import json
import utility
from employee_element import EmployeeElement
from employee import Employee

DAYFORCE_URL_FRAGMENT = '.dayforcehcm.com'
SLACK_URL_FRAGMENT = '.slack.com'

class Container:

    def __init__(self, pages):
        self.urls = []
        self.employee_elements = []
        self.employees = []
        self.name_rules = None
        self.name_aliases = []
        self.errors = []

        if utility.RESOURCES_NAME_RULES.exists():
            with open(utility.RESOURCES_NAME_RULES, 'r') as name_rules_raw:
                self.name_rules = json.loads(name_rules_raw.read())
                for alias in self.name_rules['aliases']:
                    for alias_variation in alias['variations']:
                        self.name_aliases.append(alias_variation)

        for page in pages:
            for entry in page.entries:

                if entry.url not in self.urls:
                    self.urls.append(entry.url)

                if entry.response and entry.response.mimeType == 'application/json':
                    try:
                        response_json = json.loads(entry.response.text)
                        if DAYFORCE_URL_FRAGMENT in entry.url:
                            self.process_dayforce_entry(entry.url, response_json)
                        elif SLACK_URL_FRAGMENT in entry.url:
                            self.process_slack_entry(entry.url, response_json)
                        else:
                            print(entry.url)
                    except KeyError:
                        pass

        print('Total Employee Elements: {}'.format(len(self.employee_elements)))

        employee_map = {}
        alias_elements = []

        for element in self.employee_elements:
            if element.recognized_name:
                employee = None
                if element.full_name_hash in employee_map:
                    employee = employee_map[element.full_name_hash]
                elif element.full_name in self.name_aliases:
                    alias_elements.append(element)
                else:
                    employee = Employee(element.full_name_hash)
                    employee_map[employee.full_name_hash] = employee

                if employee:
                    employee.process_element(element)

        for alias in self.name_rules['aliases']:
            full_name_hash = utility.hash_name(alias['name'])
            if full_name_hash not in employee_map:
                self.errors.append('Alias "{}" has no valid elements'.format(alias['name']))
            else:
                for variation in alias['variations']:
                    variation_full_name_hash = utility.hash_name(variation)
                    for alias_element in alias_elements:
                        if variation_full_name_hash == alias_element.full_name_hash:
                            employee_map[full_name_hash].process_element(alias_element)
                            break

        self.employees = employee_map.values()

        for employee in self.employees:
            if employee.manager_id:
                for manager in self.employees:
                    if manager.employee_id == employee.manager_id:
                        employee.manager = manager.get_full_name()


    def process_dayforce_entry(self, url, response_json):
        if EmployeeElement.TYPE_DAYFORCE_MANAGED_EMPLOYEES in url:
            for element in response_json:
                self.employee_elements.append(EmployeeElement(EmployeeElement.TYPE_DAYFORCE_MANAGED_EMPLOYEES, element, self.name_rules))

    def process_slack_entry(self, url, response_json):
        if EmployeeElement.TYPE_SLACK_LIST in url:
            for element in response_json['results']:
                self.employee_elements.append(EmployeeElement(EmployeeElement.TYPE_SLACK_LIST, element, self.name_rules))

    def __str__(self):
        result = ''
        for value in sorted(self.employees, key=lambda v: v.full_name_hash if len(v.last_names) == 0 else v.last_names[0]):
            result += '\n{}'.format(value)

        result += '\n'
        result += '\nUnrecognized elements:'
        unrecognized_elements_shown = []
        for element in self.employee_elements:
            if not element.recognized_name:
                if element.full_name_hash not in unrecognized_elements_shown:
                    result += '\n\t{}'.format(element.full_name_hash)
                    unrecognized_elements_shown.append(element.full_name_hash)

        result += '\n'
        result += '\nManager Count: \t{}'.format(len([x for x, e in enumerate(self.employees) if e.is_manager]))
        result += '\nNonmanager Count: \t{}'.format(len([x for x, e in enumerate(self.employees) if not e.is_manager]))
        result += '\nEmployee Count: \t{}'.format(len(self.employees))

        result += '\n'
        if self.errors:
            result += '\nError count: {}'.format(len(self.errors))
            for error in self.errors:
                result += '\n{}'.format(error)
        else:
            result += '\n{}'.format('Completed without errors')

        return result