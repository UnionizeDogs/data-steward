class Employee:

    def __init__(self, full_name_hash):
        self.full_name_hash = full_name_hash
        self.first_names = []
        self.last_names = []
        self.elements = []

    def process_element(self, element):
        self.elements.append(element)
        if element.first_name not in self.first_names:
            self.first_names.append(element.first_name)
        if element.last_name not in self.last_names:
            self.last_names.append(element.last_name)

    def __str__(self):
        result = self.full_name_hash
        result += '\n\t'
        for name in self.first_names:
            result += name + ', '
        result = result + '\n\t'
        for name in self.last_names:
            result += name + ', '
        return result