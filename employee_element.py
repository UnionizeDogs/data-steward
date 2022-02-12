import utility

class EmployeeElement:

    TYPE_DAYFORCE_MANAGED_EMPLOYEES = 'GetManagedEmployees'
    TYPE_SLACK_LIST = '/users/list'

    def __init__(self, block_type, block_json, name_rules):
        self.block_type = block_type
        self.block_json = block_json
        self.first_name = None
        self.last_name = None
        self.recognized_name = False

        if block_type == self.TYPE_DAYFORCE_MANAGED_EMPLOYEES:
            names = self.block_json['DisplayName'].split(', ')
            self.first_name = names[-1]
            self.last_name = names[0]
        elif block_type == self.TYPE_SLACK_LIST:
            self.first_name = self.block_json['profile']['first_name']
            self.last_name = self.block_json['profile']['last_name']

        if name_rules:
            for trim in name_rules['trims']:
                self.first_name = self.first_name.replace(trim, '')
                self.last_name = self.last_name.replace(trim, '')

        self.full_name = '{} {}'.format(self.first_name, self.last_name)
        self.full_name_hash = utility.hash_name(self.full_name)

        is_ignored = False

        if name_rules:
            for name_ignored in name_rules['ignored']:
                if name_ignored.lower().strip() in self.first_name.lower().strip() or name_ignored.lower().strip() in self.last_name.lower().strip():
                    is_ignored = True
                    break

        if not is_ignored:
            if not self.recognized_name and name_rules:
                for name_valid in name_rules['valid']:
                    if name_valid.lower().strip() in self.first_name.lower().strip() or name_valid.lower().strip() in self.last_name.lower().strip():
                        self.recognized_name = True
                        break

            if not self.recognized_name:
                self.recognized_name = utility.is_recognized_name(self.first_name, self.last_name)


    def __str__(self):
        result = self.full_name_hash if self.full_name_hash else '<no name>'
        result += '\n\t{}'.format(self.full_name)
        return result