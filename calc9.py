# Token types
(INTEGER, PLUS, MINUS, MUL, DIV, LPAREN, RPAREN, BEGIN, END, DOT, ASSIGN,
SEMI, ID, EOF, COLON, COMMA, VAR, INTEGER_CONST, INTEGER_DIV, FLOAT_DIV, PROGRAM, REAL_CONST, REAL) = (
    'INTEGER', 'PLUS', 'MINUS', 'MUL', 'DIV', '(', ')',
    'BEGIN', 'END', 'DOT', 'ASSIGN', 'SEMI', 'ID', 'EOF', 'COLON', 'COMMA', 'VAR', 'INTEGER_CONST', 'INTEGER_DIV', 'FLOAT_DIV', 'PROGRAM', 'REAL_CONST', 'REAL'
)

class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return f'Token({self.type}, {repr(self.value)})'

    def __repr__(self):
        return self.__str__()

RESERVED_KEYWORDS = {
    'PROGRAM': Token(PROGRAM, 'PROGRAM'),
    'VAR': Token(VAR, 'VAR'),
    'DIV': Token(INTEGER_DIV, 'DIV'),
    'INTEGER': Token(INTEGER, 'INTEGER'),
    'REAL': Token(REAL, 'REAL'),
    'BEGIN': Token(BEGIN, 'BEGIN'),
    'END': Token(END, 'END'),
}

