import utils
import mem_table

clausecounter = utils.ClauseCounter()
mtable = mem_table.MemTable()
stable = mem_table.StringTable()
text_asm = ""


class UnaryOP:
    def __init__(self, op='~', factor=None):
        self.op = op
        self.factor = factor

    def _asm(self):
        src = ""
        if self.op == '-':
            src += self.factor._asm()
            src += "neg %rax\n"

        elif self.op == '!':
            src += self.factor._asm()
            src += "cmpq $0,%rax\n"
            src += "movq $0,%rax\n"
            src += "sete %al\n"

        elif self.op == '~':
            src += self.factor._asm()
            src += "not %rax\n"

        elif self.op == '++':
            id_name = self.factor.id_name

            src += self.factor._asm()
            src += "inc %rax\n"
            src += "movq %rax,{}\n".format(mtable.cite(id_name))

        elif self.op == '--':
            id_name = self.factor.id_name

            src += self.factor._asm()
            src += "dec %rax\n"
            src += "movq %rax,{}\n".format(mtable.cite(id_name))

        else:
            print("unknown operator")
            exit(0)

        return src


class Number:
    """
    this class is for the instant numbers.
    """

    # can handle only int now
    def __init__(self, num=0):
        self.num = int(num)

    def _asm(self):
        src = "movq ${},%rax\n".format(self.num)
        return src


class String:
    def __init__(self, string=""):
        self.string = str(string)

    def _asm(self):
        # src = "movq ${},%rax\n".format(self.num)
        # return src
        stable.reg_string(self.string)
        id_ = stable.query(self.string)
        src = "leaq {}.str(%rip),%rax\n".format(id_)
        return src


class Func_Call:
    def __init__(self, fname, parameters):
        self.fname = fname
        self.parameters = parameters

    def _asm(self):
        src = ""

        # 16-bytes aligned
        # src += 'pushq %rdi ## save\n'
        # src += 'pushq %rsi ## save\n'
        # src += 'pushq %rcx ## save\n'

        src += 'movq %rsp,%rax\n'
        src += 'subq ${},%rax\n'.format(8 * (len(self.parameters) + 1))

        src += 'xorq %rdx,%rdx\n'
        src += 'movq $16,%rcx\n'
        src += 'idivq %rcx\n'

        src += 'subq %rdx,%rsp\n'
        src += 'pushq %rdx\n'

        # src += 'popq %rcx ## restore\n'
        # src += 'popq %rsi ## restore\n'
        # src += 'popq %rdi ## restore\n'

        regs = list(utils.call_regs[:len(self.parameters)])
        src += self.op_regs('pushq', regs)

        for idx, param in enumerate(self.parameters):
            src += param._asm()
            # src += param._asm()
            # src += "pushq %rax\n"
            src += "movq %rax,{} ## push params\n".format(regs[idx])

        src += "callq _{}\n".format(self.fname)

        src += self.op_regs('popq', reversed(regs))

        # 16-bytes aligned
        src += 'popq %rdx\n'
        src += 'addq %rdx,%rsp\n'

        return src

    def op_regs(self, op="pushq", regs=None):
        src = ""
        for reg in regs:
            src += "{} {}\n".format(op, reg)

        return src


class Factor:
    def __init__(self, expression=None):
        self.expression = expression

    def _asm(self):
        return self.expression._asm()


class Term:
    def __init__(self, factor,
                 op=None, term=None):
        self.factor = factor
        self.term = term
        self.op = op

    def _asm(self):
        if self.op is None:
            return self.factor._asm()

        src = ""
        if self.op == '*':
            src += self.factor._asm()
            src += "push %rax\n"
            src += self.term._asm()
            src += "pop %rcx\n"

            src += "imul %rcx\n"  # P545

        elif self.op == '/':  # /
            src += self.factor._asm()
            src += "push %rax\n"
            src += self.term._asm()
            src += "cdq\n"

            src += "pop %rcx\n"
            src += "idiv %rcx\n"  # P542

        else:
            src += self.factor._asm()
            src += "push %rax\n"
            src += self.term._asm()
            src += "cdq\n"

            src += "pop %rcx\n"
            src += "idiv %rcx\n"  # P542
            src += "movq %rdx,%rax\n"
        return src


