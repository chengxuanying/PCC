import tokenizer
import token_type
import utils


def preprocess_src(src):
    lines = src.split('\n')

    define_lines = []
    other_lines = []
    for line in lines:
        if "#define" in line:
            define_lines.append(line)
        else:
            other_lines.append(line)

    defines = []
    for define in define_lines:
        splits = define.split(' ')

        from_str = splits[1]
        to_str = ' '.join(splits[2:])
        defines.append([from_str, to_str])

    for define in defines:
        for idx, line in enumerate(other_lines):
            if define[0] in line:
                other_lines[idx] = line.replace(define[0], define[1])

    return '\n'.join(other_lines) + '\n'


def preprocess(tokens):
    new_tokens = []
    for t in tokens:
        if t.type == token_type.INCLUDE:
            # only 1 layer include is considered
            if '<' in t.value:
                file_name = t.value.split('<')[1].split('>')[0]
            else:
                file_name = t.value.split('"')[1]

            src = utils.read_src(file_name)
            ts = tokenizer.tokenize(src)
            new_tokens.extend(ts)

        else:
            new_tokens.append(t)

    return new_tokens
