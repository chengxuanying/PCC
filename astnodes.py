class UnaryOP:
    def __init__(self, op='~', expression=None):
        self.op = op
        self.expression = expression

    def get_value(self):
        return self.expression.get_value()

    def __str__(self):
        # 右结合

        src = ""
        if self.op == '-':

            src += str(self.expression)
            src += "neg %eax\n"
        elif self.op == '!':

            src += str(self.expression)
            src += "cmpl $0,%eax\n"
            src += "movl $0,%eax\n"
            src += "sete %al\n"
        elif self.op == '~':

            src += str(self.expression)
            src += "not %eax\n"
        return src


class Expression:
    def __init__(self, value=0):
        self.value = value

    def get_value(self):
        return int(self.value)

    def __str__(self):
        return ""


class Return:
    def __init__(self, expression=None):
        self.expression = expression

    def __str__(self):
        src = ""
        src += "movl ${}, % eax\n".format(self.expression.get_value())
        src += str(self.expression)
        src += "ret\n"
        return src


class Function:
    def __init__(self, fname="main", rtype="int", statement=None):
        self.rtype = rtype
        self.fname = fname
        self.statement = statement

    def __str__(self):
        src = ""
        src += '.globl _{}\n'.format(self.fname)
        src += '_{}:\n'.format(self.fname)
        src += str(self.statement)
        return src


class Program:
    def __init__(self, function=None):
        self.function = function

    def __str__(self):
        return str(self.function)