class AdditiveExpression:
    def __init__(self, term,
                 op=None, expression=None):
        self.term = term
        self.expression = expression
        self.op = op

    def _asm(self):
        if self.op is None:
            return self.term._asm()

        src = ""
        if self.op == '+':
            src += self.term._asm()
            src += "push %rax\n"
            src += self.expression._asm()
            src += "pop %rcx\n"

            src += "addq %rcx,%rax\n"

        else:  # -
            src += self.term._asm()
            src += "push %rax\n"
            src += self.expression._asm()
            src += "pop %rcx\n"

            src += "subq %rcx,%rax\n"
        return src


class LogicalOrExpression:
    def __init__(self, logical_and_expression,
                 op=None, expression=None):
        self.logical_and_expression = logical_and_expression
        self.expression = expression
        self.op = op

    def _asm(self, reg='rax'):
        if self.op is None:
            return self.logical_and_expression._asm()

        src = ""
        if self.op == '||':
            fail_clause = clausecounter.next()
            ok_clause = clausecounter.next()

            src += self.expression._asm()
            src += 'cmpq $0,%rax\n'
            src += 'je {}\n'.format(fail_clause)
            src += 'movq $1,%rax\n'
            src += 'jmp {}\n'.format(ok_clause)

            src += '{}:\n'.format(fail_clause)
            src += self.logical_and_expression._asm()
            src += 'cmpq $0,%rax\n'
            src += 'movq $1,%rax\n'
            src += "setne %al\n"

            src += '{}:\n'.format(ok_clause)

        return src


class LogicalAndExpression:
    def __init__(self, equality_expression,
                 op=None, logical_and_expression=None):
        self.equality_expression = equality_expression
        self.logical_and_expression = logical_and_expression
        self.op = op

    def _asm(self, reg='rax'):
        if self.op is None:
            return self.equality_expression._asm()

        src = ""
        if self.op == '&&':
            fail_clause = clausecounter.next()
            ok_clause = clausecounter.next()

            src += self.logical_and_expression._asm()
            src += 'cmpq $0,%rax\n'
            src += 'jne {}\n'.format(fail_clause)
            src += 'jmp {}\n'.format(ok_clause)

            src += '{}:\n'.format(fail_clause)
            src += self.equality_expression._asm()
            src += 'cmpq $0,%rax\n'
            src += 'movq $1,%rax\n'
            src += "setne %al\n"

            src += '{}:\n'.format(ok_clause)

        return src


class EqualityExpression:
    def __init__(self, relational_expression,
                 op=None, equality_expression=None):
        self.relational_expression = relational_expression
        self.equality_expression = equality_expression
        self.op = op

    def _asm(self, reg='rax'):
        if self.op is None:
            return self.relational_expression._asm()

        src = ""
        if self.op == '==':
            src += self.relational_expression._asm()
            src += "push %rax\n"

            src += self.equality_expression._asm()
            src += "pop %rcx\n"

            src += "cmpq %rcx,%rax\n"
            src += "movq $0,%rax\n"
            src += "sete %al\n"

        elif self.op == '!=':
            src += self.relational_expression._asm()
            src += "push %rax\n"

            src += self.equality_expression._asm()
            src += "pop %rcx\n"

            src += "cmpq %rcx,%rax\n"
            src += "movq $0,%rax\n"
            src += "setne %al\n"
        return src


class RelationalExpression:
    def __init__(self, additive_expression,
                 op=None, relational_expression=None):
        self.additive_expression = additive_expression
        self.relational_expression = relational_expression
        self.op = op

    def _asm(self, reg='rax'):
        if self.op is None:
            return self.additive_expression._asm()

        src = ""
        if self.op == '>':
            src += self.relational_expression._asm()
            src += "push %rax\n"

            src += self.additive_expression._asm()
            src += "pop %rcx\n"

            src += "cmpq %rcx,%rax\n"
            src += "movq $0,%rax\n"
            src += "setl %al\n"

        elif self.op == '<':
            src += self.relational_expression._asm()
            src += "push %rax\n"

            src += self.additive_expression._asm()
            src += "pop %rcx\n"

            src += "cmpq %rax,%rcx\n"
            src += "movq $0,%rax\n"
            src += "setl %al\n"

        elif self.op == '>=':
            src += self.relational_expression._asm()
            src += "push %rax\n"

            src += self.additive_expression._asm()
            src += "pop %rcx\n"

            src += "cmpq %rcx,%rax\n"
            src += "movq $0,%rax\n"
            src += "setle %al\n"

        elif self.op == '<=':
            src += self.relational_expression._asm()
            src += "push %rax\n"

            src += self.additive_expression._asm()
            src += "pop %rcx\n"

            src += "cmpq %rax,%rcx\n"
            src += "movq $0,%rax\n"
            src += "setle %al\n"
        return src


