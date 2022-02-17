import utility
from employee_element import EmployeeElement

class Employee:

    def __init__(self, full_name_hash):
        self.full_name_hash = full_name_hash
        self.first_names = []
        self.last_names = []
        self.titles = []
        self.elements = []
        self.inactive = False
        self.employee_id = None
        self.is_manager = False
        self.manager = None
        self.manager_id = None
        self.possible_contractor = False
        self.in_dayforce = False
        self.in_slack = False
        self.last_name_count = 0

    def process_element(self, element):
        self.elements.append(element)

        if element.first_name and element.first_name not in self.first_names:
            self.first_names.append(element.first_name)

        if element.last_name and element.last_name not in self.last_names:
            self.last_names.append(element.last_name)

        if element.title and element.title not in self.titles:
            self.titles.append(element.title)

        self.inactive |= element.inactive

        if element.employee_id:
            self.employee_id = element.employee_id

        self.is_manager |= element.is_manager

        if element.manager_id:
            self.manager_id = element.manager_id

        self.in_dayforce |= element.block_type in EmployeeElement.TYPES_DAYFORCE
        self.in_slack |= element.block_type in EmployeeElement.TYPES_SLACK

    def process_employees(self, employees):

        manager_full_name_hash = utility.hash_name(self.manager)

        for employee in employees:
            if self.manager_id:
                if not self.manager and employee.employee_id == self.manager_id:
                    self.manager = employee.get_full_name()
            elif self.manager:
                if employee.full_name_hash == manager_full_name_hash:
                    self.manager_id = employee.employee_id

            if list(set(self.last_names) & set(employee.last_names)):
                self.last_name_count += 1


        if self.manager_id:
            for manager in employees:
                if manager.employee_id == self.manager_id:
                    self.manager = manager.get_full_name()
                    break

        elif self.manager:
            manager_full_name_hash = utility.hash_name(self.manager)
            for manager in employees:
                if manager.full_name_hash == manager_full_name_hash:
                    self.manager_id = manager.employee_id
                    break

    def get_full_name(self):
        result = ''
        if self.first_names:
            result = self.first_names[0]
        if self.last_names:
            result += ' '
            result += self.last_names[0]
        return result

    def __getitem__(self, item):
        if hasattr(self, item):
            return getattr(self, item)

        items = item + 's'

        if hasattr(self, items):
            result = getattr(self, items)
            if not result:
                return None

            if isinstance(result, list):
                return result[0]
                # return max(result, key=len)
            else:
                return result


        raise AttributeError("'Employee' object has no attribute '{}' or '{}'".format(item, items))


    def __str__(self):
        result = self.get_full_name()
        result += '\n\tHash: \t\t{}'.format(self.full_name_hash)
        result += '\n\tFirst: \t\t'
        for name in self.first_names:
            result += name + ', '
        result += '\n\tLast: \t\t'
        for name in self.last_names:
            result += name + ', '
        result += '\n\tTitles: \t'
        for title in self.titles:
            result += title + ', '
        result += '\n\tManages: \t{}'.format(self.is_manager)
        result += '\n\tManager: \t{}'.format(self.manager)
        result += '\n\tActive: \t{}'.format(not self.inactive)
        result += '\n\tElements: \t{}'.format(len(self.elements))
        return result