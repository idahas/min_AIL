"""Parser for the Min language - Recursive descent with prefix notation."""

from .tokens import TT, Token
from .errors import SyntaxError
from .ast_nodes import (
    Number, String, Boolean, Null, Array, Object,
    Identifier, BinaryOp, UnaryOp, Assignment,
    DotAccess, IndexAccess, FunctionCall,
    If, While, For, Break, Continue, Return,
    FunctionDef, ClassDef, ObjectInit,
    Print, Input, Import, Export,
    TryCatch, Throw, MatchCase, Match, MultiAssignment, ListComprehension, Program
)


class Parser:
    """Parse tokens into AST."""
    
    def __init__(self, tokens: list[Token], filename: str = "<input>"):
        self.tokens = tokens
        self.filename = filename
        self.pos = 0
        self.errors = []
    
    def parse(self) -> Program:
        """Parse all tokens into a Program AST."""
        statements = []
        
        while not self.check(TT.EOF):
            stmt = self.parse_statement()
            if stmt:
                if isinstance(stmt, list):
                    statements.extend(stmt)
                else:
                    statements.append(stmt)
            self.skip_newlines()
        
        return Program(statements, filename=self.filename)
    
    def _pos(self, node, token: Token = None):
        """Attach line and column location from token to AST node."""
        if hasattr(node, 'line'):
            if node.line == 0:
                t = token if token is not None else self.peek()
                node.line = t.line
                node.col = t.col
        elif isinstance(node, list):
            for item in node:
                self._pos(item, token)
        return node
    
    # ─── Token Helpers ────────────────────────────────────────
    
    def peek(self) -> Token:
        return self.tokens[self.pos]
    
    def peek_token(self, offset: int = 0) -> Token:
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]
    
    def advance(self) -> Token:
        token = self.tokens[self.pos]
        self.pos += 1
        return token
    
    def check(self, tt: TT) -> bool:
        return self.peek().type == tt
    
    def expect(self, tt: TT) -> Token:
        if self.check(tt):
            return self.advance()
        token = self.peek()
        raise SyntaxError(
            f"Expected {tt.name}, got {token.type.name} ({token.value!r})",
            token.line, token.col
        )
    
    def match(self, tt: TT) -> Token | None:
        if self.check(tt):
            return self.advance()
        return None
    
    def skip_newlines(self):
        while self.check(TT.NEWLINE):
            self.advance()
    
    def at_statement_end(self) -> bool:
        return self.check(TT.NEWLINE) or self.check(TT.EOF) or self.check(TT.RBRACKET)
    
    # ─── Statements ───────────────────────────────────────────
    
    def parse_statement(self):
        start_token = self.peek()
        stmt = self._parse_statement_impl()
        return self._pos(stmt, start_token)
    
    def _parse_statement_impl(self):
        token = self.peek()
        
        # Block or destructuring assignment [:a :b] val or ListComprehension [for ...]
        if token.type == TT.LBRACKET:
            next_token = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if next_token and next_token.type == TT.COLON:
                self.advance()  # consume [
                targets = []
                while self.check(TT.COLON):
                    self.advance()
                    targets.append(self.expect(TT.IDENT).value)
                self.expect(TT.RBRACKET)
                val = self.parse_expression()
                return MultiAssignment(targets, val)
            if next_token and (next_token.type == TT.FOR or (next_token.type == TT.IDENT and next_token.value == 'for')):
                self.advance()  # consume [
                self.advance()  # consume for / !for
                var_name = self.expect(TT.IDENT).value
                iterable = self.parse_expression()
                cond = None
                if self.check(TT.QUESTION):
                    self.advance()
                    cond = self.parse_expression()
                expr = self.parse_expression()
                self.expect(TT.RBRACKET)
                return ListComprehension(var_name, iterable, expr, cond)
            return self.parse_block()
        
        # Variable assignment: :x expr or :x.field expr
        if token.type == TT.COLON:
            return self.parse_assignment()
        
        # Dot assignment: : x.field expr
        if token.type == TT.DOT:
            return self.parse_dot_assignment()
        
        # Index assignment: [ arr idx ] = val (handled in index access)
        
        # Commands starting with !
        if token.type == TT.BANG:
            return self.parse_command()
        
        # Keyword commands (lexer produces single token)
        if token.type == TT.PRINT:
            self.advance()
            return self.parse_print()
        if token.type == TT.INPUT:
            self.advance()
            return self.parse_input()
        if token.type == TT.WHILE:
            self.advance()
            return self.parse_while()
        if token.type == TT.FOR:
            self.advance()
            return self.parse_for()
        if token.type == TT.BREAK:
            self.advance()
            self.skip_newlines()
            return Break()
        if token.type == TT.CONTINUE:
            self.advance()
            self.skip_newlines()
            return Continue()
        if token.type == TT.RETURN:
            self.advance()
            return self.parse_return()
        if token.type == TT.IMPORT:
            self.advance()
            return self.parse_import()
        if token.type == TT.EXPORT:
            self.advance()
            return self.parse_export()
        if token.type == TT.TRY:
            self.advance()
            return self.parse_try_catch()
        if token.type == TT.THROW:
            self.advance()
            return self.parse_throw()
        if token.type == TT.CLASS:
            self.advance()
            return self.parse_class_def()
        if token.type == TT.NEW:
            self.advance()
            return self.parse_object_init()
        if token.type == TT.MATCH:
            self.advance()
            return self.parse_match()
        
        # If
        if token.type == TT.QUESTION:
            return self.parse_if()
        
        # Function definition @name
        if token.type == TT.AT:
            return self.parse_at_expr()
        
        # Return ~
        if token.type == TT.TILDE:
            return self.parse_return()
        
        # Everything else is an expression
        return self.parse_expression()
    
    def parse_block(self) -> list:
        """Parse a [...] block and return list of statements."""
        self.expect(TT.LBRACKET)
        self.skip_newlines()
        
        stmts = []
        while not self.check(TT.RBRACKET) and not self.check(TT.EOF):
            stmt = self.parse_statement()
            if stmt:
                if isinstance(stmt, list):
                    stmts.extend(stmt)
                else:
                    stmts.append(stmt)
            self.skip_newlines()
        
        self.expect(TT.RBRACKET)
        return stmts
    
    def parse_statement_single(self):
        """Parse a single statement (for loops, ifs)."""
        self.skip_newlines()
        token = self.peek()
        
        if token.type == TT.LBRACKET:
            return self.parse_block()
        
        stmt = self.parse_statement()
        self.skip_newlines()
        return [stmt] if stmt else []
    
    def parse_assignment(self):
        """Parse :name value or :name.field value."""
        self.expect(TT.COLON)
        name = self.parse_identifier_or_dot()
        value = self.parse_expression()
        return Assignment(name, value)
    
    def parse_dot_assignment(self):
        """Parse . obj field value."""
        self.expect(TT.DOT)
        obj = self.parse_expression()
        field = self.expect(TT.IDENT).value
        value = self.parse_expression()
        return Assignment(DotAccess(obj, field), value)
    
    def parse_command(self):
        """Parse commands: !print, !while, !for, etc."""
        token = self.expect(TT.BANG)
        
        # Peek at next token to determine command
        if self.check(TT.PRINT):
            self.advance()
            return self.parse_print()
        elif self.check(TT.INPUT):
            self.advance()
            return self.parse_input()
        elif self.check(TT.WHILE):
            self.advance()
            return self.parse_while()
        elif self.check(TT.FOR):
            self.advance()
            return self.parse_for()
        elif self.check(TT.BREAK):
            self.advance()
            self.skip_newlines()
            return Break()
        elif self.check(TT.CONTINUE):
            self.advance()
            self.skip_newlines()
            return Continue()
        elif self.check(TT.RETURN):
            self.advance()
            return self.parse_return()
        elif self.check(TT.IMPORT):
            self.advance()
            return self.parse_import()
        elif self.check(TT.EXPORT):
            self.advance()
            return self.parse_export()
        elif self.check(TT.TRY):
            self.advance()
            return self.parse_try_catch()
        elif self.check(TT.THROW):
            self.advance()
            return self.parse_throw()
        elif self.check(TT.CLASS):
            self.advance()
            return self.parse_class_def()
        elif self.check(TT.NEW):
            self.advance()
            return self.parse_object_init()
        elif self.check(TT.IDENT):
            # Method call: ! obj method args...
            obj = self.parse_expression()
            method = self.expect(TT.IDENT).value
            args = []
            while not self.at_statement_end() and not self.check(TT.RBRACKET):
                args.append(self.parse_expression())
            self.skip_newlines()
            return FunctionCall(DotAccess(obj, method), args)
        else:
            raise SyntaxError(
                f"Unknown command: !{self.peek().value}",
                token.line, token.col
            )
    
    def parse_if(self):
        """Parse ? condition [then] [else]"""
        self.expect(TT.QUESTION)
        condition = self.parse_expression()
        then_body = self.parse_block()
        self.skip_newlines()
        
        else_body = None
        if self.check(TT.ELSE):
            self.advance()
            else_body = self.parse_block()
        
        return If(condition, then_body, else_body)
    
    def parse_while(self):
        """Parse !while condition [body]"""
        condition = self.parse_expression()
        body = self.parse_block()
        return While(condition, body)
    
    def parse_for(self):
        """Parse !for [var start end] [body]"""
        self.expect(TT.LBRACKET)
        var = self.expect(TT.IDENT).value
        start = self.parse_expression()
        end = self.parse_expression()
        self.expect(TT.RBRACKET)
        
        body = self.parse_block()
        return For(var, start, end, body)
    
    def parse_return(self):
        """Parse !return expr or ~expr"""
        value = None
        if not self.at_statement_end():
            value = self.parse_expression()
        self.skip_newlines()
        return Return(value)
    
    def parse_print(self):
        """Parse !print args..."""
        args = []
        while not self.at_statement_end():
            args.append(self.parse_expression())
        self.skip_newlines()
        return Print(args)
    
    def parse_input(self):
        """Parse !input [prompt]"""
        prompt = None
        if not self.at_statement_end():
            prompt = self.parse_expression()
        self.skip_newlines()
        return Input(prompt)
    
    def parse_import(self):
        """Parse !import "module" [!as alias]"""
        module = self.expect(TT.STR).value
        alias = None
        if self.check(TT.AS):
            self.advance()
            alias = self.expect(TT.IDENT).value
        self.skip_newlines()
        return Import(module, alias)
    
    def parse_export(self):
        """Parse !export name"""
        name = self.expect(TT.IDENT).value
        self.skip_newlines()
        return Export(name)
    
    def parse_try_catch(self):
        """Parse !try [body] !catch (var) [body]"""
        try_body = self.parse_block()
        self.skip_newlines()
        if self.check(TT.BANG):
            self.advance()
        self.expect(TT.CATCH)
        self.expect(TT.LPAREN)
        catch_var = self.expect(TT.IDENT).value
        self.expect(TT.RPAREN)
        catch_body = self.parse_block()
        return TryCatch(try_body, catch_var, catch_body)
    
    def parse_throw(self):
        """Parse !throw expr"""
        message = self.parse_expression()
        return Throw(message)
    
    def parse_function_def(self):
        """Parse @name(params) [body]"""
        self.expect(TT.AT)
        name = self.expect(TT.IDENT).value
        
        # Parameters
        self.expect(TT.LPAREN)
        params = []
        if not self.check(TT.RPAREN):
            params.append(self.expect(TT.IDENT).value)
            while self.check(TT.COLON):
                self.advance()
                params.append(self.expect(TT.IDENT).value)
        self.expect(TT.RPAREN)
        
        # Body
        body = self.parse_block()
        return FunctionDef(name, params, body)
    
    def parse_class_def(self):
        """Parse !class Name [!extends Parent] [fields... @methods...]"""
        name = self.expect(TT.IDENT).value
        
        # Optional parent class
        super_class = None
        if self.check(TT.EXTENDS):
            self.advance()
            super_class = self.expect(TT.IDENT).value
        
        self.skip_newlines()
        
        has_bracket = False
        if self.check(TT.LBRACKET):
            self.advance()
            has_bracket = True
        self.skip_newlines()
        
        fields = {}
        methods = []
        init_method = None
        
        while not self.check(TT.EOF):
            if has_bracket and self.check(TT.RBRACKET):
                break
            if not has_bracket:
                if self.check(TT.AT):
                    pass
                elif self.check(TT.IDENT) and self.peek_token(1).type == TT.COLON:
                    pass
                else:
                    break
            if self.check(TT.AT):
                method = self.parse_at_expr()
                if isinstance(method, FunctionDef) and method.name == 'init':
                    init_method = method
                elif isinstance(method, FunctionDef):
                    methods.append(method)
            elif self.check(TT.IDENT):
                field_name = self.advance().value
                self.expect(TT.COLON)
                field_val = self.parse_expression()
                fields[field_name] = field_val
            else:
                self.advance()  # skip unexpected
            self.skip_newlines()
        
        if has_bracket or self.check(TT.RBRACKET):
            if self.check(TT.RBRACKET):
                self.advance()
        self.skip_newlines()
        return ClassDef(name, super_class, fields, methods, init_method)
    
    def parse_object_init(self):
        """Parse !new ClassName(args...)"""
        if self.check(TT.NEW):
            self.advance()
        class_name = self.expect(TT.IDENT).value
        self.expect(TT.LPAREN)
        args = []
        if not self.check(TT.RPAREN):
            args.append(self.parse_expression())
            while self.match(TT.COLON):
                args.append(self.parse_expression())
        self.expect(TT.RPAREN)
        return ObjectInit(class_name, args)
    
    def parse_at_expr(self):
        """Parse @func(params) [body] (definition), @(params) [body] (anonymous lambda), or @func(args) (call)."""
        self.expect(TT.AT)
        
        # Anonymous lambda: @(params) [body]
        if self.check(TT.LPAREN):
            self.expect(TT.LPAREN)
            params = []
            defaults = {}
            vararg = None
            
            while not self.check(TT.RPAREN) and not self.check(TT.EOF):
                if self.check(TT.COLON):
                    self.advance()
                    continue
                tok = self.peek()
                if tok.type == TT.IDENT and (tok.value.startswith('...') or tok.value.startswith('*')):
                    vararg = self.advance().value.lstrip('.*')
                    continue
                if tok.type == TT.IDENT:
                    p_name = self.advance().value
                    params.append(p_name)
                    if self.check(TT.EQ) or self.check(TT.COLON):
                        self.advance()
                        defaults[p_name] = self.parse_expression()
                else:
                    break
            self.expect(TT.RPAREN)
            body = self.parse_block()
            return FunctionDef("", params, body, defaults=defaults, vararg=vararg)

        name = self.expect(TT.IDENT).value
        self.expect(TT.LPAREN)
        
        # Check if followed by [ after ) -> Function definition
        # Parse parameters
        params = []
        defaults = {}
        vararg = None
        args = []
        is_def = False
        
        # Peek ahead to check if this is function definition or call
        # If followed by LBRACKET after matching RPAREN, it's a definition
        saved_pos = self.pos
        paren_depth = 1
        has_lbracket_after = False
        while saved_pos < len(self.tokens) and paren_depth > 0:
            if self.tokens[saved_pos].type == TT.LPAREN:
                paren_depth += 1
            elif self.tokens[saved_pos].type == TT.RPAREN:
                paren_depth -= 1
            saved_pos += 1
        
        # Skip trailing newlines after RPAREN
        while saved_pos < len(self.tokens) and self.tokens[saved_pos].type == TT.NEWLINE:
            saved_pos += 1
        
        if saved_pos < len(self.tokens) and self.tokens[saved_pos].type == TT.LBRACKET:
            is_def = True

        if is_def:
            while not self.check(TT.RPAREN) and not self.check(TT.EOF):
                if self.check(TT.COLON):
                    self.advance()
                    continue
                if self.check(TT.STAR) or self.check(TT.DOT):
                    while self.check(TT.STAR) or self.check(TT.DOT):
                        self.advance()
                    vararg = self.expect(TT.IDENT).value
                    continue
                tok = self.peek()
                if tok.type == TT.IDENT:
                    p_name = self.advance().value
                    params.append(p_name)
                    if self.check(TT.EQ) or self.check(TT.COLON):
                        self.advance()
                        defaults[p_name] = self.parse_expression()
                else:
                    break
            self.expect(TT.RPAREN)
            body = self.parse_block()
            return FunctionDef(name, params, body, defaults=defaults, vararg=vararg)
        else:
            if not self.check(TT.RPAREN):
                args.append(self.parse_expression())
                while self.match(TT.COLON) or (not self.check(TT.RPAREN) and not self.check(TT.LBRACKET)):
                    if self.check(TT.RPAREN) or self.check(TT.LBRACKET):
                        break
                    if self.check(TT.COLON):
                        self.advance()
                    args.append(self.parse_expression())
            self.expect(TT.RPAREN)
            return FunctionCall(Identifier(name), args)
    
    def parse_identifier_or_dot(self):
        """Parse identifier or dot access chain."""
        name = self.expect(TT.IDENT).value
        
        while self.check(TT.DOT):
            self.advance()
            member = self.expect(TT.IDENT).value
            name = DotAccess(Identifier(name) if isinstance(name, str) else name, member)
        
        return name if not isinstance(name, str) else Identifier(name)
    
    # ─── Expressions ──────────────────────────────────────────
    
    def parse_expression(self):
        """Parse an expression."""
        start_token = self.peek()
        expr = self._parse_expression_impl()
        return self._pos(expr, start_token)
    
    def _parse_expression_impl(self):
        token = self.peek()
        
        # Number
        if token.type == TT.NUM:
            self.advance()
            return Number(token.value)
        
        # String
        if token.type == TT.STR:
            self.advance()
            return String(token.value)
        
        # Boolean
        if token.type == TT.BOOL:
            self.advance()
            return Boolean(token.value)
        
        # Null
        if token.type == TT.NULL:
            self.advance()
            return Null()
        
        # Array
        if token.type == TT.LBRACKET:
            return self.parse_array()
        
        # Object
        if token.type == TT.LBRACE:
            return self.parse_object()
        
        # Dot access: . obj field  or  . obj idx (index)
        if token.type == TT.DOT:
            self.advance()
            obj = self.parse_expression()
            if self.check(TT.IDENT):
                field = self.advance().value
                return DotAccess(obj, field)
            else:
                idx = self.parse_expression()
                return IndexAccess(obj, idx)
        
        # Identifier or dot access
        if token.type == TT.IDENT:
            return self.parse_identifier_expr()
        
        # @ for function definition or call
        if token.type == TT.AT:
            return self.parse_at_expr()
        
        # !new ClassName(args)
        if token.type == TT.NEW:
            return self.parse_object_init()
        
        # Grouped expression
        if token.type == TT.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TT.RPAREN)
            return expr
        
        # Binary/unary operators
        if token.type in (TT.PLUS, TT.MINUS, TT.STAR, TT.SLASH, TT.PERCENT,
                          TT.EQ, TT.GT, TT.LT, TT.GTE, TT.LTE, TT.NEQ,
                          TT.AND, TT.OR):
            return self.parse_binary_op()
        
        if token.type == TT.BANG:
            return self.parse_unary_op()
        
        raise SyntaxError(
            f"Unexpected token: {token.type.name} ({token.value!r})",
            token.line, token.col
        )
    
    def parse_array(self):
        """Parse [ elements... ] or [for var iterable expr]"""
        self.expect(TT.LBRACKET)
        tok = self.peek()
        if tok.type == TT.FOR or (tok.type == TT.IDENT and tok.value == 'for'):
            self.advance()  # consume for / !for
            var_name = self.expect(TT.IDENT).value
            iterable = self.parse_expression()
            cond = None
            if self.check(TT.QUESTION):
                self.advance()
                cond = self.parse_expression()
            expr = self.parse_expression()
            self.expect(TT.RBRACKET)
            return ListComprehension(var_name, iterable, expr, cond)

        elements = []
        if not self.check(TT.RBRACKET):
            elements.append(self.parse_expression())
            while self.match(TT.COLON):
                elements.append(self.parse_expression())
        
        self.expect(TT.RBRACKET)
        return Array(elements)
    
    def parse_object(self):
        """Parse { key: value, ... }"""
        self.expect(TT.LBRACE)
        pairs = {}
        
        while not self.check(TT.RBRACE) and not self.check(TT.EOF):
            key = self.expect(TT.IDENT).value
            self.expect(TT.COLON)
            value = self.parse_expression()
            pairs[key] = value
            self.match(TT.COLON)  # optional separator
        
        self.expect(TT.RBRACE)
        return Object(pairs)
    
    def parse_identifier_expr(self):
        """Parse identifier, dot access, or index access."""
        name = self.expect(TT.IDENT).value
        node = Identifier(name)
        
        while True:
            # Dot access: obj.field
            if self.check(TT.DOT):
                self.advance()
                member = self.expect(TT.IDENT).value
                node = DotAccess(node, member)
            
            # Index access: obj[idx]
            elif self.check(TT.LBRACKET):
                self.advance()
                index = self.parse_expression()
                self.expect(TT.RBRACKET)
                node = IndexAccess(node, index)
            
            else:
                break
        
        return node
    
    def parse_binary_op(self):
        """Parse binary operation (prefix notation: + a b)."""
        op_token = self.advance()
        op = op_token.value
        left = self.parse_expression()
        right = self.parse_expression()
        return BinaryOp(op, left, right)
    
    def parse_unary_op(self):
        """Parse unary operation (prefix: !expr)."""
        op_token = self.advance()
        operand = self.parse_expression()
        return UnaryOp(op_token.value, operand)


    def parse_match(self):
        """Parse !match expr [ pattern [body] ... !else [default_body] ]"""
        expr = self.parse_expression()
        self.expect(TT.LBRACKET)
        
        cases = []
        default_body = None
        
        while not self.check(TT.RBRACKET) and not self.check(TT.EOF):
            self.skip_newlines()
            if self.check(TT.RBRACKET):
                break
            
            if self.check(TT.ELSE):
                self.advance()
                default_body = self.parse_block()
                self.skip_newlines()
                break
            
            pattern = self.parse_expression()
            body = self.parse_block()
            cases.append(MatchCase(pattern=pattern, body=body))
            self.skip_newlines()
        
        self.skip_newlines()
        self.expect(TT.RBRACKET)
        return Match(expr=expr, cases=cases, default_body=default_body)


def parse(tokens: list[Token], filename: str = "<input>") -> Program:
    """Convenience function to parse tokens."""
    return Parser(tokens, filename=filename).parse()
