# TOKEN CLASS

class Token:
    def __init__(self, line_number, type_, value=None):
        self.line_number = line_number
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value:
            return f'Line {self.line_number}: {self.type}: {self.value}'
        return f'Line {self.line_number}: {self.type}'
