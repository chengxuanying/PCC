import utils

def generate(ast, fname):
    if ast is None:
        print("Empty file is not allowed!")
        exit(1)

    f = open(fname, mode='w+')

    src = []
    for line in str(ast).split('\n'):
        if ':' in line:
            src.append(line)
        else:
            src.append('\t' + line)
    src = '\n'.join(src)

    f.write(utils.header)
    f.write(src)
    f.close()

    import os
    oname = fname.replace('.s', '.o')
    exename = fname.replace('.s', '')

    os.system("gcc -c {} -o {}".format(fname, oname))
    os.system("gcc {} -o {}".format(oname, exename))
