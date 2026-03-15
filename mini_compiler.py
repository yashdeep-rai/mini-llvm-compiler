from llvmlite import ir
import re

# small experiment to understand how a compiler pipeline works
# input expression -> tokens -> AST -> LLVM IR


# token patterns for the lexer
TOKENS = [
    ("NUMBER", r"\d+"),
    ("PLUS", r"\+"),
    ("MINUS", r"-"),
    ("MUL", r"\*"),
    ("DIV", r"/"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)")
]


def tokenize(code):
    tokens = []

    # simple regex based lexer
    while code:

        code = code.lstrip()

        matched = False

        for name, pattern in TOKENS:

            match = re.match(pattern, code)

            if match:
                value = match.group(0)
                tokens.append((name, value))

                # remove matched part
                code = code[len(value):]

                matched = True
                break

        if not matched:
            raise Exception("Lexer error near: " + code)

    return tokens


# ---- AST nodes ----

class Number:
    def __init__(self, value):
        self.value = int(value)


class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


# just prints the AST so it's easier to see what the parser produced
def print_ast(node, indent=0):

    space = " " * indent

    if isinstance(node, Number):
        print(space + str(node.value))

    elif isinstance(node, BinOp):

        print(space + node.op)

        print_ast(node.left, indent + 2)
        print_ast(node.right, indent + 2)


# recursive descent parser
# grammar roughly:
# expr -> term ((+|-) term)*
# term -> factor ((*|/) factor)*
# factor -> NUMBER | "(" expr ")"

class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):

        if self.pos < len(self.tokens):
            return self.tokens[self.pos]

        return None

    def eat(self, token_type):

        token = self.current()

        if token and token[0] == token_type:
            self.pos += 1
            return token

        raise Exception("Unexpected token: " + str(token))

    def parse(self):
        return self.expr()

    def expr(self):

        node = self.term()

        while self.current() and self.current()[0] in ("PLUS", "MINUS"):

            token = self.current()
            self.eat(token[0])

            node = BinOp(node, token[1], self.term())

        return node

    def term(self):

        node = self.factor()

        while self.current() and self.current()[0] in ("MUL", "DIV"):

            token = self.current()
            self.eat(token[0])

            node = BinOp(node, token[1], self.factor())

        return node

    def factor(self):

        token = self.current()

        if token[0] == "NUMBER":

            self.eat("NUMBER")
            return Number(token[1])

        elif token[0] == "LPAREN":

            self.eat("LPAREN")

            node = self.expr()

            self.eat("RPAREN")

            return node

        raise Exception("Parse error")


# walks the AST and emits LLVM instructions
class CodeGen:

    def __init__(self):

        self.module = ir.Module(name="toy_module")

        func_type = ir.FunctionType(ir.IntType(32), [])

        self.func = ir.Function(self.module, func_type, name="main")

        block = self.func.append_basic_block(name="entry")

        self.builder = ir.IRBuilder(block)

    def generate(self, node):

        if isinstance(node, Number):

            return ir.Constant(ir.IntType(32), node.value)

        elif isinstance(node, BinOp):

            left = self.generate(node.left)
            right = self.generate(node.right)

            if node.op == "+":
                return self.builder.add(left, right)

            if node.op == "-":
                return self.builder.sub(left, right)

            if node.op == "*":
                return self.builder.mul(left, right)

            if node.op == "/":
                return self.builder.sdiv(left, right)

    def finish(self, value):
        self.builder.ret(value)


def main():

    code = input("Enter expression: ")

    tokens = tokenize(code)

    parser = Parser(tokens)
    ast = parser.parse()

    print("\nAST:")
    print_ast(ast)

    codegen = CodeGen()

    result = codegen.generate(ast)

    codegen.finish(result)

    print("\nGenerated LLVM IR:\n")
    print(codegen.module)


if __name__ == "__main__":
    main()
