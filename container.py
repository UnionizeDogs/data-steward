import json
import re
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
        self.rules = None
        self.name_aliases = []
        self.errors = []

        if utility.RESOURCES_NAME_RULES.exists():
            with open(utility.RESOURCES_NAME_RULES, 'r') as name_rules_raw:
                self.rules = json.loads(name_rules_raw.read())
                for amendment in self.rules.get('amendments', []):
                    for alias_variation in amendment.get('variations', []):
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
                    except KeyError:
                        pass

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

        for amendment in self.rules.get('amendments', []):
            full_name_hash = utility.hash_name(amendment.get('name'))
            if full_name_hash not in employee_map:
                self.errors.append('Amendment "{}" has no valid elements'.format(amendment.get('name')))
            else:
                variations = amendment.get('variations')
                if variations:
                    for variation in variations:
                        variation_full_name_hash = utility.hash_name(variation)
                        for alias_element in alias_elements:
                            if variation_full_name_hash == alias_element.full_name_hash:
                                employee_map[full_name_hash].process_element(alias_element)
                                break
                manager = amendment.get('manager')
                if manager:
                    employee_map[full_name_hash].manager = manager

        self.employees = employee_map.values()

        for employee in self.employees:
            employee.process_employees(self.employees)


    def process_dayforce_entry(self, url, response_json):
        if EmployeeElement.TYPE_DAYFORCE_MANAGED_EMPLOYEES or EmployeeElement.TYPE_DAYFORCE_EMPLOYEE_MANAGERS in url:
            if isinstance(response_json, list):
                if response_json and isinstance(response_json[0], dict):
                    for element in response_json:
                        self.employee_elements.append(EmployeeElement(EmployeeElement.TYPE_DAYFORCE_MANAGED_EMPLOYEES, element, self.rules))
            elif isinstance(response_json, dict):
                self.employee_elements.append(EmployeeElement(EmployeeElement.TYPE_DAYFORCE_EMPLOYEE_MANAGERS, response_json, self.rules))

    def process_slack_entry(self, url, response_json):
        if EmployeeElement.TYPE_SLACK_LIST in url:
            for element in response_json['results']:
                self.employee_elements.append(EmployeeElement(EmployeeElement.TYPE_SLACK_LIST, element, self.rules))

    def __str__(self):

        if self.rules.get('debug', False):
            return self.get_debug()

        filtered_employees = []
        output = self.rules.get('output')
        if output:
            filter = output.get('filter')
            is_match_default = not (filter.get('any') or filter.get('all') or filter.get('none'))
            for employee in self.employees:
                if is_match_default:
                    filtered_employees.append(employee)
                    continue

                is_match_any = False
                if filter.get('any'):
                    for key, value in filter.get('any').items():
                        if employee[key] == value:
                            is_match_any = True
                            break
                else:
                    is_match_any = True

                is_match_all = True
                if filter.get('all'):
                    for key, value in filter.get('all').items():
                        if employee[key] != value:
                            is_match_all = False
                            break

                is_match_none = True
                if filter.get('none'):
                    for key, value in filter.get('none').items():
                        if employee[key] == value:
                            is_match_none = False
                            break

                if is_match_any and is_match_all and is_match_none:
                    filtered_employees.append(employee)

        result = ''

        format = output.get('format')
        if format:
            format_fields = []

            for format_field in format.split('$'):
                format_field_stripped = re.sub(r'\W+', '', format_field)
                if format_field_stripped:
                    format_fields.append(format_field_stripped)

            result += format.replace('$', '')
            if filtered_employees:
                for employee in filtered_employees:
                    result_row = format
                    for format_field in format_fields:
                        format_field_result = employee[format_field]

                        if not format_field_result:
                            format_field_result = output.get('none_value', '')

                        if isinstance(format_field_result, list):
                            format_field_list = format_field_result
                            format_field_result = ''
                            for format_field_element in format_field_list:
                                format_field_result += str(format_field_element)

                        result_row = result_row.replace('${}'.format(format_field), str(format_field_result))
                    result += result_row
            else:
                result += '--- No Employees Passed Filter ---'
        else:
            self.errors.append('No format specified')

        result += '\nFilter Matched {} Employee(s)'.format(len(filtered_employees))

        result += '\n\n' + self.get_errors()

        return result


    def get_debug(self):
        result = 'Total Employee Elements: {}'.format(len(self.employee_elements))

        for value in sorted(self.employees,
                            key=lambda v: v.full_name_hash if len(v.last_names) == 0 else v.last_names[0]):
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

        result += '\n' + self.get_errors()

        return result


    def get_errors(self):
        if self.errors:
            result = 'Error count: {}'.format(len(self.errors))
            for error in self.errors:
                result += '\n{}'.format(error)
        else:
            result = '{}'.format('Completed without errors')

        return result
