import tokenizer
import token_type
import utils

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