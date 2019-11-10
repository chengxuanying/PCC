import tokenizer
import preprocessor
import parser
import generator

import utils
import sys

#  ./test_compiler.sh "python3 ../pcc.py"
#  python3 pcc.py return_2.c
#  echo $?

if __name__ == '__main__':
    # print("PCC v1.0")

    if len(sys.argv) > 1:
        fname = sys.argv[1]
    else:
        fname = 'return_2.c'

    src = utils.read_src(fname)
    # print(src)

    tokens = tokenizer.tokenize(src)
    tokens = preprocessor.preprocess(tokens)
    # print(tokens)

    ast = parser.parse(tokens)


    generator.generate(ast, fname.replace('.c', '.s'))

