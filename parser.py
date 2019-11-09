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


"""
<program> ::= <function>
<function> ::= "int" <id> "(" ")" "{" <statement> "}"
<statement> ::= "return" <exp> ";"
<exp> ::= <term> { ("+" | "-") <term> }
<term> ::= <factor> { ("*" | "/") <factor> }
<factor> ::= "(" <exp> ")" | <unary_op> <factor> | <int>
"""


def parse_factor(tokens, idx):
    # ( expression )
    try:
        tok = tokens[idx]
        if tok.type != token_type.OPERATOR or \
                tok.value != '(':
            raise parseError('no (')
        idx += 1

        idx, expression = parse_expression(tokens, idx)
        factor = Factor(expression=expression)

        tok = tokens[idx]
        if tok.type != token_type.OPERATOR or \
                tok.value != ')':
            raise parseError('no )')
        idx += 1

        return idx, factor
    except:
        pass

    # unary_op factor

    try:
        tok = tokens[idx]
        if tok.type != token_type.OPERATOR or \
                tok.value not in utils.unary_op:
            raise parseError('no unary_op')
        idx += 1

        idx, factor = parse_factor(tokens, idx)
        factor = UnaryOP(op=tok.value,
                         factor=factor)

        return idx, factor
    except:
        pass

    # int
    try:
        tok = tokens[idx]
        if (tok.type != token_type.INT):
            raise parseError('no int')
        idx += 1

        expression = Number(num=int(tok.value))

        return idx, expression
    except:
        pass

    print('error: parse_factor')
    assert False


def parse_term(tokens, idx):
    # term
    try:
        idx, factor = parse_factor(tokens, idx)
        term = Term(factor=factor)

        # * or / factor
        while True:
            try:
                tok = tokens[idx]
                if tok.type != token_type.OPERATOR or \
                        tok.value not in ['*', '/']:
                    break
                    # raise parseError('no * or /')

                idx += 1

                idx, factor = parse_factor(tokens, idx)
                term = Term(factor=factor,
                            op=tok.value,
                            term=term)
            except:
                pass

        return idx, term
    except:
        pass

    print('error: parse_term')
    assert False


def parse_additive_expression(tokens, idx):
    # term
    try:
        idx, term = parse_term(tokens, idx)
        additive_expression = AdditiveExpression(term=term)

        # + or - term
        while True:
            try:
                tok = tokens[idx]
                if tok.type != token_type.OPERATOR or \
                        tok.value not in ['+', '-']:
                    break
                    # raise parseError('no + or -')

                idx += 1

                idx, term = parse_term(tokens, idx)
                additive_expression = AdditiveExpression(term=term,
                                                         op=tok.value,
                                                         expression=additive_expression)
            except:
                pass

        return idx, additive_expression
    except:
        pass

    print('error: parse_additive_expression')
    assert False


def parse_relational_expression(tokens, idx):
    # > < >= <=
    try:
        idx, additive_expression = parse_additive_expression(tokens, idx)
        relational_expression = RelationalExpression(additive_expression=additive_expression)

        # != == relational_expression
        while True:
            try:
                tok = tokens[idx]
                if tok.type != token_type.OPERATOR or \
                        tok.value not in ['<', '>', '<=', '>=']:
                    break
                idx += 1

                idx, additive_expression = parse_additive_expression(tokens, idx)
                relational_expression = RelationalExpression(additive_expression=additive_expression,
                                                             op=tok.value,
                                                             relational_expression=relational_expression)
            except:
                pass

        return idx, relational_expression
    except:
        pass


def parse_equality_expression(tokens, idx):
    # != ==
    try:
        idx, relational_expression = parse_relational_expression(tokens, idx)
        equality_expression = EqualityExpression(relational_expression=relational_expression)

        # != == relational_expression
        while True:
            try:
                tok = tokens[idx]
                if tok.type != token_type.OPERATOR or \
                        tok.value not in ['!=', '==']:
                    break
                idx += 1

                idx, relational_expression = parse_relational_expression(tokens, idx)
                equality_expression = EqualityExpression(relational_expression=relational_expression,
                                                         op=tok.value,
                                                         equality_expression=equality_expression)
            except:
                pass

        return idx, equality_expression
    except:
        pass


def parse_logical_and_expression(tokens, idx):
    # &&
    try:
        idx, equality_expression = parse_equality_expression(tokens, idx)
        logical_and_expression = LogicalAndExpression(equality_expression=equality_expression)

        # && equality_expression
        while True:
            try:
                tok = tokens[idx]
                if tok.type != token_type.OPERATOR or \
                        tok.value != '&&':
                    break
                idx += 1

                idx, equality_expression = parse_equality_expression(tokens, idx)
                logical_and_expression = LogicalAndExpression(equality_expression=equality_expression,
                                                              op=tok.value,
                                                              logical_and_expression=logical_and_expression)
            except:
                pass

        return idx, logical_and_expression
    except:
        pass


def parse_expression(tokens, idx):
    # ||
    try:
        idx, logical_and_expression = parse_logical_and_expression(tokens, idx)
        expression = Expression(logical_and_expression=logical_and_expression)

        # || logical_and_expression
        while True:
            try:
                tok = tokens[idx]
                if tok.type != token_type.OPERATOR or \
                        tok.value != '||':
                    break
                idx += 1

                idx, logical_and_expression = parse_logical_and_expression(tokens, idx)
                expression = Expression(logical_and_expression=logical_and_expression,
                                        op=tok.value,
                                        expression=expression)
            except:
                pass

        return idx, expression
    except:
        pass

    print('error: parse_expression')
    assert False


def parse_statement(tokens, idx):
    tok = tokens[idx]
    if (tok.type != token_type.RESERVED or tok.value != 'return'):
        print('error: no return in expression')
        assert False
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
