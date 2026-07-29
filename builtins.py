"""Built-in functions for the Min language."""

import os
import math
import time
import random
from .errors import ArgumentError, TypeError as MinTypeError, RuntimeError as MinRuntimeError


def _len(args):
    if len(args) != 1:
        raise ArgumentError("len expects 1 argument")
    val = args[0]
    if isinstance(val, (list, str, dict)):
        return len(val)
    raise MinTypeError(f"len not supported for {type(val).__name__}")


def _type(args):
    if len(args) != 1:
        raise ArgumentError("type expects 1 argument")
    val = args[0]
    if val is None:
        return "null"
    if isinstance(val, bool):
        return "bool"
    if isinstance(val, int):
        return "int"
    if isinstance(val, float):
        return "float"
    if isinstance(val, str):
        return "string"
    if isinstance(val, list):
        return "array"
    if isinstance(val, dict):
        return "object"
    return "unknown"


def _str(args):
    if len(args) != 1:
        raise ArgumentError("str expects 1 argument")
    return str(args[0])


def _num(args):
    if len(args) != 1:
        raise ArgumentError("num expects 1 argument")
    try:
        return float(args[0])
    except (ValueError, TypeError):
        raise MinTypeError(f"Cannot convert to number: {args[0]!r}")


def _int(args):
    if len(args) != 1:
        raise ArgumentError("int expects 1 argument")
    try:
        return int(args[0])
    except (ValueError, TypeError):
        raise MinTypeError(f"Cannot convert to int: {args[0]!r}")


def _abs(args):
    if len(args) != 1:
        raise ArgumentError("abs expects 1 argument")
    return abs(args[0])


def _sqrt(args):
    if len(args) != 1:
        raise ArgumentError("sqrt expects 1 argument")
    return math.sqrt(args[0])


def _pow(args):
    if len(args) != 2:
        raise ArgumentError("pow expects 2 arguments (base, exp)")
    return math.pow(args[0], args[1])


def _floor(args):
    if len(args) != 1:
        raise ArgumentError("floor expects 1 argument")
    return math.floor(args[0])


def _ceil(args):
    if len(args) != 1:
        raise ArgumentError("ceil expects 1 argument")
    return math.ceil(args[0])


def _round(args):
    if len(args) == 1:
        return round(args[0])
    elif len(args) == 2:
        return round(args[0], int(args[1]))
    raise ArgumentError("round expects 1 or 2 arguments")


def _random(args):
    return random.random()


def _randint(args):
    if len(args) != 2:
        raise ArgumentError("randint expects 2 arguments (min, max)")
    return random.randint(int(args[0]), int(args[1]))


def _min_val(args):
    if len(args) < 1:
        raise ArgumentError("min expects at least 1 argument")
    if len(args) == 1 and isinstance(args[0], list):
        return min(args[0])
    return min(args)


def _max_val(args):
    if len(args) < 1:
        raise ArgumentError("max expects at least 1 argument")
    if len(args) == 1 and isinstance(args[0], list):
        return max(args[0])
    return max(args)


def _range_val(args):
    if len(args) == 1:
        return list(range(int(args[0])))
    elif len(args) == 2:
        return list(range(int(args[0]), int(args[1])))
    elif len(args) == 3:
        return list(range(int(args[0]), int(args[1]), int(args[2])))
    raise ArgumentError("range expects 1-3 arguments")


def _push(args):
    if len(args) < 2:
        raise ArgumentError("push expects array and value")
    arr = args[0]
    if not isinstance(arr, list):
        raise MinTypeError("push requires array")
    for val in args[1:]:
        arr.append(val)
    return arr


def _pop(args):
    if len(args) != 1:
        raise ArgumentError("pop expects 1 argument")
    arr = args[0]
    if not isinstance(arr, list):
        raise MinTypeError("pop requires array")
    if not arr:
        raise MinTypeError("pop from empty array")
    return arr.pop()


