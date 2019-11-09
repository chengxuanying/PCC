import token_type
import utils
from astnodes import *


class parseError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return 'parseError: ' + self.msg

    def __repr__(self):
        return str(self)


def parse_expression(tokens, idx):
    # <unary_op> ::= "!" | "~" | "-"
    expression = None

    # int
    try:
        tok = tokens[idx]
        if (tok.type != token_type.INT):
            raise parseError('no int')
        expression = Expression(int(tok.value))
        idx += 1

        return idx, expression
    except:
        pass

    # unary operation
    try:
        tok = tokens[idx]
        if (tok.type != token_type.OPERATOR or tok.value not in utils.unary_op):
            raise parseError('no unary_op')

        idx += 1
        idx, expression = parse_expression(tokens, idx)
        expression = UnaryOP(op=tok.value,
                             expression=expression)
        return idx, expression
    except:
        pass

    print('error')
    exit()


def parse_statement(tokens, idx):
    tok = tokens[idx]
    if (tok.type != token_type.RESERVED or tok.value != 'return'):
        print('error: no return in expression')
        exit()
    idx += 1

    idx, expression = parse_expression(tokens, idx)

    tok = tokens[idx]
    if (tok.type != token_type.OPERATOR or tok.value != ';'):
        print('error: no ;')
        exit()
    idx += 1

    statement = Return(expression)
    return idx, statement


def parse_function(tokens, idx):
    tok = tokens[idx]
    if (tok.type != token_type.RESERVED or tok.value != 'int'):
        print('error')
        exit()
    rtype = tok.value
    idx += 1

    tok = tokens[idx]
    if (tok.type != token_type.IDENTIFIER or tok.value != 'main'):
        print('error')
        exit()
    fname = tok.value
    idx += 1

    tok = tokens[idx]
    if (tok.type != token_type.OPERATOR or tok.value != '('):
        print('error')
        exit()
    idx += 1

    tok = tokens[idx]
    if (tok.type != token_type.OPERATOR or tok.value != ')'):
        print('error')
        exit()
    idx += 1

    tok = tokens[idx]
    if (tok.type != token_type.OPERATOR or tok.value != '{'):
        print('error')
        exit()
    idx += 1

    # sub function
    idx, statement = parse_statement(tokens, idx)

    tok = tokens[idx]

    if (tok.type != token_type.OPERATOR or tok.value != '}'):
        print('error')
        exit()
    idx += 1

    function = Function(fname=fname,
                        rtype=rtype,
                        statement=statement)

    return idx, function


def parse_program(tokens, idx):
    idx, function = parse_function(tokens, idx)

    program = Program(function)
    return idx, program


def parse(tokens, idx=0):
    idx, program = parse_program(tokens, idx)
    return program
