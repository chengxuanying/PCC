
def generate(ast, fname):
    f = open(fname, mode='w+')

    src = str(ast)
    f.write(src)
    # f.write('.globl _{}\n'.format(ast.function.fname))
    # f.write('_{}:\n'.format(ast.function.fname))
    # f.write('movl ${}, %eax\n'.format(ast.function.statement.expression.value))
    # f.write('ret\n')

    # print(src)
    f.close()


    import os
    oname = fname.replace('.s', '.o')
    exename = fname.replace('.s', '')

    os.system("gcc -c {} -o {}".format(fname, oname))
    os.system("gcc {} -o {}".format(oname, exename))

