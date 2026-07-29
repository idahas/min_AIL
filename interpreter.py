"""Tree-walking interpreter for the Min language."""

from .ast_nodes import *
from .errors import (
    MinError, RuntimeError as MinRuntimeError, TypeError as MinTypeError,
    NameError, IndexError, ArgumentError, AttributeError, CallFrame
)


# ─── Environment (variable scope) ────────────────────────────

class Environment:
    """Variable scope."""
    
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent
        self.explicit_exports = set()
    
    def get(self, name: str):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Undefined: {name}")
    
    def set(self, name: str, value):
        self.vars[name] = value
    
    def assign(self, name: str, value):
        if name in self.vars:
            self.vars[name] = value
            return
        if self.parent:
            try:
                self.parent.assign(name, value)
                return
            except NameError:
                pass
        raise NameError(f"Undefined: {name}")


# ─── Return/Break/Continue signals ────────────────────────────

class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value

class BreakSignal(Exception):
    pass

class ContinueSignal(Exception):
    pass


# ─── Min Objects ──────────────────────────────────────────────

class BoundMethod:
    """A method bound to an instance."""
    def __init__(self, instance, method):
        self.instance = instance
        self.method = method


class MinInstance:
    """Instance of a Min class."""
    
    def __init__(self, class_def, parent_instance=None):
        self.class_def = class_def
        self.fields = dict(class_def.fields)
        self.methods = {}
        
        # Inherit parent methods
        if parent_instance:
            self.fields = {**parent_instance.fields, **self.fields}
            self.methods = dict(parent_instance.methods)
        
        for method in class_def.methods:
            self.methods[method.name] = method
        if class_def.init_method:
            self.methods['init'] = class_def.init_method
    
    def get(self, name: str):
        if name in self.fields:
            return self.fields[name]
        if name in self.methods:
            return self.methods[name]
        raise AttributeError(f"'{self.class_def.name}' has no attribute '{name}'")
    
    def set(self, name: str, value):
        self.fields[name] = value
    
    def __repr__(self):
        return f"<{self.class_def.name} {self.fields}>"


# ─── Interpreter ──────────────────────────────────────────────

