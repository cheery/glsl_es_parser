keywords = set(
    "attribute const uniform varying break continue do for while "
    "if else in out inout true false "
    "lowp mediump highp precision invariant "
    "discard return struct void "
    "float int bool mat2 mat3 mat4 "
    "vec2 vec3 vec4 ivec2 ivec3 ivec4 bvec2 bvec3 bvec4 "
    "sampler2D samplerCube ".split(' '))

reserved = set(
    "asm class union enum typedef template this packed "
    "goto switch default inline noinline volatile public "
    "static extern external interface flat "
    "long short double half fixed unsigned superp "
    "input output hvec2 hvec3 hvec4 dvec2 dvec3 dvec4 "
    "fvec2 fvec3 fvec4 sampler1D sampler3D sampler1DShadow "
    "sampler2DShadow sampler2DRect sampler3DRect "
    "sampler2DRectShadow sizeof cast namespace using".split(' '))

# also lines beginning with __ are reserved as keywords.
# identifiers starting with gl_ are reserved for OpenGL ES

class Stream(object):
    def __init__(self, source):
        self.source = source
        self.index  = 0

    @property
    def empty(self):
        return self.index >= len(self.source)

    @property
    def character(self):
        return self.source[self.index:self.index+1]

    @property
    def character_pair(self):
        return self.source[self.index:self.index+2]

    @property
    def character_tri(self):
        return self.source[self.index:self.index+3]

    def adv(self):
        ch = self.character
        self.index += 1
        return ch
    
def tokenize(source):
    stream = Stream(source)
    while not stream.empty:
        while not stream.empty and stream.character in ' \t\r\n':
            stream.adv()
        if stream.empty:
            continue
        if stream.character_pair == '/*':
            string = stream.adv() + stream.adv()
            while not stream.empty and stream.character_pair != '*/':
                string += stream.adv()
            string += stream.adv()
            string += stream.adv()
            continue
        if stream.character_pair == '//':
            string = stream.adv()
            while not stream.empty and stream.character != '\n':
                string += stream.adv()
            continue
        yield token(stream)

def token(stream):
    start = stream.index
    if stream.character == '#':
        string = stream.adv()
        while not stream.empty and stream.character != '\n':
            string += stream.adv()
        return start, stream.index, 'macro', string
    if isnondigit(stream.character):
        string = stream.adv()
        while isnondigit(stream.character) or isdigit(stream.character):
            string += stream.adv()
        name = 'IDENTIFIER'
        if string in keywords:
            name = string.upper()
        elif string in reserved:
            name = 'RESERVED'
        elif string in ('true', 'false'):
            nmae = 'BOOLCONSTANT'
        return start, stream.index, name, string
    if stream.character == '0' and stream.character_pair != '0.':
        string = stream.adv()
        if stream.character in 'xX':
            string += stream.adv()
            while ishex(stream.character):
                string += stream.adv()
            return start, stream.index, 'INTCONSTANT', string
        while isoctal(stream.character):
            string += stream.adv()
        return start, stream.index, 'INTCONSTANT', string
    if isdigit(stream.character):
        string = stream.adv()
        while isdigit(stream.character):
            string += stream.adv()
        name = 'INTCONSTANT'
        if stream.character == '.':
            name = 'FLOATCONSTANT'
            string += stream.adv()
            while isdigit(stream.character):
                string += stream.adv()
        if stream.character in 'eE':
            name = 'FLOATCONSTANT'
            string += stream.adv()
            if stream.character in '-+':
                string += stream.adv()
            if not isdigit(stream.character):
                raise Exception("expected digit")
            string += stream.adv()
            while isdigit(stream.character):
                string += stream.adv()
        return start, stream.index, name, string
    if stream.character_tri in operators:
        string = stream.adv() + stream.adv() + stream.adv()
        return start, stream.index, operators[string], string
    if stream.character_pair in operators:
        string = stream.adv() + stream.adv()
        return start, stream.index, operators[string], string
    if stream.character in operators:
        string = stream.adv()
        return start, stream.index, operators[string], string
    raise Exception("invalid character")

# operator precedence table on page 40
operators = {
    "(":'LEFT_PAREN',
    ")":'RIGHT_PAREN',
    "[":'LEFT_BRACKET',
    "]":'RIGHT_BRACKET',
    "{":'LEFT_BRACE',
    "}":'RIGHT_BRACE',
    ".":'DOT',
    "++":'INC_OP',
    "--":'DEC_OP',
    ",":'COMMA',
    ":":'COLON',
    ";":'SEMICOLON',
    "+":'PLUS',
    "-":'DASH',
    "~":'BANG',
    "!":'TILDE',
    "*":'STAR',
    "/":'SLASH',
    "%":'PERCENT',
    "<<":'LEFT_OP',
    ">>":'RIGHT_OP',
    "<":'LEFT_ANGLE',
    ">":'RIGHT_ANGLE',
    "<=":'LE_OP',
    ">=":'GE_OP',
    "==":'EQ_OP',
    "!=":'NE_OP',
    "&":'AMPERSAND',
    "^":'CARET',
    "|":'VERTICAL_BAR',
    "&&":'AND_OP',
    "^^":'XOR_OP',
    "||":'OR_OP',
    "?":'QUESTION',
    "=":'EQUAL',
    "+=":'ADD_ASSIGN',
    "-=":'SUB_ASSIGN',
    "*=":'MUL_ASSIGN',
    "/=":'DIV_ASSIGN',
    "%=":'MOD_ASSIGN',
    "<<=":'LEFT_ASSIGN',
    ">>=":'RIGHT_ASSIGN',
    "&=":'AND_ASSIGN',
    "^=":'XOR_ASSIGN',
    "|=":'OR_ASSIGN',
}

def isnondigit(ch):
    return 'a' <= ch.lower() <= 'z' or ch == '_'

def ishex(ch):
    return 'a' <= ch.lower() <= 'f' or isdigit(ch)

def isoctal(ch):
    return '0' <= ch <= '7'

def isdigit(ch):
    return '0' <= ch <= '9'

if __name__=='__main__':
    source = open('example.glsl', 'r').read()
    for tk in tokenize(source):
        print tk
