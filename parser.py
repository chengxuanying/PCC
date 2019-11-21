import token_type
import utils
from astnodes import *
from token_type import *


class parseError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return 'parseError: ' + self.msg

    def __repr__(self):
        return str(self)


"""
<program> ::= { <function> | <declaration> }
<function> ::= "int" <id> "(" ")" "{" { <block-item> } "}"
<block-item> ::= <statement> | <declaration>
<statement> ::= "return" <exp> ";"
              | <exp-option> ";"
              | "if" "(" <exp> ")" <statement> [ "else" <statement> ]
              | "{" { <block-item> } "}
              | "for" "(" <exp-option> ";" <exp-option> ";" <exp-option> ")" <statement>
              | "for" "(" <declaration> <exp-option> ";" <exp-option> ")" <statement>
              | "while" "(" <exp> ")" <statement>
              | "do" <statement> "while" <exp> ";"
              | "break" ";"
              | "continue" ";"
<exp-option> ::= <exp> | ""
<declaration> ::= "int" <id> [ = <exp> ] ";"  |  "int" <id> "[" <exp> "]"            #new
<exp> ::= <id> "=" <exp> 
        ｜ <id> "[" <exp> "]" "=" <exp>  #new
        | <conditional-exp>
<conditional-exp> ::= <logical-or-exp> [ "?" <exp> ":" <conditional-exp> ]
<logical-or-exp> ::= <logical-and-exp> { "||" <logical-and-exp> } 
<logical-and-exp> ::= <equality-exp> { "&&" <equality-exp> }
<equality-exp> ::= <relational-exp> { ("!=" | "==") <relational-exp> }
<relational-exp> ::= <additive-exp> { ("<" | ">" | "<=" | ">=") <additive-exp> }
<additive-exp> ::= <term> { ("+" | "-") <term> }
<term> ::= <factor> { ("*" | "/") <factor> }
<factor> ::= <function-call> | "(" <exp> ")" | <unary_op> <factor> 
            | <int> | <char> | <string> 
            | <id> "[" <exp> "]" | <id>                                             #new
<unary_op> ::= "!" | "~" | "-"| ++ | --
<function-call> ::= id "(" [ <exp> { "," <exp> } ] ")"
"""


def parse_func_call(tokens, idx):
    # <function-call> ::= id "(" [ <exp> { "," <exp> } ] ")"
    try:

        idx, tok = utils.match_type(tokens, idx, IDENTIFIER)

        fname = tok.value
        idx, tok = utils.match(tokens, idx, OPERATOR, '(')
        parameters = []

        try:
            idx, exp = parse_condition_expression(tokens, idx)
            parameters.append(exp)
            while True:
                old_idx = idx
                try:
                    old_idx = idx
                    idx, tok = utils.match(tokens, idx, OPERATOR, ',')
                    # idx, exp = parse_expression(tokens, idx)
                    idx, exp = parse_condition_expression(tokens, idx)  # fix bugs, no assignment action
                    parameters.append(exp)
                except:
                    idx = old_idx
                    break
        except:
            pass

        # print(parameters[0])

        idx, tok = utils.match(tokens, idx, OPERATOR, ')')
        # print(parameters)
        # print(fname, tok)
        return idx, Func_Call(fname=fname,
                              parameters=parameters)
    except:
        pass

    assert False


