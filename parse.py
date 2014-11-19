import json
import tokenizer

functions = {}

functions['pass'] = lambda first, *rest: first if len(rest) == 0 else [first] + list(rest)
functions['list'] = lambda *args: list(args)

def append(lst, *args):
    lst.extend(args)
    return lst
functions['append'] = append

table = json.load(open('glsl_es.json'))

columns = dict((name, index) for index, name in enumerate(table['columns']))
stack = []
data  = []
state = 0

def step(start, stop, group, value):
    global state
    action = table['rows'][state][columns[group]]
    while action <= -2:
        values = []
        for n in range(table['arity'][-2 -action]):
            state = stack.pop(-1)
            block = data.pop(-1)
            values.append(block)
        values.reverse()
        print table['columns'][table['lhs'][-2-action]], values
        mapping = table['mapping'][-2-action]
        if mapping is not None:
            values = [values[index] for index in mapping]
        data.append(functions[table['func'][-2-action]](*values))
        stack.append(state)
        state = table['rows'][state][table['lhs'][-2 -action]]
        action = table['rows'][state][columns[group]]
    if action == -1:
        state = stack.pop(-1)
        block = data.pop(-1)
        assert len(stack) == 0
        assert len(data) == 0
        return block
    if action == 0:
        names = []
        for name, value in zip(table['columns'], table['rows'][state]):
            if value != 0:
                names.append(name)
        raise Exception("got {} but expected {}".format(group, ', '.join(names)))
    data.append(value)
    stack.append(state)
    state = action

for start, stop, group, value in tokenizer.tokenize(open('example.glsl').read()):
    print 'token', group
    step(start, stop, group, value)
result = step(stop, stop, None, None)

print result
