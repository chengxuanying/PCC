import utils

clausecounter = utils.ClauseCounter()


class UnaryOP:
    def __init__(self, op='~', factor=None):
        self.op = op
        self.factor = factor

    def _asm(self, reg='eax'):
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
        return src


class Number:
    # can handle only int now
    def __init__(self, num=0):
        self.num = int(num)

    def _asm(self):
        src = "movq ${}, %rax\n".format(self.num)
        return src


class Factor:
    def __init__(self, expression=None):
        self.expression = expression

    def _asm(self, reg='eax'):
        return self.expression._asm()


class Term:
    def __init__(self, factor,
                 op=None, term=None):
        self.factor = factor
        self.term = term
        self.op = op

    def _asm(self, reg='eax'):
        if self.op is None:
            return self.factor._asm()

        src = ""
        if self.op == '*':
            src += self.factor._asm()
            src += "push %rax\n"
            src += self.term._asm()
            src += "pop %rcx\n"

            src += "imul %rcx\n"  # P545

        else:  # /
            src += self.factor._asm()
            src += "push %rax\n"
            src += self.term._asm()
            src += "cdq\n"

            src += "pop %rcx\n"
            src += "idiv %rcx\n"  # P542
        return src


class AdditiveExpression:
    def __init__(self, term,
                 op=None, expression=None):
        self.term = term
        self.expression = expression
        self.op = op

    def _asm(self, reg='eax'):
        if self.op is None:
            return self.term._asm()

        src = ""
        if self.op == '+':
            src += self.term._asm()
            src += "push %rax\n"
            src += self.expression._asm()
            src += "pop %rcx\n"

            src += "addq %rcx, %rax\n"

        else:  # -
            src += self.term._asm()
            src += "push %rax\n"
            src += self.expression._asm()
            src += "pop %rcx\n"

            src += "subq %rcx, %rax\n"
        return src


class Expression:
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


class Return:
    def __init__(self, expression=None):
        self.expression = expression

    def _asm(self):
        src = ""
        # src += "movl ${}, % eax\n".format(self.expression.get_value())
        src += self.expression._asm()
        src += "ret\n"
        return src


class Function:
    def __init__(self, fname="main", rtype="int", statement=None):
        self.rtype = rtype
        self.fname = fname
        self.statement = statement

    def _asm(self):
        src = ""
        src += '.globl _{}\n'.format(self.fname)
        src += '_{}:\n'.format(self.fname)
        src += self.statement._asm()
        return src


class Program:
    def __init__(self, function=None):
        self.function = function

    def __str__(self):
        return self.function._asm()