def parse_factor(tokens, idx):
    # <function-call>
    try:
        idx, expression = parse_func_call(tokens, idx)
        return idx, Factor(expression=expression)
    except:
        pass

    # "(" <exp> ")"
    try:
        idx, tok = utils.match(tokens, idx, OPERATOR, '(')
        idx, expression = parse_expression(tokens, idx)
        idx, tok = utils.match(tokens, idx, OPERATOR, ')')
        return idx, Factor(expression=expression)
    except:
        pass

    # <unary_op> <factor>
    try:
        idx, tok = utils.match_type_values(tokens, idx, OPERATOR, utils.unary_op)
        idx, factor = parse_factor(tokens, idx)
        return idx, UnaryOP(op=tok.value,
                            factor=factor)
    except:
        pass

    # <int>
    try:
        idx, tok = utils.match_type(tokens, idx, INT)
        return idx, Number(num=int(tok.value))
    except:
        pass

    # <char>
    try:
        idx, tok = utils.match_type(tokens, idx, CHAR)
        return idx, Number(num=ord(tok.value))
    except:
        pass

    # <string>
    try:
        idx, tok = utils.match_type(tokens, idx, STRING)
        return idx, String(string=tok.value)
    except:
        pass

    # <id> "[" <exp> "]"
    old_idx = idx
    try:

        idx, tok = utils.match_type(tokens, idx, IDENTIFIER)
        id_name = tok.value
        idx, tok = utils.match(tokens, idx, OPERATOR, '[')

        idx, index_expression = parse_expression(tokens, idx)
        idx, tok = utils.match(tokens, idx, OPERATOR, ']')

        return idx, ArrayVariable(id_name=id_name,
                                  index_expression=index_expression)
    except:
        idx = old_idx

    # <id>
    try:
        idx, tok = utils.match_type(tokens, idx, IDENTIFIER)
        return idx, Variable(id_name=tok.value)
    except:
        pass

    # print('error: parse_factor')
    assert False


def parse_term(tokens, idx):
    # <factor> { ("*" | "/") <factor> }
    try:
        idx, factor = parse_factor(tokens, idx)
        term = Term(factor=factor)
        while True:
            try:
                idx, tok = utils.match_type_values(tokens, idx, OPERATOR, ['*', '/', '%'])
                idx, factor = parse_factor(tokens, idx)
                term = Term(factor=factor,
                            op=tok.value,
                            term=term)
            except:
                break

        return idx, term
    except:
        pass

    # print('error: parse_term')
    assert False


def parse_additive_expression(tokens, idx):
    # <additive-exp> ::= <term> { ("+" | "-") <term> }
    try:
        idx, term = parse_term(tokens, idx)
        additive_expression = AdditiveExpression(term=term)

        while True:
            try:
                idx, tok = utils.match_type_values(tokens, idx, OPERATOR, ['+', '-'])
                idx, term = parse_term(tokens, idx)
                additive_expression = AdditiveExpression(term=term,
                                                         op=tok.value,
                                                         expression=additive_expression)
            except:
                break
        return idx, additive_expression
    except:
        pass

    # print('error: parse_additive_expression')
    assert False


def parse_relational_expression(tokens, idx):
    # <relational-exp> ::= <additive-exp> { ("<" | ">" | "<=" | ">=") <additive-exp> }
    try:
        idx, additive_expression = parse_additive_expression(tokens, idx)
        relational_expression = RelationalExpression(additive_expression=additive_expression)
        while True:
            try:
                idx, tok = utils.match_type_values(tokens, idx, OPERATOR, ['<', '>', '<=', '>='])
                idx, additive_expression = parse_additive_expression(tokens, idx)
                relational_expression = RelationalExpression(additive_expression=additive_expression,
                                                             op=tok.value,
                                                             relational_expression=relational_expression)
            except:
                break
        return idx, relational_expression
    except:
        pass
    assert False


def parse_equality_expression(tokens, idx):
    # <equality-exp> ::= <relational-exp> { ("!=" | "==") <relational-exp> }
    try:
        idx, relational_expression = parse_relational_expression(tokens, idx)
        equality_expression = EqualityExpression(relational_expression=relational_expression)

        # != == relational_expression
        while True:
            try:
                idx, tok = utils.match_type_values(tokens, idx, OPERATOR, ['!=', '=='])
                idx, relational_expression = parse_relational_expression(tokens, idx)
                equality_expression = EqualityExpression(relational_expression=relational_expression,
                                                         op=tok.value,
                                                         equality_expression=equality_expression)
            except:
                break

        return idx, equality_expression
    except:
        pass
    assert False


