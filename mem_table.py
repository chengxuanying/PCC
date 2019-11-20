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

    def push(self, same_func = False):
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
        src = "addq ${}, %rsp\n".format(len(self.inner) * 8)

        self.outer = self.outter_stack.pop()
        self.inner = self.inner_stack.pop()
        self.stack_index = self.stack_stack.pop()
        self.arg_stack_index = self.arg_stack_stack.pop()

        return src

    def declare_arguments(self, params):
        for param in params:
            self.arg_stack_index += 8
            self.inner[param[1].value] = self.arg_stack_index

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
        self.inner[id_name] = self.stack_index

        # print(id_name, self.inner, self.outer)
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

    def get_local_var(self, id_name):
        src = ""
        src += "movq {}(%rbp),%rax\n".format(self.inner[id_name])
        return src

    def get_outer_var(self, id_name):
        src = ""
        src += "movq {}(%rbp),%rax\n".format(self.outer[id_name])
        return src

    def cite(self, id_name):
        if id_name in self.inner:
            return self.inner[id_name]
        elif id_name in self.outer:
            return self.outer[id_name]
