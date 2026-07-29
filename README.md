<<<<<<< HEAD
# min_AIL
Min is a minimal language made for AI by AI
=======
# Min Language Specification

**Version:** 0.1.0
**Type:** Interpreted, general-purpose, AI-optimized
**Implementation:** Tree-walking interpreter (Python)

---

## Table of Contents

1. [Philosophy](#philosophy)
2. [Installation](#installation)
3. [Running](#running)
4. [Lexical Structure](#lexical-structure)
5. [Data Types](#data-types)
6. [Variables](#variables)
7. [Operators](#operators)
8. [Control Flow](#control-flow)
9. [Functions](#functions)
10. [Classes & Objects](#classes--objects)
11. [Arrays](#arrays)
12. [Objects (Maps)](#objects-maps)
13. [Strings](#strings)
14. [Built-in Functions](#built-in-functions)
15. [Error Handling](#error-handling)
16. [Modules](#modules)
17. [Scoping Rules](#scoping-rules)
18. [Operator Precedence](#operator-precedence)
19. [Examples](#examples)
20. [Grammar](#grammar)
21. [Architecture](#architecture)
22. [Limitations](#limitations)

---

## Philosophy

Min is designed around three core principles:

1. **Token Efficiency** — Every character must earn its place. No boilerplate, no unnecessary keywords.
2. **Prefix Notation** — Operators precede operands (`+ 3 4` not `3 + 4`). This eliminates ambiguity and reduces parsing complexity.
3. **AI Readability** — The syntax is structured for machine parsing. Cryptic by human standards, optimal for tokenizers.

### Comparison to Traditional Languages

| Operation | Python | JavaScript | Min |
|-----------|--------|------------|-----|
| Variable | `x = 5` | `let x = 5` | `:x 5` |
| Function | `def add(a,b): return a+b` | `const add=(a,b)=>a+b` | `@add(a b) [+ a b]` |
| If/else | `if x > 5: ... else: ...` | `if(x>5){...}else{...}` | `? (> x 5) [...] !else [...]` |
| While | `while i < 10:` | `while(i<10){}` | `!while [< i 10] [...]` |
| For | `for i in range(10):` | `for(let i=0;i<10;i++){}` | `!for [i 0 10] [...]` |
| Class | `class Dog:` | `class Dog{}` | `!class Dog [...]` |
| Array | `[1,2,3]` | `[1,2,3]` | `[1:2:3]` |
| Object | `{"a":1}` | `{a:1}` | `{a:1}` |
| Print | `print("hi")` | `console.log("hi")` | `!print "hi"` |

---

## Installation

Min requires Python 3.10+ (for `match` statements in type hints).

```bash
# Clone or copy the min/ directory
cd min/

# No external dependencies required
```

### File Structure

```
min/
  __init__.py        # Package entry point, run() function
  __main__.py        # CLI entry: REPL and file runner
  tokens.py          # Token type enum and Token dataclass
  errors.py          # Error class hierarchy
  lexer.py           # Tokenizer: source → tokens
  ast_nodes.py       # AST node dataclass definitions
  parser.py          # Recursive descent parser: tokens → AST
  interpreter.py     # Tree-walking interpreter: AST → execution
  builtins.py        # 30+ built-in functions
  README.md          # This documentation
  tests/
    test_simple.min  # Comprehensive feature test
    test_all.min     # Extended test suite
    test_errors.py   # Unit test suite for error diagnostics & call stack traces
    examples/
      fibonacci.min  # Recursive fibonacci
      classes.min    # Class inheritance demo
      todo.min       # Todo list with OOP
      utils.min      # Math utility module
```

---

## Running

### REPL Mode

Launch the interactive REPL shell:

```bash
python -m min
```

Output:
```text
Min v0.1.0 Interactive REPL
Type !help for syntax reference, !vars for session state, !exit to quit

min>
```

#### REPL Features:
- **Persistent State**: Variables, functions, and classes defined in previous inputs are retained across the session.
- **Multi-Line Input**: Typing an unclosed block (`[`, `{`, `(`) automatically switches the prompt to `... ` until all brackets are balanced.
- **Tab Autocompletion**: Autocompletes keywords, built-in functions, and user-defined session variables.
- **ANSI Color Output**: Colorful prompts, formatted results, and red diagnostic error tracebacks.

#### REPL Meta-Commands:
- `!vars`: List all user-defined variables and functions in the active session.
- `!help`: Display the syntax reference cheatsheet.
- `!clear`: Clear current REPL session environment.
- `!exit` or `!quit`: Exit the REPL.

### File Mode

```bash
python -m min program.min
```

### Programmatic Usage

```python
from min import run

# Execute source code
run(':x 42')
run('!print "Hello"')

# Or use the components individually
from min.lexer import tokenize
from min.parser import parse
from min.interpreter import Interpreter

tokens = tokenize(':x 42')
ast = parse(tokens)
interp = Interpreter()
interp.run(ast)
```

---

## Lexical Structure

### Comments

```
# This is a comment (rest of line)
x:42  # Inline comment
```

Comments start with `#` and extend to end of line. The one exception: `#true`, `#false`, `#null` are NOT comments — they are boolean/null literals.

### Whitespace

- Spaces and tabs are ignored (used as token separators)
- Newlines are significant — they separate statements
- `(`, `[`, `{` can appear after newlines without issues

### Identifiers

```
valid:   x, _name, counter1, myList
invalid: 1x, my-name, @var
```

Identifiers start with a letter or underscore, followed by letters, digits, or underscores.

### Escape Sequences in Strings

| Sequence | Meaning |
|----------|---------|
| `\n` | Newline |
| `\t` | Tab |
| `\\` | Backslash |
| `\"` | Double quote |

---

## Data Types

Min has 6 core data types:

### 1. Integer

```
:age 25
:max_val 999999
:negative -42
```

Whole numbers. Stored as Python `int`.

### 2. Float

```
:pi 3.14159
:ratio 0.5
:temp -12.5
```

Decimal numbers. Stored as Python `float`.

### 3. String

```
:name "John"
:greeting "Hello, World!"
:empty ""
:multiline "line1\nline2"
```

Double-quoted. No single-quote strings. Escape sequences supported.

### 4. Boolean

```
:flag #true
:done #false
```

Prefixed with `#`. Only two values: `#true` and `#false`.

### 5. Null

```
:data #null
```

Represents absence of value. Prefixed with `#`.

### 6. Array

```
:nums [1:2:3:4:5]
:mixed [1:"hello":#true]
:empty []
```

Ordered collection. Elements separated by `:`. Zero-indexed.

### 7. Object (Map)

```
:user {name:"John" age:30 active:#true}
:empty {}
```

Key-value pairs. Keys are identifiers. Values can be any type.

### Type Checking

```
!type 42        # "int"
!type 3.14      # "float"
!type "hello"   # "string"
!type #true     # "bool"
!type #null     # "null"
!type [1:2:3]   # "array"
!type {a:1}     # "object"
```

---

## Variables

### Declaration & Assignment

```
:x 42              # declare x = 42
:name "John"       # declare name = "John"
:x 100             # reassign x = 100
```

The `:` operator declares or reassigns a variable. If the variable exists, it updates. If not, it creates.

### Dot Assignment

```
:user {name:"John"}
: user name "Jane"     # update field
: user age 31          # add field
```

### Index Assignment

```
:arr [1:2:3]
: arr 0 99           # set index 0 to 99
```

### Scope

Variables declared in a block `[...]` are local to that block:

```
:x 10
? #true [
  :x 20    # local x, doesn't affect outer x
]
!print x   # prints 10
```

---

## Operators

### Arithmetic (Prefix)

```
+ 3 4         # 7 (addition)
- 10 3        # 7 (subtraction)
* 5 6         # 30 (multiplication)
/ 20 4        # 5.0 (division, always float)
% 17 5        # 2 (modulo)
- 5           # -5 (unary negation)
```

### String Concatenation

```
+ "Hello" " World"    # "Hello World"
+ "Count: " 42        # "Count: 42" (auto-convert)
```

When `+` has a string operand, the other operand is auto-converted to string.

### Comparison

```
= 5 5         # true (equal)
!= 5 3        # true (not equal)
> 10 5        # true (greater than)
< 3 7         # true (less than)
>= 5 5        # true (greater or equal)
<= 3 7        # true (less or equal)
```

### Logical

```
& #true #false    # false (logical AND)
| #true #false    # true (logical OR)
! #true           # false (logical NOT)
```

### Operator Precedence

All binary operators have **equal precedence** and are evaluated **left to right**. Use parentheses for grouping:

```
+ 2 3         # 5
* 2 + 1 1     # 4, because (* 2 (+ 1 1)) = (* 2 2)
(+ 2 3)       # 5 (explicit grouping)
```

### Prefix Notation Rules

- Binary operators: `OP LEFT RIGHT`
- Unary operators: `OP OPERAND`
- Grouped expressions: `(EXPRESSION)`

```
+ 3 4                    # 3 + 4
* (+ 1 2) (+ 3 4)       # (1+2) * (3+4) = 21
(!= (+ 1 1) 2)           # (1+1) == 2 = true
```

---

## Control Flow

### If/Else

```
? (> x 5) [
  !print "x is big"
]
```

With else:

```
? (> x 5) [
  !print "big"
] !else [
  !print "small"
]
```

- `?` introduces the condition
- First `[...]` is the then-branch
- `!else` introduces the else-branch
- Second `[...]` is the else-body
- Else-branch is optional

### While Loop

```
:i 0
!while [< i 10] [
  !print i
  :i (+ i 1)
]
```

- `!while` introduces the loop
- Condition is evaluated before each iteration
- Body repeats while condition is truthy
- Supports `!break` and `!continue`

### For Loop

```
!for [i 0 10] [
  !print i
]
```

- `!for` introduces the loop
- `[VAR START END]` defines the loop variable and range
- `START` is inclusive, `END` is exclusive
- `VAR` starts at `START`, increments by 1, stops before `END`
- Supports `!break` and `!continue`

### Break & Continue

```
!for [i 0 100] [
  ? (= i 5) [!break]
  ? (= (% i 2) 0) [!continue]
  !print i
]
```

- `!break` exits the innermost loop
### Pattern Matching (`!match`)

```min
:val 2
:result !match (val) [
  1 ["one"]
  2 ["two"]
  3 ["three"]
  !else ["unknown"]
]
!print result         # "two"
```

- `!match (expr) [ pattern [body] ... !else [default_body] ]` evaluates expression against case patterns.
- Returns the result of the matching branch block.

### Return

```
@abs(n) [
  ? (< n 0) [~(- 0 n)]
    !else [~n]
]
```

- `!return EXPR` or `~EXPR` returns a value from a function
- `!return` without a value returns `#null`
- Only meaningful inside function bodies

---

## Functions

### Definition

```
@add(a b) [+ a b]
```

- `@` marks a function definition
- Parameters are space-separated inside `()`
- Body is a `[...]` block
- The last expression in the body is the return value
- Use `!return` or `~` for early return

### Multi-line Body

```
@factorial(n) [
  ? (= n 0) [~1]
    !else [~(* n (@factorial((- n 1))))]
]
```

### Anonymous Functions (Lambdas)

```min
# Inline lambda passed directly to @map
:doubled (@map [1:2:3:4]: @(x) [* x 2])
!print doubled        # [2:4:6:8]

# Inline lambda with closure variable
:factor 10
:scaled (@map [1:2:3]: @(x) [* x factor])
!print scaled         # [10:20:30]
```

- `@(params) [body]` creates an inline anonymous function.
- Can capture variables from outer lexical scopes.

### Recursive Functions

```
@fib(n) [
  ? (< n 2) [~n]
    !else [~(+ (@fib((- n 1))) (@fib((- n 2))))]
]
```

Functions can call themselves. Each call creates a new scope.

### First-Class Functions

Functions are values that can be passed around:

```
@apply(f x) [@f(x)]

@double(n) [* n 2]

!print (@apply(@double:5))   # 10
```

### Method Call Syntax

```
! obj method args
```

The `!` prefix with an identifier calls a method on an object:

```
!class Dog
  name:""
  @init(n) [:name n]
  @bark() [!print (+ name " says Woof!")]

:dog (!new Dog("Rex"))
! dog bark        # "Rex says Woof!"
```

Methods automatically receive `self` and `this` as references to the instance.

---

## Classes & Objects

### Class Definition

```
!class Dog
  name:""
  age:0

  @init(n a) [
    :name n
    :age a
  ]

  @bark() [
    !print (+ name " says Woof!")
  ]

  @getAge() [~age]
```

- `!class` introduces a class
- Fields are declared as `fieldname:default_value`
- `@init` is the constructor (special method name)
- Other `@` definitions are methods
- Class body ends with `]`

### Creating Instances

```
:dog (!new Dog("Rex":3))
```

- `!new ClassName(args)` creates a new instance
- Arguments passed to `!new` are forwarded to `@init`
- `self` and `this` are available inside methods

### Accessing Fields & Methods

```
! dog bark           # method call
! dog getAge         # method with no args
(. dog name)         # field access
```

### Field Assignment

Inside methods, field assignments update the instance:

```
@setName(n) [
  :name n     # updates self.name
]
```

Outside methods, use dot assignment:

```
: dog name "Buddy"
```

### Inheritance

```
!class Animal
  name:""
  @init(n) [:name n]
  @speak() [!print "..." ]

!class Dog !extends Animal
  @init(n) [(!super init(n))]
  @bark() [!print (+ name " says Woof!")]
```

- `!extends ParentClass` inherits from a parent class
- Child inherits all fields and methods from parent
- Child can override methods
- Child fields override parent fields with same name

### Instance Checking

```
:dog (!new Dog("Rex"))
! type dog    # returns the class name as string
```

---

## Arrays

### Creation

```
:nums [1:2:3:4:5]
:mixed [1:"hello":#true:3.14]
:empty []
```

Elements separated by `:`. Can mix types.

### Access

```
:arr [10:20:30]
(. arr 0)       # 10
(. arr 2)       # 30
```

Index access uses prefix `.` syntax: `(. array index)`.

### Length

```
:arr [1:2:3]
! len arr       # 3
(. arr length)  # 3 (special .length property)
```

### Modification

```
:arr [1:2:3]
! arr push 4         # arr is now [1:2:3:4]
! arr push 5:6       # push multiple
! arr pop            # removes last, returns 3
: arr 0 99           # set index 0 to 99
```

### Slicing

```
:arr [1:2:3:4:5]
! slice arr 1 4      # [2:3:4]
! slice arr 2        # [3:4:5]
```

### Sorting & Reversing

```
:arr [3:1:4:1:5]
! sort arr           # [1:1:3:4:5]
! reverse arr        # [5:1:4:1:3]
```

### Higher-Order Functions

```
:arr [1:2:3:4:5]

# Map: transform each element
! map arr (@inc(n) [+ n 1])        # [2:3:4:5:6]

# Filter: keep elements matching predicate
! filter arr (@big(n) [> n 3])     # [4:5]

# Reduce: accumulate to single value
! reduce arr (@sum(a b) [+ a b]) 0  # 15
```

---

## Objects (Maps)

### Creation

```
:user {name:"John" age:30 active:#true}
:empty {}
```

### Access

```
:user {name:"John" age:30}
(. user name)       # "John"
(. user age)        # 30
```

### Modification

```
:user {name:"John"}
: user age 30           # add field
: user name "Jane"      # update field
```

### Checking Keys

```
:user {name:"John"}
! has user "name"       # true
! has user "email"      # false
```

### Getting Keys & Values

```
:user {name:"John" age:30}
! keys user     # ["name":"age"]
! values user   # ["John":30]
```

---

## Strings

### Concatenation

```
+ "Hello" " World"          # "Hello World"
+ "Count: " 42              # "Count: 42"
+ "Pi is " 3.14             # "Pi is 3.14"
```

The `+` operator auto-converts non-string operands to strings.

### Length

```
! len "hello"       # 5
```

### Case Conversion

```
! upper "hello"     # "HELLO"
! lower "HELLO"     # "hello"
```

### Trimming

```
! trim "  hello  "  # "hello"
```

### Slicing

```
! slice "hello" 1 3     # "el"
! slice "hello" 2       # "llo"
```

### Splitting & Joining

```
! split "a:b:c" ":"     # ["a":"b":"c"]
! join ":" ["a":"b":"c"] # "a:b:c"
```

### Replacing

```
! replace "hello world" "world" "Min"  # "hello Min"
```

### Containment

```
! contains "hello" "ell"    # true
! contains "hello" "xyz"    # false
```

### Reversing

```
! reverse "hello"   # "olleh"
```

---

## Built-in Functions

### I/O

| Function | Syntax | Description | Returns |
|----------|--------|-------------|---------|
| `!print` | `!print expr...` | Print values to stdout (space-separated) | `#null` |
| `!input` | `!input "prompt"` | Read line from stdin | `string` |

```
!print "Hello" "World"    # prints: Hello World
:name !input "Enter name: "
```

### Type Conversion

| Function | Syntax | Description | Returns |
|----------|--------|-------------|---------|
| `!str` | `!str value` | Convert to string | `string` |
| `!num` | `!num value` | Convert to float | `float` |
| `!int` | `!int value` | Convert to integer | `int` |
| `!type` | `!type value` | Get type name | `string` |

```
! str 42         # "42"
! str 3.14       # "3.14"
! num "3.14"     # 3.14
! int 3.9        # 3
! type 42        # "int"
```

### Math

| Function | Syntax | Description | Returns |
|----------|--------|-------------|---------|
| `!abs` | `!abs n` | Absolute value | `number` |
| `!sqrt` | `!sqrt n` | Square root | `float` |
| `!pow` | `!pow base exp` | Power / Exponentiation | `float` |
| `!floor` | `!floor n` | Round down | `int` |
| `!ceil` | `!ceil n` | Round up | `int` |
| `!round` | `!round n [digits]` | Round number | `number` |
| `!random` | `!random` | Random float in [0, 1) | `float` |
| `!randint` | `!randint min max` | Random int in [min, max] | `int` |
| `!min` | `!min a b` or `!min [arr]` | Minimum value | `number` |
| `!max` | `!max a b` or `!max [arr]` | Maximum value | `number` |
| `!range` | `!range n` or `!range start end` or `!range start end step` | Generate range | `array` |

```
! abs -5          # 5
! sqrt 16         # 4.0
! pow 2 3         # 8.0
! floor 3.9       # 3
! ceil 3.1        # 4
! round 3.567 2   # 3.57
! min 3 7         # 3
! max [1:5:3]     # 5
! range 5         # [0:1:2:3:4]
```

### File I/O & Environment

| Function | Syntax | Description | Returns |
|----------|--------|-------------|---------|
| `!read_file` | `!read_file path` | Read text file contents | `string` |
| `!write_file` | `!write_file path content` | Write text to file (overwrite) | `bool` |
| `!append_file` | `!append_file path content` | Append text to file | `bool` |
| `!file_exists` | `!file_exists path` | Check if file exists | `bool` |
| `!delete_file` | `!delete_file path` | Remove file | `bool` |
| `!getenv` | `!getenv var [default]` | Get environment variable | `string` |

### Array Operations

| Function | Syntax | Description | Returns |
|----------|--------|-------------|---------|
| `!len` | `!len collection` | Length of array/string/object | `int` |
| `!push` | `!push arr val...` | Append values to array | `array` |
| `!pop` | `!pop arr` | Remove and return last element | `any` |
| `!slice` | `!slice obj start [end]` | Extract substring/subarray | `array/string` |
| `!sort` | `!sort arr` | Return sorted copy | `array` |
| `!reverse` | `!reverse arr` | Return reversed copy | `array` |
| `!contains` | `!contains container item` | Check if item exists | `bool` |

```
:arr [3:1:4:1:5]
! len arr          # 5
! push arr 6       # [3:1:4:1:5:6]
! pop arr          # 6, arr is now [3:1:4:1:5]
! sort arr         # [1:1:3:4:5]
! contains arr 4   # true
```

### Object Operations

| Function | Syntax | Description | Returns |
|----------|--------|-------------|---------|
| `!keys` | `!keys obj` | Get all keys | `array` |
| `!values` | `!values obj` | Get all values | `array` |
| `!has` | `!has obj key` | Check if key exists | `bool` |

```
:user {name:"John" age:30}
! keys user       # ["name":"age"]
! values user     # ["John":30]
! has user "name" # true
```

### Higher-Order Functions

| Function | Syntax | Description | Returns |
|----------|--------|-------------|---------|
| `!map` | `!map arr func` | Apply function to each element | `array` |
| `!filter` | `!filter arr func` | Keep elements where func returns truthy | `array` |
| `!reduce` | `!reduce arr func init` | Reduce array to single value | `any` |

```
:arr [1:2:3:4:5]
! map arr (@double(n) [* n 2])          # [2:4:6:8:10]
! filter arr (@even(n) [= (% n 2) 0])   # [2:4]
! reduce arr (@add(a b) [+ a b]) 0      # 15
```

### String Operations

| Function | Syntax | Description | Returns |
|----------|--------|-------------|---------|
| `!upper` | `!upper str` | Uppercase | `string` |
| `!lower` | `!lower str` | Lowercase | `string` |
| `!trim` | `!trim str` | Strip whitespace | `string` |
| `!split` | `!split str sep` | Split by separator | `array` |
| `!join` | `!join sep arr` | Join with separator | `string` |
| `!replace` | `!replace str old new` | Replace substring | `string` |
| `!reverse` | `!reverse str` | Reverse string | `string` |

### Utility

| Function | Syntax | Description | Returns |
|----------|--------|-------------|---------|
| `!time` | `!time` | Unix timestamp | `float` |
| `!clock` | `!clock` | Process time (seconds) | `float` |
| `!error` | `!error msg` | Throw a runtime error | never returns |

---

## Error Handling

### Try/Catch

```
!try [
  :result (/ 10 0)
] !catch (e) [
  !print "Error:" e
]
```

- `!try [...]` wraps code that might fail
- `!catch (var) [...]` catches errors, `var` holds the error message
- Only catches `MinRuntimeError` and subclasses
- Other Python exceptions propagate up

### Throwing Errors

```
@divide(a b) [
  ? (= b 0) [!throw "Division by zero"]
    !else [~(/ a b)]
]
```

### Error Types

| Error | When | Example |
|-------|------|---------|
| `SyntaxError` | Invalid syntax | `+ 3` (missing operand) |
| `RuntimeError` | Runtime failure | `!throw "msg"` |
| `TypeError` | Wrong type | `+ "a" #true` |
| `NameError` | Undefined variable | `!print x` (x not defined) |
| `IndexError` | Index out of bounds | `(. [1:2] 5)` |
| `ArgumentError` | Wrong arg count | `@f(a) [...]` called as `@f(1:2)` |
| `AttributeError` | Invalid field access | `(. 42 name)` |
| `ImportError` | Module not found | `!import "missing"` |

### Error Format

Errors provide rich diagnostic output, including multi-frame call stack tracebacks, source code line snippets, and column caret pointers (`^`):

```text
Traceback (most recent call last):
  File "main.min", line 7, in @outer
  File "main.min", line 5, in @deep_fail
Line 2:3 RuntimeError: Division by zero
  2 |   / x 0
        ^
```

All AST nodes preserve line and column metadata, allowing both syntax errors and runtime failures to pinpoint exact source locations.

---

## Modules

### Standard Library Virtual Modules

Min includes built-in virtual standard library modules that can be imported directly without local `.min` files:

```min
!import "std/math" !as math
!import "std/io" !as io
!import "std/string" !as str
!import "std/array" !as arr

!print (! math sqrt 16)               # 4.0
!print (! str upper "hello min")       # HELLO MIN
!print (! arr slice [1:2:3:4:5] 1 4)  # [2:3:4]
```

### Relative Imports & Resolution

```min
!import "utils"
!import "utils.min"
!import "math/utils" !as mu
```

- Imports resolve relative to the directory of the file issuing the `!import` statement.
- `!as alias` creates a custom namespace alias.
- Imported module functions are accessed via module commands: `! module func args...` or dot property access `(. module func)`.

### Exporting

```min
# utils.min
:secret_key "12345"
@add(a b) [+ a b]

!export add
```

- If a module contains `!export name` statements, **only** explicitly exported names are exposed to importers.
- Without `!export`, all top-level non-underscore names are exported by default.

### Module Caching

Modules are cached by normalized path after the first import. Importing the same module multiple times returns the cached version.

---

## Scoping Rules

### Lexical Scoping

Min uses lexical (static) scoping. Variables are resolved in the scope they were defined, not called:

```
:x 10
@getX() [~x]
@make() [
  :x 20
  ~@getX
]
!print (@getX)      # 10 (global x)
!print (@make())    # 10 (still global x, not local)
```

### Scope Chain

```
Global scope
  └─ Block scope
       └─ Function scope
            └─ Method scope
```

Each scope has a reference to its parent. Variable lookup traverses up the chain.

### Variable Resolution Order

1. Current scope
2. Parent scope
3. ... up to global scope

### Shadowing

Inner scopes can shadow outer variables:

```
:x 10
? #true [
  :x 20        # shadows outer x
  !print x     # prints 20
]
!print x       # prints 10
```

### Instance Fields in Methods

Inside methods, instance fields are accessible directly:

```
!class Dog
  name:""
  @init(n) [:name n]
  @bark() [!print name]

:dog (!new Dog("Rex"))
! dog bark     # prints "Rex"
```

Methods have access to:
- `self` — the instance
- `this` — alias for self
- All instance fields by name
- Method parameters
- Outer scope variables

---

## Operator Precedence

All operators in Min have **equal precedence** and are evaluated **left-to-right**. This is intentional — it simplifies parsing and makes evaluation order predictable.

```
+ 2 3 4        # ((2+3)+4) = 9, NOT 2+(3+4)
* 2 + 1 1      # (2*(1+1)) = 4, NOT (2*1)+1
```

To override default left-to-right evaluation, use parentheses:

```
(+ 2 (* 3 4))  # 2 + (3*4) = 14
```

### Why Equal Precedence?

Traditional languages have complex precedence tables (PEMDAS). This creates subtle bugs and makes parsing harder. Min's equal precedence means:
- No surprises about evaluation order
- Simpler parser (no precedence climbing)
- Predictable behavior
- Parentheses make intent explicit

---

## Examples

### Hello World

```
!print "Hello, World!"
```

### Fibonacci

```
@fib(n) [
  ? (< n 2) [~n]
    !else [~(+ (@fib((- n 1))) (@fib((- n 2))))]
]

!for [i 0 15] [
  !print (@fib(i))
]
```

### Factorial

```
@factorial(n) [
  ? (= n 0) [~1]
    !else [~(* n (@factorial((- n 1))))]
]

!print (@factorial(10))   # 3628800
```

### Bubble Sort

```
@bubbleSort(arr) [
  :n (! len arr)
  !for [i 0 n] [
    !for [j 0 (- n (- i 1))] [
      ? (> (. arr j) (. arr (+ j 1))) [
        :temp (. arr j)
        : arr j (. arr (+ j 1))
        : arr (+ j 1) temp
      ]
    ]
  ]
  ~arr
]

:nums [64:34:25:12:22:11:90]
!print (@bubbleSort(nums))
```

### Todo List (OOP)

```
!class Todo
  text:""
  done:#false

  @init(t) [:text t]
  @toggle() [:done (! not done)]
  @toString() [~(+ "[ " (? done "x" " ") " ] " text)]

!class TodoList
  items:[]

  @init() [:items []]
  @add(t) [(! items push (!new Todo(t)))]
  @print() [
    !for [i 0 (! len items)] [
      !print (! (. items i) toString)
    ]
  ]

:todos (!new TodoList)
(! todos add "Learn Min")
(! todos add "Build something")
(! todos print)
```

### FizzBuzz

```
!for [i 1 101] [
  :result ""
  ? (= (% i 3) 0) [:result (+ result "Fizz")]
  ? (= (% i 5) 0) [:result (+ result "Buzz")]
  ? (= result "") [:result (! str i)]
  !print result
]
```

### Matrix Multiply

```
@matMul(a b) [
  :rowsA (! len a)
  :colsB (! len (. b 0))
  :result []
  !for [i 0 rowsA] [
    :row []
    !for [j 0 colsB] [
      :sum 0
      !for [k 0 (! len (. a 0))] [
        :sum (+ sum (* (. (. a i) k) (. (. b k) j)))
      ]
      ! row push sum
    ]
    ! result push row
  ]
  ~result
]
```

---

## Grammar

### EBNF Grammar

```
program         = statement*

statement       = block
                | assignment
                | dot_assignment
                | command
                | keyword_command
                | if_statement
                | function_def
                | return_stmt
                | expression

block           = '[' statement* ']'

assignment      = ':' identifier expression
dot_assignment  = '.' expression identifier expression

command         = '!' (method_call | keyword_command)
method_call     = expression identifier expression*

keyword_command = print_stmt | input_stmt | while_stmt | for_stmt
                | break_stmt | continue_stmt | return_keyword
                | import_stmt | export_stmt | try_stmt
                | throw_stmt | class_stmt | new_stmt

print_stmt      = 'print' expression*
input_stmt      = 'input' expression?
while_stmt      = 'while' expression block
for_stmt        = 'for' '[' identifier expression expression ']' block
break_stmt      = 'break'
continue_stmt   = 'continue'
return_keyword  = 'return' expression?
import_stmt     = 'import' string ('as' identifier)?
export_stmt     = 'export' identifier
try_stmt        = 'try' block 'catch' '(' identifier ')' block
throw_stmt      = 'throw' expression
class_stmt      = 'class' identifier ('extends' identifier)? class_body
new_stmt        = 'new' identifier '(' (expression (':' expression)*)? ')'

class_body      = '{' (field_def | function_def)* '}'
field_def       = identifier ':' expression

function_def    = '@' identifier '(' (identifier*) ')' (block | expression)
if_statement    = '?' expression block ('else' block)?

expression      = number | string | boolean | null
                | array | object | dot_access | identifier
                | function_call | grouped_expr
                | binary_op | unary_op | new_expr

array           = '[' (expression (':' expression)*)? ']'
object          = '{' (identifier ':' expression)* '}'

dot_access      = '.' expression (identifier | expression)
index_access    = identifier '[' expression ']'

function_call   = '@' identifier '(' (expression (':' expression)*)? ')'
grouped_expr    = '(' expression ')'

binary_op       = ('+' | '-' | '*' | '/' | '%' | '=' | '!=' | '>' | '<'
                  | '>=' | '<=' | '&' | '|') expression expression
unary_op        = ('!' | '-') expression

new_expr        = 'new' identifier '(' (expression (':' expression)*)? ')'

number          = digit+ ('.' digit+)?
string          = '"' chars '"'
boolean         = '#true' | '#false'
null            = '#null'
identifier      = letter (letter | digit | '_')*
```

### Token Table

| Token | Literal | Type | Usage |
|-------|---------|------|-------|
| Number | `42`, `3.14` | `NUM` | Numeric literal |
| String | `"hello"` | `STR` | String literal |
| Boolean | `#true`, `#false` | `BOOL` | Boolean literal |
| Null | `#null` | `NULL` | Null literal |
| Identifier | `x`, `name` | `IDENT` | Variable/function name |
| `@` | `@` | `AT` | Function definition/call |
| `:` | `:` | `COLON` | Assignment, array separator |
| `.` | `.` | `DOT` | Dot access, index access |
| `(` | `(` | `LPAREN` | Grouping, function args |
| `)` | `)` | `RPAREN` | End grouping |
| `[` | `[` | `LBRACKET` | Array, block start |
| `]` | `]` | `RBRACKET` | Array, block end |
| `{` | `{` | `LBRACE` | Object start |
| `}` | `}` | `RBRACE` | Object end |
| `+` | `+` | `PLUS` | Addition, concatenation |
| `-` | `-` | `MINUS` | Subtraction, unary negation |
| `*` | `*` | `STAR` | Multiplication |
| `/` | `/` | `SLASH` | Division |
| `%` | `%` | `PERCENT` | Modulo |
| `=` | `=` | `EQ` | Equality comparison |
| `!=` | `!=` | `NEQ` | Inequality comparison |
| `>` | `>` | `GT` | Greater than |
| `<` | `<` | `LT` | Less than |
| `>=` | `>=` | `GTE` | Greater or equal |
| `<=` | `<=` | `LTE` | Less or equal |
| `&` | `&` | `AND` | Logical AND |
| `\|` | `\|` | `OR` | Logical OR |
| `!` | `!` | `BANG` | Command prefix, logical NOT |
| `?` | `?` | `QUESTION` | If condition |
| `~` | `~` | `TILDE` | Return shorthand |
| `\n` | newline | `NEWLINE` | Statement separator |
| EOF | end of file | `EOF` | End of input |

---

## Architecture

### Compilation Pipeline

```
Source Code (string)
       │
       ▼
   ┌────────┐
   │ Lexer  │  Tokenizer: source → tokens
   └────────┘
       │
       ▼
   Tokens [Token, Token, ...]
       │
       ▼
   ┌────────┐
   │ Parser │  Recursive descent: tokens → AST
   └────────┘
       │
       ▼
   AST (Program node)
       │
       ▼
   ┌───────────────┐
   │ Interpreter   │  Tree-walking: AST → execution
   └───────────────┘
       │
       ▼
   Output (stdout, return values)
```

### Key Classes

| Class | File | Purpose |
|-------|------|---------|
| `Token` | `tokens.py` | Single token with type, value, line, col |
| `Lexer` | `lexer.py` | Converts source to token stream |
| `Parser` | `parser.py` | Converts tokens to AST |
| `Interpreter` | `interpreter.py` | Executes AST nodes |
| `Environment` | `interpreter.py` | Variable scope (linked list) |
| `MinInstance` | `interpreter.py` | Class instance with fields/methods |
| `BoundMethod` | `interpreter.py` | Method bound to an instance |

### AST Nodes

| Node | Type | Fields |
|------|------|--------|
| `Number` | Literal | `value: int\|float` |
| `String` | Literal | `value: str` |
| `Boolean` | Literal | `value: bool` |
| `Null` | Literal | — |
| `Array` | Literal | `elements: list[Node]` |
| `Object` | Literal | `pairs: dict[str, Node]` |
| `Identifier` | Expression | `name: str` |
| `BinaryOp` | Expression | `op, left, right` |
| `UnaryOp` | Expression | `op, operand` |
| `Assignment` | Expression | `name: Node, value: Node` |
| `DotAccess` | Expression | `object: Node, member: str` |
| `IndexAccess` | Expression | `object: Node, index: Node` |
| `FunctionCall` | Expression | `callee: Node, args: list[Node]` |
| `If` | Statement | `condition, then_body, else_body` |
| `While` | Statement | `condition, body` |
| `For` | Statement | `var, start, end, body` |
| `Break` | Statement | — |
| `Continue` | Statement | — |
| `Return` | Statement | `value: Node?` |
| `FunctionDef` | Statement | `name, params, body` |
| `ClassDef` | Statement | `name, super_class, fields, methods, init_method` |
| `ObjectInit` | Expression | `class_name, args` |
| `Print` | Statement | `args: list[Node]` |
| `Input` | Expression | `prompt: Node?` |
| `Import` | Statement | `module, alias` |
| `Export` | Statement | `name` |
| `TryCatch` | Statement | `try_body, catch_var, catch_body` |
| `Throw` | Statement | `message: Node` |
| `Program` | Root | `statements: list[Node]` |

---

## Limitations

### Current (v0.1.0)

1. **No closures** — Functions capture scope at definition time but don't create closures
2. **No coroutines** — No async/await or generators
3. **No threads** — Single-threaded execution only
4. **No introspection** — Limited ability to inspect objects at runtime
5. **No pattern matching** — No switch/match statements
6. **No list comprehensions** — Use `!map`/`!filter` instead
7. **No string interpolation** — Use `+` concatenation
8. **No multiple return values** — Return arrays or objects instead
9. **No optional arguments** — All arguments required
10. **No variadic functions** — Fixed argument count only

### Performance

Min is a tree-walking interpreter. For compute-intensive tasks, it will be significantly slower than compiled languages. It's designed for:
- Rapid prototyping
- AI-generated code execution
- Scripting and automation
- Learning language concepts

### Extending

To add new features:
1. Add token type to `tokens.py`
2. Add lexer rule to `lexer.py`
3. Add AST node to `ast_nodes.py`
4. Add parser rule to `parser.py`
5. Add interpreter handler to `interpreter.py`
6. Add built-in function to `builtins.py` (if applicable)

---

## Repository & License

- **GitHub Repository**: [https://github.com/idahas/min_AIL.git](https://github.com/idahas/min_AIL.git)
- **License**: [MIT License](LICENSE)

```text
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Attributions & Dependencies

Min is implemented from scratch with **zero third-party package dependencies**, running exclusively on the core Python standard library.
- **Python**: (c) Python Software Foundation (PSF License).
>>>>>>> d87ccf5 (Initial commit: Complete Min Language Interpreter)