def parse_logical_and_expression(tokens, idx):
    # <logical-and-exp> ::= <equality-exp> { "&&" <equality-exp> }
    try:
        idx, equality_expression = parse_equality_expression(tokens, idx)
        logical_and_expression = LogicalAndExpression(equality_expression=equality_expression)

        # && equality_expression
        while True:
            try:
                idx, tok = utils.match_type_values(tokens, idx, OPERATOR, ['&&'])
                idx, equality_expression = parse_equality_expression(tokens, idx)
                logical_and_expression = LogicalAndExpression(equality_expression=equality_expression,
                                                              op=tok.value,
                                                              logical_and_expression=logical_and_expression)
            except:
                break
        return idx, logical_and_expression
    except:
        pass


def parse_logical_or_expression(tokens, idx):
    # <logical-or-exp> ::= <logical-and-exp> { "||" <logical-and-exp> }
    try:
        idx, logical_and_expression = parse_logical_and_expression(tokens, idx)
        expression = LogicalOrExpression(logical_and_expression=logical_and_expression)
        while True:
            try:
                idx, tok = utils.match_type_values(tokens, idx, OPERATOR, ['||'])
                idx, logical_and_expression = parse_logical_and_expression(tokens, idx)
                expression = LogicalOrExpression(logical_and_expression=logical_and_expression,
                                                 op=tok.value,
                                                 expression=expression)
            except:
                break
        return idx, expression
    except:
        pass
    # print('error: parse_logical_or_expression')
    assert False


def parse_condition_expression(tokens, idx):
    # <conditional-exp> ::= <logical-or-exp> [ "?" <exp> ":" <conditional-exp> ]
    try:
        idx, logical_or_expression = parse_logical_or_expression(tokens, idx)
        condition_expression = ConditionExpression(logical_or_expression=logical_or_expression)

        old_idx = idx
        try:
            idx, tok = utils.match(tokens, idx, OPERATOR, '?')
            idx, expression = parse_expression(tokens, idx)
            idx, tok = utils.match(tokens, idx, OPERATOR, ':')
            idx, condition_expression = parse_condition_expression(tokens, idx)
            condition_expression = ConditionExpression(logical_or_expression=logical_or_expression,
                                                       expression=expression,
                                                       condition_expression=condition_expression)
            return idx, condition_expression

        except:
            idx = old_idx
        return idx, condition_expression
    except:
        pass
    assert False


def parse_expression(tokens, idx):
    # <exp> ::= <id> "=" <exp>
    old_idx = idx
    try:
        idx, tok = utils.match_type(tokens, idx, IDENTIFIER)
        f_name = tok.value

        idx, tok = utils.match_type_values(tokens, idx, OPERATOR, utils.assign_op)
        idx, expression = parse_expression(tokens, idx)
        assignment = Assignment(id_name=f_name,
                                expression=expression,
                                op=tok.value)
        return idx, assignment
    except:
        idx = old_idx

    # <id> "[" <exp> "]" "=" <exp>
    old_idx = idx
    try:
        idx, tok = utils.match_type(tokens, idx, IDENTIFIER)
        f_name = tok.value

        idx, tok = utils.match(tokens, idx, OPERATOR, '[')
        idx, index_expression = parse_expression(tokens, idx)
        idx, tok = utils.match(tokens, idx, OPERATOR, ']')

        idx, tok = utils.match_type_values(tokens, idx, OPERATOR, utils.assign_op)
        idx, expression = parse_expression(tokens, idx)
        assignment = ArrayAssignment(id_name=f_name,
                                     expression=expression,
                                     op=tok.value,
                                     index_expression=index_expression)
        return idx, assignment
    except:
        idx = old_idx

    # <conditional-exp>
    try:
        idx, expression = parse_condition_expression(tokens, idx)
        expression = Expression(logical_or_expression=expression)
        return idx, expression
    except:
        pass

    assert False