class Expression:
    def __init__(self, logical_or_expression,
                 f_name=None, expression=None):
        self.logical_or_expression = logical_or_expression
        self.f_name = f_name
        self.expression = expression

    def _asm(self, reg='rax'):
        if self.f_name is None:
            return self.logical_or_expression._asm()

        src = ""

        return src


class NopExpression:
    def __init__(self):
        pass

    def _asm(self):
        return ""


start_clause_global = None
end_clause_global = None


class Compound:
    def __init__(self, block_item, compound=None):
        self.block_item = block_item
        self.compound = compound

    def _asm(self, header=True):
        # tail
        if self.compound is None:
            if not header:
                return self.block_item._asm()
            else:
                return self.newBlock(compound=False) + mtable.pop()

        # body
        if not header:
            src = ""
            src += self.compound._asm(header=False)
            src += self.block_item._asm()
            return src

        # is head block
        src = self.newBlock()
        src += mtable.pop()
        return src

    def newBlock(self, compound=True):
        src = ""

        mtable.push(same_func=True)

        if compound:
            src += self.compound._asm(header=False)
        src += self.block_item._asm()

        return src


class Assignment:
    def __init__(self, id_name, expression, op):
        self.id_name = id_name
        self.expression = expression
        self.op = op

    def _asm(self):
        return self._op(mtable.cite(self.id_name))

    def _op(self, reg):
        src = ""

        if self.op == '=':
            src += self.expression._asm()
            src += "movq %rax,{}\n".format(reg)

        elif self.op == '+=':
            src += self.expression._asm()
            src += "addq %rax,{}\n".format(reg)

        elif self.op == '-=':
            src += self.expression._asm()
            src += "subq %rax,{}\n".format(reg)

        elif self.op == '*=':
            src += self.expression._asm()
            src += "movq {},%rcx\n".format(reg)
            src += "imul %rcx\n"
            src += "movq %rax,{}\n".format(reg)

        elif self.op == '/=':
            src += self.expression._asm()
            src += "movq %rax,%rcx\n"

            src += "movq {},%rax\n".format(reg)

            src += "cdq\n"
            src += "idiv %rcx\n"

            src += "movq %rax,{}\n".format(reg)

        elif self.op == '%=':
            src += self.expression._asm()
            src += "movq %rax,%rcx\n"

            src += "movq {},%rax\n".format(reg)

            src += "cdq\n"
            src += "idiv %rcx\n"

            src += "movq %rdx,{}\n".format(reg)

        elif self.op == '<<=':
            src += self.expression._asm()
            src += "movq %rax,%rcx\n"

            src += "movq {},%rax\n".format(reg)

            src += "shll %cl,%eax\n"

            src += "movq %rax,{}\n".format(reg)

        elif self.op == '>>=':
            src += self.expression._asm()
            src += "movq %rax,%rcx\n"

            src += "movq {},%rax\n".format(reg)

            src += "shrl %cl,%eax\n"

            src += "movq %rax,{}\n".format(reg)

        elif self.op == '&=':  # P61
            src += self.expression._asm()
            src += "push %rax\n"

            src += "movq {},%rax\n".format(reg)

            src += "pop %rcx\n"
            src += "and %rcx,%rax\n"

            src += "movq %rax,{}\n".format(reg)

        elif self.op == '^=':
            src += self.expression._asm()
            src += "push %rax\n"

            src += "movq {},%rax\n".format(reg)

            src += "pop %rcx\n"
            src += "xor %rcx,%rax\n"

            src += "movq %rax,{}\n".format(reg)

        elif self.op == '|=':
            src += self.expression._asm()
            src += "push %rax\n"

            src += "movq {},%rax\n".format(reg)

            src += "pop %rcx\n"
            src += "or %rcx,%rax\n"

            src += "movq %rax,{}\n".format(reg)

        elif self.op == ',':
            src += self.expression._asm()

        else:
            print("unknown operator")
            exit(0)

        return src


