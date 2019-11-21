import utils


class MemTable:
    def __init__(self):
        self.outter_stack = []
        self.inner_stack = []
        self.stack_stack = []
        self.arg_stack_stack = []

        self.outer = {}
        self.inner = {}
        self.stack_index = 0
        self.arg_stack_index = 0
        self.push()

        self.glo = []

    def push(self, same_func=False):
        """
        go into a subfunction
        :return:
        """
        self.outter_stack.append(self.outer)
        self.inner_stack.append(self.inner)
        self.stack_stack.append(self.stack_index)
        self.arg_stack_stack.append(self.arg_stack_stack)

        # merge outter to inner
        new_outter = self.inner
        for k, v in self.outer.items():
            if k not in new_outter:
                new_outter[k] = v

        if same_func:
            self.inner = {}
            self.outer = new_outter

        else:
            self.inner = {}
            self.outer = new_outter
            self.stack_index = 0
            self.arg_stack_index = 8

    def pop(self):
        """
        go out of a subfunction
        :return:
        """
        # print(self.inner, self.outer)
        src = "addq ${}, %rsp\n".format(len(self.inner) * 8)  # TODO

        self.outer = self.outter_stack.pop()
        self.inner = self.inner_stack.pop()
        self.stack_index = self.stack_stack.pop()
        self.arg_stack_index = self.arg_stack_stack.pop()

        return src

    def declare_arguments(self, params):
        regs = list(utils.call_regs[:len(params)])
        for idx, param in enumerate(params):
            # self.arg_stack_index += 8
            self.inner[param[1].value] = regs[idx]

        # print(self.inner)

    def declare_global(self, id_name, id_type, val):
        if id_name in self.inner:
            print('{} is already defined'.format(id_name))
            exit(0)

        self.inner[id_name] = "_{}(%rip)".format(id_name)
        self.glo.append([id_name, id_type, val])

    def argu2stack(self, params):
        src = ""
        regs = list(utils.call_regs[:len(params)])
        for idx, param in enumerate(params):
            id_name = param[1].value
            src += "pushq {} ##push arg to stack\n".format(regs[idx])
            self.stack_index -= 8
            self.inner[id_name] = "{}(%rbp)".format(self.stack_index)
        return src
        # print(self.inner)

    def declare(self, id_name, id_type, exp):
        """
        declare a id in this layer
        :return:
        """

        if id_name in self.inner:
            print('{} is already defined'.format(id_name))
            exit(0)

        src = ""

        # default value is zero!
        if exp is None:
            src += "movq $0,%rax    ## set local variable's default value to 0\n"
        else:
            src += exp._asm()
        src += "pushq %rax\n"

        self.stack_index -= 8
        self.inner[id_name] = "{}(%rbp)".format(self.stack_index)

        # print(id_name, self.inner, self.outer)
        return src

    def declare_array(self, id_name, id_type, index_exp, exp=None):
        """
        declare a id array in this layer
        :return:
        """

        if id_name in self.inner:
            print('{} is already defined'.format(id_name))
            exit(0)

        src = ""

        src += "subq ${},%rsp\n".format(8 * index_exp.num)
        self.stack_index -= 8 * index_exp.num
        self.inner[id_name] = "{}".format(self.stack_index)

        return src

    def use(self, id_name):
        """
        return the _asm of the id
        :return:
        """

        if id_name in self.inner:
            return self.get_local_var(id_name)
        elif id_name in self.outer:
            return self.get_outer_var(id_name)

        print('{} is not defined'.format(id_name))
        exit(0)

    def use_array(self, id_name, index_expression):
        """
        return the _asm of the id
        :return:
        """
        src = ""

        if id_name in self.inner:
            src += self.get_local_arr_var(id_name, index_expression)
        elif id_name in self.outer:
            src += self.get_outer_arr_var(id_name, index_expression)
        else:
            print('{} is not defined'.format(id_name))
            exit(0)

        return src

    def get_outer_arr_var(self, id_name, index_expression):
        src = self.cal_index(index_expression)
        src += "movq {}(%rbp,%r11,8),%rax\n".format(self.outer[id_name])
        return src

    def get_local_arr_var(self, id_name, index_expression):
        src = self.cal_index(index_expression)
        src += "movq {}(%rbp,%r11,8),%rax\n".format(self.inner[id_name])
        return src

    def get_local_var(self, id_name):
        src = ""
        src += "movq {},%rax\n".format(self.inner[id_name])
        return src

    def get_outer_var(self, id_name):
        src = ""
        src += "movq {},%rax\n".format(self.outer[id_name])
        return src

    def assign_array(self, id_name, index_expression):
        src = self.cal_index(index_expression)

        off = None
        if id_name in self.inner:
            off = self.inner[id_name]
        elif id_name in self.outer:
            off = self.outer[id_name]

        src += "movq %rax,{}(%rbp,%r11,8)\n".format(off)
        return src

    def cal_index(self, index_expression):
        src = "pushq %rax\n"
        src += index_expression._asm()
        src += "movq %rax,%r11\n"
        src += "popq %rax\n"
        return src

    def cite(self, id_name):
        if id_name in self.inner:
            return self.inner[id_name]
        elif id_name in self.outer:
            return self.outer[id_name]

    def _asm(self):
        src = ""
        for id_name, id_type, val in self.glo:
            src += "\n"

            # print(id_name, id_type, val)
            src = ".section __DATA,__data\n"
            src += ".globl _{}\n".format(id_name)
            # src += ".data\n"
            src += ".align 3\n"
            src += "_{}:\n".format(id_name)
            src += ".quad {}\n".format(val)

        return src


class StringTable:
    def __init__(self):
        self.string2id = {}
        self.asm = ""

    def reg_string(self, string):
        if string not in self.string2id:
            _id = "L{}_".format(len(self.string2id.keys()))
            self.asm += "{}.str:\n".format(_id)
            self.asm += '.asciz	"{}"\n'.format(str(string))

            self.string2id[str(string)] = _id

    def query(self, string):
        """
        return the _id name
        :param string:
        :return:
        """
        return self.string2id[str(string)]

    def _asm(self):
        return self.asm