def parse_declaration(tokens, idx):
    # <declaration> ::= "int" <id> [ = <exp> ] ";"
    old_idx = idx
    try:
        idx, tok = utils.match(tokens, idx, RESERVED, 'int')
        type_name = tok.value
        idx, tok = utils.match_type(tokens, idx, IDENTIFIER)
        id_name = tok.value

        try:
            idx, tok = utils.match(tokens, idx, OPERATOR, '=')
            idx, expression = parse_expression(tokens, idx)
            idx, tok = utils.match(tokens, idx, OPERATOR, ';')
            return idx, Declaration(type_name=type_name,
                                    id_name=id_name,
                                    expression=expression)
        except:
            pass

        idx, tok = utils.match(tokens, idx, OPERATOR, ';')
        return idx, Declaration(type_name=type_name,
                                id_name=id_name)
    except:
        idx = old_idx

    # "int" <id> "[" <exp> "]"
    old_idx = idx
    try:
        idx, tok = utils.match(tokens, idx, RESERVED, 'int')
        type_name = tok.value
        idx, tok = utils.match_type(tokens, idx, IDENTIFIER)
        id_name = tok.value

        idx, tok = utils.match(tokens, idx, OPERATOR, '[')
        # idx, index_expression = parse_expression(tokens, idx)
        idx, tok = utils.match_type(tokens, idx, INT)
        index_expression = Number(num=int(tok.value))
        idx, tok = utils.match(tokens, idx, OPERATOR, ']')

        idx, tok = utils.match(tokens, idx, OPERATOR, ';')
        return idx, ArrayDeclaration(type_name=type_name,
                                     id_name=id_name,
                                     index_expression=index_expression)
    except:
        idx = old_idx
    assert False


def parse_extended_statement(tokens, idx):
    # normal expression
    try:
        idx, expression = parse_expression(tokens, idx)
        idx, tok = utils.match(tokens, idx, OPERATOR, ';')
        return idx, expression
    except:
        pass

    # nop expression
    try:
        idx, tok = utils.match(tokens, idx, OPERATOR, ';')
        return idx, NopExpression()
    except:
        pass
    assert False