class Declaration:
    def __init__(self, type_name, id_name, expression=None):
        self.type_name = type_name
        self.id_name = id_name
        self.expression = expression

    def _asm(self):
        return mtable.declare(self.id_name, self.type_name, self.expression)


class ArrayAssignment:
    def __init__(self, id_name, expression, op, index_expression):
        self.id_name = id_name
        self.expression = expression
        self.op = op
        self.index_expression = index_expression
        self.ass = Assignment(id_name=self.id_name,
                              expression=self.expression,
                              op=self.op)

    def _asm(self):
        src = ""

        if self.op == '=':
            src += self.expression._asm()
            src += mtable.cite_array(self.id_name, self.index_expression)

        return src


class ArrayDeclaration:
    def __init__(self, type_name, id_name, index_expression):
        self.type_name = type_name
        self.id_name = id_name
        self.index_expression = index_expression

    def _asm(self):
        return mtable.declare_array(self.id_name, self.type_name, self.index_expression, None)


class Variable:
    def __init__(self, id_name):
        self.id_name = id_name

    def _asm(self):
        return mtable.use(self.id_name)


class ArrayVariable:
    def __init__(self, id_name, index_expression):
        self.id_name = id_name
        self.index_expression = index_expression

    def _asm(self):
        return mtable.use_array(self.id_name, self.index_expression)


class Return:
    def __init__(self, expression=None):
        self.expression = expression

    def _asm(self):
        src = ""

        if self.expression is not None:
            src += self.expression._asm()

        src += "movq %rbp,%rsp\n"
        src += "popq %rbp\n"
        src += "ret\n"
        return src


class ConditionExpression:
    def __init__(self, logical_or_expression, expression=None, condition_expression=None):
        self.logical_or_expression = logical_or_expression
        self.expression = expression
        self.condition_expression = condition_expression

    def _asm(self, reg='rax'):
        if self.expression is None:
            return self.logical_or_expression._asm()

        src = ""

        else_clause = clausecounter.next()
        end_clause = clausecounter.next()

        src += self.logical_or_expression._asm()
        src += 'cmpq $0,%rax\n'
        src += 'je {}\n'.format(else_clause)
        src += self.expression._asm()
        src += 'jmp {}\n'.format(end_clause)

        src += '{}:\n'.format(else_clause)
        src += self.condition_expression._asm()
        src += '{}:\n'.format(end_clause)

        return src


class Condition:
    def __init__(self, condition_expression, if_statement, else_statement=None):
        self.condition_expression = condition_expression
        self.if_statement = if_statement
        self.else_statement = else_statement

    def _asm(self, reg='rax'):
        src = ""

        # if_clause = clausecounter.next()
        else_clause = clausecounter.next()
        end_clause = clausecounter.next()

        src += self.condition_expression._asm()
        src += 'cmpq $0,%rax\n'
        src += 'je {}\n'.format(else_clause)
        src += self.if_statement._asm()
        src += 'jmp {}\n'.format(end_clause)

        src += '{}:\n'.format(else_clause)

        if self.else_statement is not None:
            src += self.else_statement._asm()

        src += '{}:\n'.format(end_clause)

        return src


class ForExpression:
    def __init__(self, expression1, expression2, expression3, statement):
        self.expression1 = expression1
        self.expression2 = expression2
        self.expression3 = expression3
        self.statement = statement

    def _asm(self):
        start_clause = clausecounter.next()
        end_clause = clausecounter.next()
        add_clause = clausecounter.next()

        global start_clause_global
        global end_clause_global

        start_clause_global = add_clause
        end_clause_global = end_clause

        # body
        src = ""
        src += self.expression1._asm()

        src += '{}:\n'.format(start_clause)
        if type(self.expression2) == NopExpression:
            # for (;1;) always 1
            pass
        else:
            src += self.expression2._asm()
            src += 'cmpq $0,%rax\n'
            src += 'je {}\n'.format(end_clause)

        src += self.statement._asm()

        src += '{}:\n'.format(add_clause)
        src += self.expression3._asm()
        src += 'jmp {}\n'.format(start_clause)

        src += '{}:\n'.format(end_clause)

        # end body

        start_clause_global = None
        end_clause_global = None

        return src


