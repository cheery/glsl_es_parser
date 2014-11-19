import lrkit
from lrkit import canonical 

evals = {}
rules = []

def line(mapping, lhs, *rhs):
    rule = lrkit.Rule(lhs, rhs)
    rules.append(rule)
    def _impl_(fn):
        evals[rule] = (fn, mapping)
        return fn
    return _impl_

def new_list(item):
    return [item]

def list_append(items, item):
    items.append(item)
    return items

@line([0],    "grammar", "group")
def grammar_one(group):
    return group

@line([0, 2], "grammar", "grammar", "newline", "group")
def grammar_many(groups, group):
    groups.extend(group)
    return groups

@line([0, 3], "group",   "symbol", "colon", "indent", "rules", "dedent")
def build_group(lhs, parts):
    rules = []
    for func, mapping, rhs in parts:
        rule = lrkit.Rule(lhs, rhs)
        rule.func = func
        rule.mapping = mapping
        rules.append(rule)
    return rules

line([0],    "rules",   "rule")(new_list)
line([0, 2], "rules",   "rules", "newline", "rule")(list_append)

@line([0],   "rule",    "symbol")
def new_rule(symbol):
    return ("pass", None, [symbol])

@line([0, 3], "rule", "symbol", "lparen", "rparen", "symbol")
def new_rule(func, symbol):
    return (func, [], [symbol])

@line([0, 2, 4], "rule", "symbol", "lparen", "numbers", "rparen", "symbol")
def new_rule(func, mapping, symbol):
    return (func, mapping, [symbol])

@line([0, 1],"rule",    "rule", "symbol")
def rule_append(rule, symbol):
    rule[2].append(symbol)
    return rule

@line([0], "numbers", "star")
def numbers_all(symbol):
    return None

line([0],    "numbers",   "integer")(new_list)
line([0, 1], "numbers",   "numbers", "integer")(list_append)


result = canonical.simulate(rules, "grammar")

def visitor(rule, pos, tab):
    fn, mapping = evals[rule]
    return fn(*[tab[i] for i in mapping])

parser = lrkit.Parser(result, visitor)
fd = open('glsl_es.gr')
for token in lrkit.tokenize(fd, {':':"colon", '(':"lparen", ')':"rparen", "*":"star"}):
    parser.step(token.start, token.stop, token.group, token.value)
glsl_rules = parser.step(token.stop, token.stop, None, None)

result = canonical.simulate(glsl_rules, "translation_unit")

for row, name, states in result.conflicts:
    assert name == 'ELSE', "unresolvable conflict"
    shift = None
    reduc = None
    for state in states:
        if isinstance(state, lrkit.Rule):
            assert reduc is None, "reduce/reduce conflict on ELSE"
            reduc = state
        else:
            assert shift is None, "shift/shift conflict on ELSE"
            shift = state
    assert reduc != None, "shift/shift conflict on ELSE"
    result.table[row]['ELSE'] = shift

rules   = glsl_rules
columns = [None] + list(sorted(result.terminals)) + list(sorted(result.nonterminals))
rows    = []

for line in result.table:
    row = [0 for _ in columns]
    for key, value in line.items():
        if isinstance(value, lrkit.Accept):
            value = -1
        if isinstance(value, lrkit.Rule):
            value = -2 - rules.index(value)
        row[columns.index(key)] = value
    rows.append(row)

import json

json.dump(dict(
    arity=[len(rule) for rule in rules],
    lhs=[columns.index(rule.lhs) for rule in rules],
    func=[rule.func for rule in rules],
    mapping=[rule.mapping for rule in rules],
    rows=rows,
    columns=columns), open("glsl_es.json", 'w'))

# TYPE_NAME
