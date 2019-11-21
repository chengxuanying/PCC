"""
using DFA to recognize the tokens in the source files.
Greedy
"""
import token_type
import utils



def tokenize(src):
    """

    :type src: str
    """

    tokens = []

    src = src.strip()
    while src:

        if src.startswith('/*'):
            idx = src.find('*/') + 2
            src = src[idx:]

        elif src.startswith('//'):
            idx = src.find('\n') + 1
            src = src[idx:]

        elif src.startswith('#include'):
            src = src[8:].strip()

            # TODO 对"和<不同的处理方式
            idx = src.find(utils.mapPair[src[0]]) + 1  # find next  > or "

            include_file = '#include' + src[:idx]
            include_file = include_file.replace(' ', '')  # remove spaces

            tokens.append(token_type.Token(include_file, token_type.INCLUDE))
            src = src[idx:]

        # 标识符
        elif src[0] in utils.id_alphabet:
            idx = 0
            for idx, ch in enumerate(src):
                if idx == 0:
                    continue

                if ch not in (utils.id_alphabet +
                              utils.num_alphabet):
                    break

            id_name = src[:idx]

            if id_name not in utils.reserved_ids:
                tokens.append(token_type.Token(id_name, token_type.IDENTIFIER))
            else:
                tokens.append(token_type.Token(id_name, token_type.RESERVED))

            src = src[idx:]

        # 数字
        elif src[0] in utils.num_alphabet:
            idx = 0
            for idx, ch in enumerate(src):
                if ch not in utils.num_alphabet:
                    break

            value = src[:idx]
            if '.' in value:
                tokens.append(token_type.Token(float(value), token_type.FLOAT))
            else:
                tokens.append(token_type.Token(int(value), token_type.INT))
            src = src[idx:]

        # 操作符
        elif src[:3] in utils.op_alphabet3:
            tokens.append(token_type.Token(src[:3], token_type.OPERATOR))
            src = src[3:]

        elif src[:2] in utils.op_alphabet2:
            tokens.append(token_type.Token(src[:2], token_type.OPERATOR))
            src = src[2:]

        elif src[:1] in utils.op_alphabet1:
            tokens.append(token_type.Token(src[:1], token_type.OPERATOR))
            src = src[1:]

        # 字符串和字符
        elif src[0] == '"':
            idx = 0

            escaped = False
            src = src[1:]
            for idx, ch in enumerate(src):
                if escaped:
                    escaped = False
                elif ch == '\\':
                    escaped = True
                elif ch == '"':
                    break

            tokens.append(token_type.Token(src[:idx], token_type.STRING))
            src = src[idx + 1:]

        elif src[0] == '\'' and src[2] == '\'':
            tokens.append(token_type.Token(src[1], token_type.CHAR))

            src = src[3:]

        src = src.strip()
    return tokens