class Lexer(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        self.pos += 1
        self.current_char = None if self.pos > len(self.text) - 1 else self.text[self.pos]

    def peek(self):
        peek_pos = self.pos + 1
        return None if peek_pos > len(self.text) - 1 else self.text[peek_pos]

    def skip_comment(self):
        while self.current_char != '}':
            self.advance()
        self.advance()

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def number(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        if self.current_char == '.':
            result += self.current_char
            self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()
            return Token(REAL_CONST, float(result))
        return Token(INTEGER_CONST, int(result))

    def _id(self):
        result = ''
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.advance()
        return RESERVED_KEYWORDS.get(result.upper(), Token(ID, result))

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.isalpha():
                return self._id()
            if self.current_char == ':' and self.peek() == '=':
                self.advance(); self.advance()
                return Token(ASSIGN, ':=')
            if self.current_char == ';':
                self.advance(); return Token(SEMI, ';')
            if self.current_char == '.':
                self.advance(); return Token(DOT, '.')
            if self.current_char.isdigit():
                return self.number()
            if self.current_char == '+':
                self.advance(); return Token(PLUS, '+')
            if self.current_char == '-':
                self.advance(); return Token(MINUS, '-')
            if self.current_char == '*':
                self.advance(); return Token(MUL, '*')
            if self.current_char == '/':
                self.advance(); return Token(FLOAT_DIV, '/')
            if self.current_char == '(':
                self.advance(); return Token(LPAREN, '(')
            if self.current_char == ')':
                self.advance(); return Token(RPAREN, ')')
            if self.current_char == '{':
                self.advance(); self.skip_comment(); continue
            if self.current_char == ':':
                self.advance(); return Token(COLON, ':')
            if self.current_char == ',':
                self.advance(); return Token(COMMA, ',')
            self.error()
        return Token(EOF, None)

# AST nodes
class AST: pass
class Program(AST): 
    def __init__(self, name, block): self.name = name; self.block = block
class Block(AST):
    def __init__(self, declarations, compound_statement):
        self.declarations = declarations
        self.compound_statement = compound_statement
class VarDecl(AST):
    def __init__(self, var_node, type_node):
        self.var_node = var_node
        self.type_node = type_node
class Type(AST):
    def __init__(self, token): self.token = token; self.value = token.value
class BinOp(AST):
    def __init__(self, left, op, right): self.left = left; self.token = self.op = op; self.right = right
class UnaryOp(AST):
    def __init__(self, op, expr): self.token = self.op = op; self.expr = expr
class Num(AST):
    def __init__(self, token): self.token = token; self.value = token.value
class Compound(AST):
    def __init__(self): self.children = []
class Assign(AST):
    def __init__(self, left, op, right): self.left = left; self.token = self.op = op; self.right = right
class Var(AST):
    def __init__(self, token): self.token = token; self.value = token.value
class NoOp(AST): pass

# Parser
class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def program(self):
        self.eat(PROGRAM)
        var_node = self.variable()
        prog_name = var_node.value
        self.eat(SEMI)
        block_node = self.block()
        self.eat(DOT)
        return Program(prog_name, block_node)

    def block(self):
        declaration_nodes = self.declarations()
        compound_statement_node = self.compound_statement()
        return Block(declaration_nodes, compound_statement_node)

    def declarations(self):
        declarations = []
        if self.current_token.type == VAR:
            self.eat(VAR)
            while self.current_token.type == ID:
                var_decl = self.variable_declaration()
                declarations.extend(var_decl)
                self.eat(SEMI)
        return declarations

    def variable_declaration(self):
        var_nodes = [Var(self.current_token)]
        self.eat(ID)
        while self.current_token.type == COMMA:
            self.eat(COMMA)
            var_nodes.append(Var(self.current_token))
            self.eat(ID)
        self.eat(COLON)
        type_node = self.type_spec()
        return [VarDecl(var_node, type_node) for var_node in var_nodes]

    def type_spec(self):
        token = self.current_token
        if token.type == INTEGER:
            self.eat(INTEGER)
        else:
            self.eat(REAL)
        return Type(token)

    def compound_statement(self):
        self.eat(BEGIN)
        nodes = self.statement_list()
        self.eat(END)
        root = Compound()
        for node in nodes:
            root.children.append(node)
        return root

    def statement_list(self):
        node = self.statement()
        results = [node]
        while self.current_token.type == SEMI:
            self.eat(SEMI)
            results.append(self.statement())
        return results

    def statement(self):
        if self.current_token.type == BEGIN:
            return self.compound_statement()
        elif self.current_token.type == ID:
            return self.assignment_statement()
        return self.empty()

    def assignment_statement(self):
        left = self.variable()
        token = self.current_token
        self.eat(ASSIGN)
        right = self.expr()
        return Assign(left, token, right)

    def variable(self):
        node = Var(self.current_token)
        self.eat(ID)
        return node

    def empty(self):
        return NoOp()

    def expr(self):
        node = self.term()
        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)
            node = BinOp(left=node, op=token, right=self.term())
        return node

    def term(self):
        node = self.factor()
        while self.current_token.type in (MUL, INTEGER_DIV, FLOAT_DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            elif token.type == INTEGER_DIV:
                self.eat(INTEGER_DIV)
            elif token.type == FLOAT_DIV:
                self.eat(FLOAT_DIV)
            node = BinOp(left=node, op=token, right=self.factor())
        return node

    def factor(self):
        token = self.current_token
        if token.type == PLUS:
            self.eat(PLUS)
            return UnaryOp(token, self.factor())
        elif token.type == MINUS:
            self.eat(MINUS)
            return UnaryOp(token, self.factor())
        elif token.type in (INTEGER_CONST, REAL_CONST):
            self.eat(token.type)
            return Num(token)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node
        return self.variable()

    def parse(self):
        node = self.program()
        if self.current_token.type != EOF:
            self.error()
        return node

# Interpreter
class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'No visit_{type(node).__name__} method')

class Interpreter(NodeVisitor):
    GLOBAL_SCOPE = {}

    def __init__(self, parser):
        self.parser = parser

    def interpret(self):
        tree = self.parser.parse()
        self.visit(tree)

    def visit_Program(self, node):
        self.visit(node.block)

    def visit_Block(self, node):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_VarDecl(self, node): pass
    def visit_Type(self, node): pass
    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_Assign(self, node):
        var_name = node.left.value
        self.GLOBAL_SCOPE[var_name] = self.visit(node.right)

    def visit_Var(self, node):
        val = self.GLOBAL_SCOPE.get(node.value)
        if val is None:
            raise NameError(repr(node.value))
        return val

    def visit_NoOp(self, node): pass
    def visit_BinOp(self, node):
        if node.op.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == INTEGER_DIV:
            return self.visit(node.left) // self.visit(node.right)
        elif node.op.type == FLOAT_DIV:
            return float(self.visit(node.left)) / float(self.visit(node.right))

    def visit_Num(self, node):
        return node.value

    def visit_UnaryOp(self, node):
        if node.op.type == PLUS:
            return +self.visit(node.expr)
        elif node.op.type == MINUS:
            return -self.visit(node.expr)

# Main
def main():
    text = """
    PROGRAM Test;
    VAR
        number     : INTEGER;
        a, b, c, x : INTEGER;
        y          : REAL;

    BEGIN
        number := 2;
        a := number;
        b := 10 * a + 10 * number DIV 4;
        c := a - - b;
        x := 11;
        y := 20 / 7 + 3.14;
        { writeln('a = ', a); }
        { writeln('b = ', b); }
        { writeln('c = ', c); }
        { writeln('number = ', number); }
        { writeln('x = ', x); }
        { writeln('y = ', y); }
    END.
    """
    lexer = Lexer(text)
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    interpreter.interpret()
    print(interpreter.GLOBAL_SCOPE)

if __name__ == '__main__':
    main()
