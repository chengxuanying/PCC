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
<function> ::= "int" <id> "(" ")" "{" { <statement> } "}"
<statement> ::= "return" <exp> ";"
              | <exp> ";"
              | "int" <id> [ = <exp> ] ";"
              | "if" "(" <exp> ")" <statement> [ "else" <statement> ]
<exp> ::= <id> "=" <exp> | <logical-or-exp>
<exp> ::= <id> "=" <exp> | <conditional-exp>
-<conditional-exp> ::= <logical-or-exp> [ "?" <exp> ":" <conditional-exp> ]
-<logical-or-exp> ::= <logical-and-exp> { "||" <logical-and-exp> } 
<logical-and-exp> ::= <equality-exp> { "&&" <equality-exp> }
<equality-exp> ::= <relational-exp> { ("!=" | "==") <relational-exp> }
<relational-exp> ::= <additive-exp> { ("<" | ">" | "<=" | ">=") <additive-exp> }
<additive-exp> ::= <term> { ("+" | "-") <term> }
<term> ::= <factor> { ("*" | "/") <factor> }
<factor> ::= "(" <exp> ")" | <unary_op> <factor> | <int> | <id>
<unary_op> ::= "!" | "~" | "-"| ++ | --
"""


def parse_factor(tokens, idx):
    """
    <factor> ::= "(" <exp> new ")" | <unary_op> <factor> | <int> | <id> new

    :param tokens:
    :param idx:
    :return:
    """
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

    # id
    try:
        tok = tokens[idx]

        if (tok.type != token_type.IDENTIFIER):
            raise parseError('no IDENTIFIER')
        idx += 1

        variable = Variable(id_name=tok.value)

        return idx, variable
    except:
        pass

    # print('error: parse_factor')
    assert False


def parse_term(tokens, idx):
    # term
    try:
        # print(idx, tokens[idx])
        idx, factor = parse_factor(tokens, idx)
        term = Term(factor=factor)
        # print(idx, tokens[idx])
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

    # print('error: parse_term')
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

    # print('error: parse_additive_expression')
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


def parse_logical_or_expression(tokens, idx):
    """
    <exp> ::= <id> "=" <exp> | <logical-or-exp>
    <logical-or-exp> ::= <logical-and-exp> { "||" <logical-and-exp> }
    :param tokens:
    :param idx:
    :return:
    """
    # ||
    try:
        idx, logical_and_expression = parse_logical_and_expression(tokens, idx)
        expression = LogicalOrExpression(logical_and_expression=logical_and_expression)

        # || logical_and_expression
        while True:
            try:
                tok = tokens[idx]
                if tok.type != token_type.OPERATOR or \
                        tok.value != '||':
                    break
                idx += 1

                idx, logical_and_expression = parse_logical_and_expression(tokens, idx)
                expression = LogicalOrExpression(logical_and_expression=logical_and_expression,
                                                 op=tok.value,
                                                 expression=expression)
            except:
                pass

        return idx, expression
    except:
        pass

    # print('error: parse_logical_or_expression')
    assert False


def parse_condition_expression(tokens, idx):
    """
    -<conditional-exp> ::= <logical-or-exp> [ "?" <exp> ":" <conditional-exp> ]
    -<logical-or-exp> ::= <logical-and-exp> { "||" <logical-and-exp> }
    :param tokens:
    :param idx:
    :return:
    """

    try:
        idx, logical_or_expression = parse_logical_or_expression(tokens, idx)
        condition_expression = ConditionExpression(logical_or_expression=logical_or_expression)

        try:
            old_idx = idx
            tok = tokens[idx]
            if (tok.type != token_type.OPERATOR or tok.value != '?'):
                raise parseError('no ?')
            idx += 1

            idx, expression = parse_expression(tokens, idx)

            tok = tokens[idx]
            if (tok.type != token_type.OPERATOR or tok.value != ':'):
                idx = old_idx
                raise parseError('no :')
            idx += 1

            idx, condition_expression = parse_condition_expression(tokens, idx)
            condition_expression = ConditionExpression(logical_or_expression=logical_or_expression,
                                                       expression=expression,
                                                       condition_expression=condition_expression)
            return idx, condition_expression

        except:
            pass

        return idx, condition_expression
    except:
        pass

    # print('error: parse_condition_expression')
    assert False


def parse_expression(tokens, idx):
    """
    <exp> ::= <id> "=" <exp> | <logical-or-exp>
    <logical-or-exp> ::= <logical-and-exp> { "||" <logical-and-exp> }
    :param tokens:
    :param idx:
    :return:
    """
    # ||

    try:
        tok = tokens[idx]
        if tok.type != token_type.IDENTIFIER:
            raise parseError('no IDENTIFIER')
        idx += 1
        f_name = tok.value

        tok = tokens[idx]
        if tok.type != token_type.OPERATOR or \
                tok.value not in utils.assign_op:
            idx -= 1
            raise parseError('no =')
        idx += 1

        idx, expression = parse_expression(tokens, idx)

        assignment = Assignment(id_name=f_name,
                                expression=expression,
                                op=tok.value)

        return idx, assignment
    except:
        pass

    # or -> ?:
    try:
        # print(idx, tokens[idx])
        idx, expression = parse_condition_expression(tokens, idx)
        expression = Expression(logical_or_expression=expression)

        return idx, expression
    except:
        pass

    # print('error: parse_expression')
    assert False


def parse_declaration(tokens, idx):
    """
    <declaration> ::= "int" <id> [ = <exp> ] ";"
    :param tokens:
    :param idx:
    :return:
    """
    # int xxx [= xxx];

    try:
        tok = tokens[idx]
        if tok.type != token_type.RESERVED or \
                tok.value != 'int':
            raise parseError('no int')
        idx += 1

        tok = tokens[idx]
        if (tok.type != token_type.IDENTIFIER):
            raise parseError('no int')
        idx += 1
        type_name = tok.value

        id_name = tok.value

        try:
            tok = tokens[idx]
            if tok.type != token_type.OPERATOR or \
                    tok.value != '=':
                raise parseError('no =')
            idx += 1

            idx, expression = parse_expression(tokens, idx)

            declaration = Declaration(type_name=type_name,
                                      id_name=id_name,
                                      expression=expression)

            tok = tokens[idx]
            if (tok.type != token_type.OPERATOR or tok.value != ';'):
                print('error: no ;')
                exit()
            idx += 1

            return idx, declaration

        except:
            pass

        tok = tokens[idx]
        if (tok.type != token_type.OPERATOR or tok.value != ';'):
            print('error: no ;')
            exit()
        idx += 1

        declaration = Declaration(type_name=type_name,
                                  id_name=id_name)
        return idx, declaration

    except:
        pass

    # print('error: parse_declaration')
    assert False


def parse_statement(tokens, idx):
    """
    <statement> ::= "return" <exp> ";"
                  | <exp> ";"
                  | "if" "(" <exp> ")" <statement> [ "else" <statement> ]

    :param tokens:
    :param idx:
    :return:
    """

    try:
        tok = tokens[idx]
        if (tok.type != token_type.RESERVED or tok.value != 'return'):
            raise parseError('no return')
        idx += 1

        idx, expression = parse_expression(tokens, idx)

        tok = tokens[idx]
        if (tok.type != token_type.OPERATOR or tok.value != ';'):
            print('error: no ;')
            exit()
        idx += 1

        statement = Return(expression)
        return idx, statement

    except:
        pass

    # normal expression
    try:
        idx, expression = parse_expression(tokens, idx)

        tok = tokens[idx]
        if (tok.type != token_type.OPERATOR or tok.value != ';'):
            print('error: no ;')
            exit()
        idx += 1

        return idx, expression

    except:
        pass

    # "if" "(" <exp> ")" <statement> [ "else" <statement> ]
    try:
        tok = tokens[idx]
        if (tok.type != token_type.RESERVED or tok.value != 'if'):
            raise parseError('no if')
        idx += 1

        tok = tokens[idx]
        if (tok.type != token_type.OPERATOR or tok.value != '('):
            raise parseError('no (')
        idx += 1

        idx, condition_expression = parse_expression(tokens, idx)

        tok = tokens[idx]
        if (tok.type != token_type.OPERATOR or tok.value != ')'):
            raise parseError('no )')
        idx += 1

        idx, if_statement = parse_statement(tokens, idx)

        try:

            tok = tokens[idx]
            if (tok.type != token_type.RESERVED or tok.value != 'else'):
                raise parseError('no else')
            idx += 1

            idx, else_statement = parse_statement(tokens, idx)

            condition = Condition(condition_expression=condition_expression,
                                  if_statement=if_statement,
                                  else_statement=else_statement)
            return idx, condition
        except:
            pass

        condition = Condition(condition_expression=condition_expression,
                              if_statement=if_statement)
        return idx, condition

    except:
        pass

    print('error: parse_statement')
    assert False


def parse_block_item(tokens, idx):
    """
    <block-item> ::= <statement> | <declaration>
    :param tokens:
    :param idx:
    :return:
    """

    try:
        idx, declaration = parse_declaration(tokens, idx)
        return idx, declaration
    except:
        pass

    try:
        idx, statement = parse_statement(tokens, idx)
        return idx, statement
    except:
        pass

    print('error: parse_block_item')
    assert False


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
    idx, statement = parse_block_item(tokens, idx)
    function = Function(fname=fname,
                        rtype=rtype,
                        statement=statement,
                        function=None)

    # more statement
    while True:
        if tokens[idx].value == '}':
            break
        # print(idx, tokens[idx])
        idx, statement = parse_block_item(tokens, idx)
        function = Function(fname=fname,
                            rtype=rtype,
                            statement=statement,
                            function=function)

    tok = tokens[idx]
    if (tok.type != token_type.OPERATOR or tok.value != '}'):
        print('error')
        exit()

    idx += 1
    return idx, function


def parse_program(tokens, idx):
    idx, function = parse_function(tokens, idx)
    program = Program(function)

    # if idx!= len(tokens):
    #     exit(1)
    return program


def parse(tokens, idx=0):
    return parse_program(tokens, idx)