class WhileExperssion:
    def __init__(self, expression, statement):
        self.statement = statement
        self.expression = expression

    def _asm(self):
        start_clause = clausecounter.next()
        end_clause = clausecounter.next()

        global start_clause_global
        global end_clause_global
        start_clause_global = start_clause
        end_clause_global = end_clause

        src = ""
        src += '{}:\n'.format(start_clause)
        src += self.expression._asm()

        src += 'cmpq $0,%rax\n'
        src += 'je {}\n'.format(end_clause)

        src += self.statement._asm()
        src += 'jmp {}\n'.format(start_clause)

        src += '{}:\n'.format(end_clause)

        start_clause_global = None
        end_clause_global = None

        return src


class DoExperssion:
    def __init__(self, statement, expression):
        self.statement = statement
        self.expression = expression

    def _asm(self):
        start_clause = clausecounter.next()
        end_clause = clausecounter.next()

        global start_clause_global
        global end_clause_global
        start_clause_global = start_clause
        end_clause_global = end_clause

        src = ""
        src += '{}:\n'.format(start_clause)
        src += self.statement._asm()

        src += self.expression._asm()
        src += 'cmpq $0,%rax\n'
        src += 'jne {}\n'.format(start_clause)
        src += '{}:\n'.format(end_clause)

        start_clause_global = None
        end_clause_global = None

        return src


class Break:
    def __init__(self):
        pass

    def _asm(self):
        if end_clause_global is None:
            print('error: can not use break now')
        src = 'jmp {}\n'.format(end_clause_global)
        return src


class Continue:
    def __init__(self):
        pass

    def _asm(self):
        if start_clause_global is None:
            print('error: can not use continue now')
        # print(start_clause_global)
        src = 'jmp {}\n'.format(start_clause_global)
        return src


class Function_Declaration:
    def __init__(self, fname, rtype, parameters=None, function=None):
        self.rtype = rtype
        self.fname = fname
        self.parameters = parameters
        self.function = function

    def _asm(self):
        return ""


class Function:
    def __init__(self, fname, rtype, statement, parameters=None, function=None):
        self.rtype = rtype
        self.fname = fname
        self.statement = statement
        self.parameters = parameters
        self.function = function

    def _asm(self, header=True):
        """
        one line code also needs a header
        :param header:
        :return:
        """

        if self.function is None:
            if header:
                return self._header() + self.statement._asm()
            else:
                return self.statement._asm()

        src = ""

        if header:
            src = self._header()

        src += self.function._asm(header=False)
        src += self.statement._asm()

        # if header:
        # src += mtable.pop()
        return src

    def _header(self):
        src = ""
        src += '.globl _{}\n'.format(self.fname)
        src += '_{}:\n'.format(self.fname)
        src += 'pushq %rbp\n'
        src += 'movq %rsp,%rbp\n'

        mtable.push()
        mtable.declare_arguments(self.parameters)

        # save params to stack
        src += mtable.argu2stack(self.parameters)

        return src


class GlobalDeclaration:
    def __init__(self, type_name, id_name, val='0'):
        self.type_name = type_name
        self.id_name = id_name
        self.val = val

    def _asm(self):
        # src = ".section __DATA,__data\n"
        # src += ".globl _{}\n".format(self.id_name)
        # # src += ".data\n"
        # src += ".align 3\n"
        # src += "_{}:\n".format(self.id_name)
        # src += ".quad {}\n".format(self.val)

        mtable.declare_global(self.id_name, self.type_name, self.val)

        return ""


class Program:
    def __init__(self, function, program=None):
        self.function = function
        self.program = program

    def __str__(self):
        # print(varMap)
        # print(scopeVarMap)
        src = self._asm()
        src += stable._asm()
        src += mtable._asm()
        return src

    def _asm(self):
        src = ""
        if self.program is not None:
            src += self.program._asm()
        src += self.function._asm()
        return src