def _slice(args):
    if len(args) < 2:
        raise ArgumentError("slice expects at least 2 arguments")
    obj = args[0]
    start = int(args[1])
    if len(args) > 2:
        end = int(args[2])
        return obj[start:end]
    return obj[start:]


def _keys(args):
    if len(args) != 1:
        raise ArgumentError("keys expects 1 argument")
    obj = args[0]
    if not isinstance(obj, dict):
        raise MinTypeError("keys requires object")
    return list(obj.keys())


def _values(args):
    if len(args) != 1:
        raise ArgumentError("values expects 1 argument")
    obj = args[0]
    if not isinstance(obj, dict):
        raise MinTypeError("values requires object")
    return list(obj.values())


def _has(args):
    if len(args) != 2:
        raise ArgumentError("has expects 2 arguments")
    obj = args[0]
    key = args[1]
    if isinstance(obj, dict):
        return key in obj
    if isinstance(obj, list):
        return key in obj
    if isinstance(obj, str):
        return key in obj
    return False


def _join(args):
    if len(args) < 2:
        raise ArgumentError("join expects separator and array")
    sep = str(args[0])
    arr = args[1]
    if not isinstance(arr, list):
        raise MinTypeError("join requires array")
    return sep.join(str(x) for x in arr)


def _split(args):
    if len(args) < 2:
        raise ArgumentError("split expects string and separator")
    s = str(args[0])
    sep = str(args[1])
    return s.split(sep)


def _replace(args):
    if len(args) != 3:
        raise ArgumentError("replace expects 3 arguments")
    s = str(args[0])
    old = str(args[1])
    new = str(args[2])
    return s.replace(old, new)


def _upper(args):
    if len(args) != 1:
        raise ArgumentError("upper expects 1 argument")
    return str(args[0]).upper()


def _lower(args):
    if len(args) != 1:
        raise ArgumentError("lower expects 1 argument")
    return str(args[0]).lower()


def _trim(args):
    if len(args) != 1:
        raise ArgumentError("trim expects 1 argument")
    return str(args[0]).strip()


def _contains(args):
    if len(args) != 2:
        raise ArgumentError("contains expects 2 arguments")
    container = args[0]
    item = args[1]
    return item in container


def _reverse(args):
    if len(args) != 1:
        raise ArgumentError("reverse expects 1 argument")
    obj = args[0]
    if isinstance(obj, list):
        return list(reversed(obj))
    if isinstance(obj, str):
        return obj[::-1]
    raise MinTypeError("reverse requires array or string")


def _sort(args):
    if len(args) != 1:
        raise ArgumentError("sort expects 1 argument")
    arr = args[0]
    if not isinstance(arr, list):
        raise MinTypeError("sort requires array")
    return sorted(arr)


def _map(args, interp=None):
    if len(args) != 2:
        raise ArgumentError("map expects array and function")
    arr = args[0]
    func = args[1]
    if not isinstance(arr, list):
        raise MinTypeError("map requires array")
    if interp is None:
        from .interpreter import Interpreter
        interp = Interpreter()
    return [interp.call_function(func, [x]) for x in arr]


def _filter(args, interp=None):
    if len(args) != 2:
        raise ArgumentError("filter expects array and function")
    arr = args[0]
    func = args[1]
    if not isinstance(arr, list):
        raise MinTypeError("filter requires array")
    if interp is None:
        from .interpreter import Interpreter
        interp = Interpreter()
    return [x for x in arr if interp.call_function(func, [x])]


def _reduce(args, interp=None):
    if len(args) < 3:
        raise ArgumentError("reduce expects array, function, and initial value")
    arr = args[0]
    func = args[1]
    acc = args[2]
    if not isinstance(arr, list):
        raise MinTypeError("reduce requires array")
    if interp is None:
        from .interpreter import Interpreter
        interp = Interpreter()
    for x in arr:
        acc = interp.call_function(func, [acc, x])
    return acc