def parse_statement(tokens, idx):
    """
    <statement> ::= "return" <exp> ";"
              | <exp-option> ";"
              | "if" "(" <exp> ")" <statement> [ "else" <statement> ]
              | "{" { <block-item> } "}
              | "for" "(" <exp-option> ";" <exp-option> ";" <exp-option> ")" <statement>
              | "for" "(" <declaration> <exp-option> ";" <exp-option> ")" <statement>
              | "while" "(" <exp> ")" <statement>
              | "do" <statement> "while" <exp> ";"
              | "break" ";"
              | "continue" ";"
    """
    old_idx = idx
    try:
        idx, tok = utils.match(tokens, idx, RESERVED, 'return')
        idx, expression = parse_expression(tokens, idx)
        idx, tok = utils.match(tokens, idx, OPERATOR, ';')
        return idx, Return(expression)
    except:
        idx = old_idx

    # <exp-option> ";"
    old_idx = idx
    try:
        idx, expression = parse_extended_statement(tokens, idx)
        return idx, expression
    except:
        idx = old_idx

    # "if" "(" <exp> ")" <statement> [ "else" <statement> ]
    old_idx = idx
    try:
        idx, tok = utils.match(tokens, idx, RESERVED, 'if')
        idx, tok = utils.match(tokens, idx, OPERATOR, '(')
        idx, condition_expression = parse_expression(tokens, idx)
        idx, tok = utils.match(tokens, idx, OPERATOR, ')')

        idx, if_statement = parse_statement(tokens, idx)

        try:
            idx, tok = utils.match(tokens, idx, RESERVED, 'else')
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
        idx = old_idx

    #  | "{" { <block-item> } "}
    old_idx = idx
    try:
        idx, tok = utils.match(tokens, idx, OPERATOR, '{')
        try:
            idx, block_item = parse_block_item(tokens, idx)
            compound = Compound(block_item=block_item)
            while True:
                try:
                    idx, block_item = parse_block_item(tokens, idx)
                    compound = Compound(block_item=block_item,
                                        compound=compound)
                except:
                    break
        except:
            raise parseError('no block_item')
        idx, tok = utils.match(tokens, idx, OPERATOR, '}')
        return idx, compound
    except:
        idx = old_idx

    # "break" ";"
    old_idx = idx
    try:
        idx, tok = utils.match(tokens, idx, RESERVED, 'break')
        idx, tok = utils.match(tokens, idx, OPERATOR, ';')
        return idx, Break()
    except:
        idx = old_idx

    # "continue" ";"
    old_idx = idx
    try:
        idx, tok = utils.match(tokens, idx, RESERVED, 'continue')
        idx, tok = utils.match(tokens, idx, OPERATOR, ';')
        return idx, Continue()
    except:
        idx = old_idx

    # "do" <statement> "while" <exp> ";"
    old_idx = idx
    try:
        idx, tok = utils.match(tokens, idx, RESERVED, 'do')
        statement = None
        try:
            idx, statement = parse_statement(tokens, idx)
        except:
            raise parseError('no statement')
        idx, tok = utils.match(tokens, idx, RESERVED, 'while')

        expression = None
        try:
            idx, expression = parse_expression(tokens, idx)
        except:
            raise parseError('no expression')
        idx, tok = utils.match(tokens, idx, OPERATOR, ';')
        return idx, DoExperssion(statement=statement,
                                 expression=expression)
    except:
        idx = old_idx

    # "while" <exp>  <statement>
    old_idx = idx
    try:
        idx, tok = utils.match(tokens, idx, RESERVED, 'while')
        expression = None
        try:
            idx, expression = parse_expression(tokens, idx)
        except:
            raise parseError('no expression')

        statement = None
        try:
            idx, statement = parse_statement(tokens, idx)
        except:
            raise parseError('no statement')
        return idx, WhileExperssion(statement=statement,
                                    expression=expression)
    except:
        idx = old_idx

    #  "for" "(" <exp-option> ";" <exp-option> ";" <exp-option> ")" <statement>
    #  "for" "(" <declaration> ; <exp-option> ";" <exp-option> ")" <statement>
    old_idx = idx
    try:
        idx, tok = utils.match(tokens, idx, RESERVED, 'for')
        idx, tok = utils.match(tokens, idx, OPERATOR, '(')

        # content
        expression1 = None
        try:
            idx, expression1 = parse_extended_statement(tokens, idx)
        except:
            expression1 = None
            # then try this
            try:
                idx, expression1 = parse_declaration(tokens, idx)
            except:
                expression1 = None

        if expression1 is None:
            raise parseError('no expression1')

        expression2 = None
        try:
            idx, expression2 = parse_extended_statement(tokens, idx)
        except:
            raise parseError('no expression2')

        expression3 = None
        # normal expression
        try:
            idx, expression3 = parse_expression(tokens, idx)
        except:
            expression3 = None

            # then try nop expression
            try:
                tok = tokens[idx]
                if (tok.type != token_type.OPERATOR or tok.value != ')'):
                    exit()
                expression3 = NopExpression()
            except:
                expression3 = None

        if expression3 is None:
            raise parseError('no expression3')

        idx, tok = utils.match(tokens, idx, OPERATOR, ')')

        # body
        statement = None
        try:
            idx, statement = parse_statement(tokens, idx)
        except:
            raise parseError('no block_item')
        return idx, ForExpression(expression1=expression1,
                                  expression2=expression2,
                                  expression3=expression3,
                                  statement=statement)

    except:
        idx = old_idx
    # print('error: parse_statement')
    assert False