class Interpreter:
    """Execute AST nodes."""
    
    def __init__(self, filename: str = "<input>", source: str | None = None):
        self.global_env = Environment()
        self.current_env = self.global_env
        self.modules = {}  # imported modules cache
        self.filename = filename
        self.source = source
        self.call_stack: list[CallFrame] = []
        self.current_line: int = 0
        self.current_col: int = 0
        
        # Register built-in functions
        self._register_builtins()
    
    def _register_builtins(self):
        """Register built-in functions."""
        from .builtins import BUILTINS
        for name, func in BUILTINS.items():
            self.global_env.set(name, func)
    
    def run(self, program: Program):
        """Execute a program."""
        if hasattr(program, 'filename') and program.filename:
            self.filename = program.filename
        return self.exec_block(program.statements, self.current_env)
    
    def exec_block(self, statements: list[Node], env: Environment):
        """Execute a list of statements."""
        old_env = self.current_env
        self.current_env = env
        result = None
        
        for stmt in statements:
            if isinstance(stmt, list):
                for s in stmt:
                    result = self.exec(s)
            else:
                result = self.exec(stmt)
        
        self.current_env = old_env
        return result
    
    def exec(self, node: Node):
        """Execute a single node."""
        old_line = self.current_line
        old_col = self.current_col
        if hasattr(node, 'line') and node.line > 0:
            self.current_line = node.line
            self.current_col = node.col
        
        try:
            return self._exec_internal(node)
        except MinError as e:
            if not e.line:
                e.line = self.current_line
                e.col = self.current_col
            if e.filename == "<input>" and self.filename != "<input>":
                e.filename = self.filename
            if not e.source and self.source:
                e.source = self.source
            if not e.stack_trace and self.call_stack:
                e.stack_trace = list(self.call_stack)
            raise e
        except (ReturnSignal, BreakSignal, ContinueSignal):
            raise
        except Exception as py_err:
            err_msg = str(py_err)
            if isinstance(py_err, ZeroDivisionError):
                err_msg = "Division by zero"
            elif isinstance(py_err, TypeError):
                err_msg = f"Type error: {py_err}"
            elif isinstance(py_err, IndexError):
                err_msg = f"Index out of range: {py_err}"
            elif isinstance(py_err, KeyError):
                err_msg = f"Key error: {py_err}"
            
            min_err = MinRuntimeError(
                message=err_msg,
                line=self.current_line,
                col=self.current_col,
                filename=self.filename,
                stack_trace=list(self.call_stack),
                source=self.source
            )
            raise min_err from py_err
        finally:
            self.current_line = old_line
            self.current_col = old_col

    def _exec_internal(self, node: Node):
        """Execute a single node."""
        if isinstance(node, Number):
            return node.value
        if isinstance(node, String):
            return node.value
        if isinstance(node, Boolean):
            return node.value
        if isinstance(node, Null):
            return None
        if isinstance(node, Identifier):
            return self.current_env.get(node.name)
        if isinstance(node, Array):
            return [self.exec(e) for e in node.elements]
        if isinstance(node, Object):
            return {k: self.exec(v) for k, v in node.pairs.items()}
        
        if isinstance(node, Assignment):
            value = self.exec(node.value)
            if isinstance(node.name, Identifier):
                # Check if this is an instance field (via self/this)
                name = node.name.name
                try:
                    self_obj = self.current_env.get('self')
                    if isinstance(self_obj, MinInstance) and name in self_obj.fields:
                        self_obj.set(name, value)
                        return value
                except NameError:
                    pass
                try:
                    self.current_env.assign(name, value)
                except NameError:
                    self.current_env.set(name, value)
            elif isinstance(node.name, DotAccess):
                obj = self.exec(node.name.object)
                if isinstance(obj, MinInstance):
                    obj.set(node.name.member, value)
                elif isinstance(obj, dict):
                    obj[node.name.member] = value
                else:
                    raise MinRuntimeError("Cannot set attribute on non-object")
            elif isinstance(node.name, IndexAccess):
                obj = self.exec(node.name.object)
                idx = self.exec(node.name.index)
                if isinstance(obj, list):
                    obj[int(idx)] = value
                elif isinstance(obj, dict):
                    obj[idx] = value
                else:
                    raise MinRuntimeError("Cannot index non-collection")
            return value
        
        if isinstance(node, DotAccess):
            obj = self.exec(node.object)
            if isinstance(obj, MinInstance):
                val = obj.get(node.member)
                if isinstance(val, FunctionDef):
                    return BoundMethod(obj, val)
                return val
            if isinstance(obj, dict):
                if node.member in obj:
                    return obj[node.member]
                raise AttributeError(f"Key not found: {node.member}")
            if isinstance(obj, list) and node.member == 'length':
                return len(obj)
            if isinstance(obj, str) and node.member == 'length':
                return len(obj)
            raise MinRuntimeError(f"Cannot access '{node.member}'")
        
        if isinstance(node, IndexAccess):
            obj = self.exec(node.object)
            idx = self.exec(node.index)
            if isinstance(obj, list):
                return obj[int(idx)]
            if isinstance(obj, dict):
                return obj[idx]
            if isinstance(obj, str):
                return obj[int(idx)]
            raise MinRuntimeError("Cannot index non-collection")
        
        if isinstance(node, FunctionCall):
            callee = self.exec(node.callee)
            args = [self.exec(a) for a in node.args]
            return self.call_function(callee, args)
        
        if isinstance(node, BinaryOp):
            return self.exec_binary(node)
        if isinstance(node, UnaryOp):
            return self.exec_unary(node)
        
        if isinstance(node, If):
            return self.exec_if(node)
        if isinstance(node, While):
            return self.exec_while(node)
        if isinstance(node, For):
            return self.exec_for(node)
        if isinstance(node, Break):
            raise BreakSignal()
        if isinstance(node, Continue):
            raise ContinueSignal()
        if isinstance(node, Return):
            return ReturnSignal(self.exec(node.value) if node.value else None)
        
        if isinstance(node, FunctionDef):
            if node.name:
                self.current_env.set(node.name, node)
            return node
        if isinstance(node, ClassDef):
            self.current_env.set(node.name, node)
            return node
        if isinstance(node, ObjectInit):
            return self.exec_object_init(node)
        
        if isinstance(node, Match):
            val = self.exec(node.expr)
            for case in node.cases:
                pat_val = self.exec(case.pattern)
                if val == pat_val:
                    res = self.exec_block(case.body, Environment(self.current_env))
                    if isinstance(res, ReturnSignal):
                        return res.value
                    return res
            if node.default_body:
                res = self.exec_block(node.default_body, Environment(self.current_env))
                if isinstance(res, ReturnSignal):
                    return res.value
                return res
            return None
        
        if isinstance(node, Print):
            self.exec_print(node)
            return None
        if isinstance(node, Input):
            return self.exec_input(node)
        
        if isinstance(node, Import):
            return self.exec_import(node)
        if isinstance(node, Export):
            self.current_env.explicit_exports.add(node.name)
            return self.current_env.get(node.name)
        
        if isinstance(node, TryCatch):
            return self.exec_try_catch(node)
        if isinstance(node, Throw):
            raise MinRuntimeError(str(self.exec(node.message)))
        
        if isinstance(node, Program):
            return self.run(node)
        
        raise MinRuntimeError(f"Unknown node type: {type(node).__name__}")
    
    # ─── Binary & Unary ───────────────────────────────────────
    
    def exec_binary(self, node: BinaryOp):
        left = self.exec(node.left)
        right = self.exec(node.right)
        
        op = node.op
        if op == '+':
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            return left + right
        if op == '-':
            return left - right
        if op == '*':
            return left * right
        if op == '/':
            return left / right
        if op == '%':
            return left % right
        if op == '=':
            return left == right
        if op == '!=':
            return left != right
        if op == '>':
            return left > right
        if op == '<':
            return left < right
        if op == '>=':
            return left >= right
        if op == '<=':
            return left <= right
        if op == '&':
            return left and right
        if op == '|':
            return left or right
        
        raise MinRuntimeError(f"Unknown operator: {op}")
    
    def exec_unary(self, node: UnaryOp):
        operand = self.exec(node.operand)
        if node.op == '!':
            return not operand
        if node.op == '-':
            return -operand
        raise MinRuntimeError(f"Unknown unary operator: {node.op}")
    
    # ─── Control Flow ─────────────────────────────────────────
    
    def exec_if(self, node: If):
        if self.exec(node.condition):
            return self.exec_block(node.then_body, Environment(self.current_env))
        elif node.else_body:
            return self.exec_block(node.else_body, Environment(self.current_env))
        return None
    
    def exec_while(self, node: While):
        env = Environment(self.current_env)
        while self.exec(node.condition):
            try:
                self.exec_block(node.body, env)
            except BreakSignal:
                break
            except ContinueSignal:
                continue
        return None
    
    def exec_for(self, node: For):
        env = Environment(self.current_env)
        start = int(self.exec(node.start))
        end = int(self.exec(node.end))
        for i in range(start, end):
            env.set(node.var, i)
            try:
                self.exec_block(node.body, env)
            except BreakSignal:
                break
            except ContinueSignal:
                continue
        return None
    
    # ─── Functions & Classes ──────────────────────────────────
    
    def call_function(self, callee, args: list):
        # Bound method
        if isinstance(callee, BoundMethod):
            env = Environment(self.current_env)
            env.set('self', callee.instance)
            env.set('this', callee.instance)
            # Copy instance fields into method scope
            for k, v in callee.instance.fields.items():
                if k not in env.vars:
                    env.set(k, v)
            if len(args) != len(callee.method.params):
                raise ArgumentError(
                    f"Expected {len(callee.method.params)} args, got {len(args)}"
                )
            for param, arg in zip(callee.method.params, args):
                env.set(param, arg)
            
            fn_name = callee.method.name if callee.method.name.startswith('@') else f"@{callee.method.name}"
            frame = CallFrame(fn_name=fn_name, filename=self.filename, line=self.current_line, col=self.current_col)
            self.call_stack.append(frame)
            try:
                result = self.exec_block(callee.method.body, env)
                if isinstance(result, ReturnSignal):
                    return result.value
                return result
            finally:
                self.call_stack.pop()
        
        # Built-in function (Python callable)
        if callable(callee) and not isinstance(callee, (FunctionDef, MinInstance)):
            import inspect
            try:
                sig = inspect.signature(callee)
                if 'interp' in sig.parameters:
                    return callee(args, interp=self)
            except (ValueError, TypeError):
                pass
            return callee(args)
        
        # User-defined function
        if isinstance(callee, FunctionDef):
            if len(args) != len(callee.params):
                raise ArgumentError(
                    f"Expected {len(callee.params)} args, got {len(args)}"
                )
            env = Environment(self.current_env)
            for param, arg in zip(callee.params, args):
                env.set(param, arg)
            
            fn_name = callee.name if callee.name.startswith('@') else f"@{callee.name}"
            frame = CallFrame(fn_name=fn_name, filename=self.filename, line=self.current_line, col=self.current_col)
            self.call_stack.append(frame)
            try:
                result = self.exec_block(callee.body, env)
                if isinstance(result, ReturnSignal):
                    return result.value
                return result
            finally:
                self.call_stack.pop()
        
        # Method call
        if isinstance(callee, MinInstance):
            return callee
        
        raise MinRuntimeError(f"Cannot call: {type(callee).__name__}")
    
    def exec_object_init(self, node: ObjectInit):
        class_def = self.current_env.get(node.class_name)
        
        if not isinstance(class_def, ClassDef):
            raise MinRuntimeError(f"{node.class_name} is not a class")
        
        parent_instance = None
        if class_def.super_class:
            try:
                super_def = self.current_env.get(class_def.super_class)
                if isinstance(super_def, ClassDef):
                    parent_instance = MinInstance(super_def)
            except NameError:
                pass
        
        instance = MinInstance(class_def, parent_instance)
        
        if class_def.init_method:
            args = [self.exec(a) for a in node.args]
            env = Environment(self.current_env)
            env.set('self', instance)
            env.set('this', instance)
            for k, v in instance.fields.items():
                if k not in env.vars:
                    env.set(k, v)
            for param, arg in zip(class_def.init_method.params, args):
                env.set(param, arg)
            
            frame = CallFrame(fn_name=f"@{class_def.name}.init", filename=self.filename, line=self.current_line, col=self.current_col)
            self.call_stack.append(frame)
            try:
                result = self.exec_block(class_def.init_method.body, env)
                if isinstance(result, ReturnSignal):
                    return result.value
            finally:
                self.call_stack.pop()
        
        return instance
    
    # ─── I/O ──────────────────────────────────────────────────
    
    def exec_print(self, node: Print):
        values = [self.exec(a) for a in node.args]
        print(*values)
    
    def exec_input(self, node: Input):
        if node.prompt:
            prompt = self.exec(node.prompt)
        else:
            prompt = ""
        return input(str(prompt))
    
    # ─── Modules ──────────────────────────────────────────────
    
    def exec_import(self, node: Import):
        from .builtins import STD_MODULES
        
        # 1. Virtual Standard Library Modules (std/math, std/io, std/string, std/array)
        if node.module in STD_MODULES:
            exports = STD_MODULES[node.module]
            alias = node.alias or node.module.split('/')[-1]
            self.current_env.set(alias, exports)
            return exports

        import os
        from .lexer import tokenize
        from .parser import parse

        # 2. Resolve relative path based on current file's directory
        rel_dir = os.path.dirname(os.path.abspath(self.filename)) if self.filename and self.filename != "<input>" else os.getcwd()
        
        module_name = node.module if node.module.endswith('.min') else node.module + '.min'
        
        target_path = os.path.normpath(os.path.join(rel_dir, module_name))
        if not os.path.exists(target_path):
            fallback_path = os.path.normpath(os.path.abspath(module_name))
            if os.path.exists(fallback_path):
                target_path = fallback_path
            else:
                raise ImportError(f"Module not found: {node.module}")
        
        # 3. Check module cache using normalized path
        if target_path in self.modules:
            exports = self.modules[target_path]
            alias = node.alias or os.path.splitext(os.path.basename(target_path))[0]
            self.current_env.set(alias, exports)
            return exports
        
        with open(target_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        tokens = tokenize(source)
        ast = parse(tokens, filename=target_path)
        
        # 4. Create module environment and execute in child interpreter
        module_env = Environment(self.global_env)
        old_env = self.current_env
        self.current_env = module_env
        
        sub_interp = Interpreter(filename=target_path, source=source)
        sub_interp.global_env = self.global_env
        sub_interp.current_env = module_env
        sub_interp.run(ast)
        
        self.current_env = old_env
        
        # 5. Extract exports: explicit !export list or all non-underscored names
        exports = {}
        if module_env.explicit_exports:
            for name in module_env.explicit_exports:
                if name in module_env.vars:
                    exports[name] = module_env.vars[name]
        else:
            for name, val in module_env.vars.items():
                if not name.startswith('_'):
                    exports[name] = val
        
        self.modules[target_path] = exports
        alias = node.alias or os.path.splitext(os.path.basename(target_path))[0]
        self.current_env.set(alias, exports)
        return exports
    
    # ─── Error Handling ───────────────────────────────────────
    
    def exec_try_catch(self, node: TryCatch):
        try:
            return self.exec_block(node.try_body, Environment(self.current_env))
        except MinError as e:
            env = Environment(self.current_env)
            env.set(node.catch_var, e.message if hasattr(e, 'message') else str(e))
            return self.exec_block(node.catch_body, env)