def _read_file(args):
    if len(args) != 1:
        raise ArgumentError("read_file expects 1 argument (filepath)")
    filepath = str(args[0])
    if not os.path.exists(filepath):
        raise MinRuntimeError(f"File not found: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def _write_file(args):
    if len(args) != 2:
        raise ArgumentError("write_file expects 2 arguments (filepath, content)")
    filepath = str(args[0])
    content = str(args[1])
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return True


def _append_file(args):
    if len(args) != 2:
        raise ArgumentError("append_file expects 2 arguments (filepath, content)")
    filepath = str(args[0])
    content = str(args[1])
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(content)
    return True


def _file_exists(args):
    if len(args) != 1:
        raise ArgumentError("file_exists expects 1 argument (filepath)")
    return os.path.exists(str(args[0]))


def _delete_file(args):
    if len(args) != 1:
        raise ArgumentError("delete_file expects 1 argument (filepath)")
    filepath = str(args[0])
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False


def _getenv(args):
    if len(args) < 1 or len(args) > 2:
        raise ArgumentError("getenv expects 1 or 2 arguments (var_name, [default])")
    default_val = str(args[1]) if len(args) == 2 else ""
    return os.environ.get(str(args[0]), default_val)


def _time(args):
    return time.time()


def _clock(args):
    return time.perf_counter()


def _error(args):
    if len(args) != 1:
        raise ArgumentError("error expects 1 argument")
    raise MinTypeError(str(args[0]))


def _thread(args, interp=None):
    if len(args) < 1:
        raise ArgumentError("thread expects a function argument")
    func = args[0]
    func_args = args[1:] if len(args) > 1 else []
    if interp is None:
        from .interpreter import Interpreter
        interp = Interpreter()
    
    import threading
    t = threading.Thread(target=interp.call_function, args=(func, func_args), daemon=True)
    t.start()
    return t


# ─── Register all builtins ────────────────────────────────────

BUILTINS = {
    'len': _len,
    'type': _type,
    'str': _str,
    'num': _num,
    'int': _int,
    'abs': _abs,
    'sqrt': _sqrt,
    'pow': _pow,
    'floor': _floor,
    'ceil': _ceil,
    'round': _round,
    'random': _random,
    'randint': _randint,
    'min': _min_val,
    'max': _max_val,
    'range': _range_val,
    'push': _push,
    'pop': _pop,
    'slice': _slice,
    'keys': _keys,
    'values': _values,
    'has': _has,
    'join': _join,
    'split': _split,
    'replace': _replace,
    'upper': _upper,
    'lower': _lower,
    'trim': _trim,
    'contains': _contains,
    'reverse': _reverse,
    'sort': _sort,
    'map': _map,
    'filter': _filter,
    'reduce': _reduce,
    'read_file': _read_file,
    'write_file': _write_file,
    'append_file': _append_file,
    'file_exists': _file_exists,
    'delete_file': _delete_file,
    'getenv': _getenv,
    'time': _time,
    'clock': _clock,
    'error': _error,
    'thread': _thread,
}


STD_MODULES = {
    'std/math': {
        'abs': _abs,
        'sqrt': _sqrt,
        'pow': _pow,
        'floor': _floor,
        'ceil': _ceil,
        'round': _round,
        'random': _random,
        'randint': _randint,
        'min': _min_val,
        'max': _max_val,
        'range': _range_val,
    },
    'std/io': {
        'read_file': _read_file,
        'write_file': _write_file,
        'append_file': _append_file,
        'file_exists': _file_exists,
        'delete_file': _delete_file,
    },
    'std/string': {
        'upper': _upper,
        'lower': _lower,
        'trim': _trim,
        'split': _split,
        'join': _join,
        'replace': _replace,
        'reverse': _reverse,
        'contains': _contains,
        'len': _len,
        'str': _str,
    },
    'std/array': {
        'push': _push,
        'pop': _pop,
        'slice': _slice,
        'sort': _sort,
        'reverse': _reverse,
        'contains': _contains,
        'map': _map,
        'filter': _filter,
        'reduce': _reduce,
        'len': _len,
        'join': _join,
    },
}
