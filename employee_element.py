import utility

class EmployeeElement:

    TYPE_DAYFORCE_MANAGED_EMPLOYEES = 'GetManagedEmployees'
    TYPE_DAYFORCE_EMPLOYEE_MANAGERS = 'GetEmployeeManagers'

    TYPES_DAYFORCE = [
        TYPE_DAYFORCE_MANAGED_EMPLOYEES,
        TYPE_DAYFORCE_EMPLOYEE_MANAGERS
    ]

    TYPE_SLACK_LIST = '/users/list'

    TYPES_SLACK = [
        TYPE_SLACK_LIST
    ]

    def __init__(self, block_type, block_json, rules):
        self.block_type = block_type
        self.block_json = block_json
        self.full_name = None
        self.full_name_hash = None
        self.first_name = None
        self.last_name = None
        self.recognized_name = False
        self.title = None
        self.inactive = False
        self.employee_id = None
        self.is_manager = False
        self.manager_id = None

        if block_type in self.TYPES_DAYFORCE:
            names = self.block_json['DisplayName'].split(', ')
            self.first_name = names[-1]
            self.last_name = names[0]
            self.title = self.block_json['Position']
            self.employee_id = self.block_json['EmployeeId']
            self.is_manager = 0 < self.block_json['ManagedEmployeesCount']
            self.manager_id = self.block_json['ManagerId']

        elif block_type == self.TYPE_SLACK_LIST:
            self.first_name = self.block_json['profile']['first_name']
            self.last_name = self.block_json['profile']['last_name']
            self.title = self.block_json['profile']['title']
            self.inactive = self.block_json['deleted']

        rules_names = (rules or {}).get('names', {})

        for trim in rules_names.get('trims', []):
            self.first_name = self.first_name.replace(trim, '')
            self.last_name = self.last_name.replace(trim, '')

        self.full_name = '{} {}'.format(self.first_name, self.last_name)
        self.full_name_hash = utility.hash_name(self.full_name)

        is_ignored = False

        for name_ignored in rules_names.get('ignored', []):
            if name_ignored.lower().strip() in self.first_name.lower().strip() or name_ignored.lower().strip() in self.last_name.lower().strip():
                is_ignored = True
                break

        if not is_ignored:
            if not self.recognized_name:
                for name_valid in rules_names.get('valid', []):
                    if name_valid.lower().strip() in self.first_name.lower().strip() or name_valid.lower().strip() in self.last_name.lower().strip():
                        self.recognized_name = True
                        break

            if not self.recognized_name and rules_names.get('validate', False):
                self.recognized_name = utility.is_recognized_name(self.first_name, self.last_name)
            else:
                self.recognized_name = True


    def __str__(self):
        return str(self.block_json)