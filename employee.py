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

    def get_full_name(self):
        result = ''
        if self.first_names:
            result = sorted(self.first_names, key=lambda n: len(n))[0]
        if self.last_names:
            result += ' '
            result += sorted(self.last_names, key=lambda n: len(n))[0]
        return result

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