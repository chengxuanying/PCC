class Token():
    def __init__(self, value, type):
        self.value = value
        self.type = type

    def __str__(self):
        return '[{}:{}]\n'.format(self.type, self.value)

    def __repr__(self):
        return str(self)

IDENTIFIER = 'IDENTIFIER'
OPERATOR = 'OPERATOR'
INT = 'INT'
FLOAT = 'FLOAT'
INCLUDE = 'INCLUDE'
CHAR = 'CHAR'
STRING = 'STRING'

RESERVED = 'RESERVED'