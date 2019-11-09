# lexer
id_alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
               'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
               'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
               'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
               '_']

mapPair = {
    '[' : ']',
    '{' : '}',
    '<' : '>',
    '(' : ')',
    '\'' : '\'',
    '"' : '"',
}

num_alphabet = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']

op_alphabet1 = [':', ';', ',',
                '+', '-', '*', '/', '%',
                '=', '<', '>', '!', '?',
                '~',
                '[', ']', '{', '}', '<', '>', '(', ')']

op_alphabet2 = ['+=', '-=', '*=', '/=', '%=',
                '++', '--']

reserved_ids = ["bool", "char", "short", "int", "long",
                "signed", "unsigned",
                "if", "else", "while", "do", "return"]

# parse
unary_op = ['!', '~', '-']


def read_src(file = 'return_2.c'):
    with open(file) as f:
        return f.read()