def parse_block_item(tokens, idx):
    # <block-item> ::= <statement> | <declaration>
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
    assert False


def parse_parameter_list(tokens, idx):
    # [ "int" <id> { "," "int" <id> } ]
    ret = []
    try:
        idx, tok1 = utils.match(tokens, idx, RESERVED, 'int')
        idx, tok2 = utils.match_type(tokens, idx, IDENTIFIER)
        ret.append([tok1, tok2])

        old_idx = None
        try:
            while True:
                old_idx = idx
                idx, tok = utils.match(tokens, idx, OPERATOR, ',')
                idx, tok1 = utils.match(tokens, idx, RESERVED, 'int')
                idx, tok2 = utils.match_type(tokens, idx, IDENTIFIER)
                ret.append([tok1, tok2])
        except:
            idx = old_idx

    except:
        pass
    return idx, ret


def parse_function(tokens, idx):
    # <function> ::= "int" <id> "(" [ "int" <id> { "," "int" <id> } ] ")" ( "{" { <block-item> } "}" | ";" )
    idx, tok = utils.match(tokens, idx, RESERVED, 'int')
    rtype = tok.value
    idx, tok = utils.match_type(tokens, idx, IDENTIFIER)
    fname = tok.value

    idx, tok = utils.match(tokens, idx, OPERATOR, '(')
    idx, parameters = parse_parameter_list(tokens, idx)
    idx, tok = utils.match(tokens, idx, OPERATOR, ')')

    # if it is declaration
    try:
        idx, tok = utils.match(tokens, idx, OPERATOR, ';')
        return idx, Function_Declaration(fname=fname,
                                         rtype=rtype,
                                         parameters=parameters,
                                         function=None)
    except:
        pass

    # else it is defination
    idx, tok = utils.match(tokens, idx, OPERATOR, '{')

    # sub statement
    idx, statement = parse_block_item(tokens, idx)
    function = Function(fname=fname,
                        rtype=rtype,
                        statement=statement,
                        parameters=parameters,
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
                            parameters=parameters,
                            function=function)

    idx, tok = utils.match(tokens, idx, OPERATOR, '}')

    # add default return
    if 'astnodes.Return' not in str(type(function.statement)):
        function = Function(fname=fname,
                            rtype=rtype,
                            statement=Return(),
                            parameters=parameters,
                            function=function)

    return idx, function


def parse_global_declaration(tokens, idx):
    # <declaration> ::= "int" <id> [ = <exp> ] ";"
    try:
        idx, tok = utils.match(tokens, idx, RESERVED, 'int')
        type_name = tok.value
        idx, tok = utils.match_type(tokens, idx, IDENTIFIER)
        id_name = tok.value

        try:
            idx, tok = utils.match(tokens, idx, OPERATOR, '=')
            idx, tok = utils.match_type(tokens, idx, INT)
            val = tok.value
            idx, tok = utils.match(tokens, idx, OPERATOR, ';')
            return idx, GlobalDeclaration(type_name=type_name,
                                          id_name=id_name,
                                          val=val)
        except:
            pass

        idx, tok = utils.match(tokens, idx, OPERATOR, ';')
        return idx, Declaration(type_name=type_name,
                                id_name=id_name)
    except:
        pass
    assert False


def parse_program(tokens, idx):
    program = None

    try:
        while True:
            ava = False
            try:
                idx, function = parse_function(tokens, idx)
                program = Program(function=function,
                                  program=program)
                ava = True
            except:
                pass

            try:
                idx, declaration = parse_global_declaration(tokens, idx)
                program = Program(function=declaration,
                                  program=program)
                ava = True
            except:
                pass

            if not ava:
                break

    except:
        pass

    return program


def parse(tokens, idx=0):
    return parse_program(tokens, idx)
