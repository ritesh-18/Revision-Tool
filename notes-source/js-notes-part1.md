# JS Topics (Some Things That I Forgot)

<!-- page 1 -->

_Resources: Mozilla Developer Edition (browser) + for developers._

## Introduction to JavaScript

- **Q1)** JS is everywhere.
- **Q2)** JS is a programming language:
  1. Capability to make decisions.
  2. You can smartly do task repetition.
     - Ex: if you want to add 100 `<li>` elements in HTML, doing it manually is possible, but using JS you can use loops.
  3. You can build logic.
- **Q3)** ECMAScript (old name).

### Online workspaces (Google)

- **Project IDX** — a free workspace to write code
- **CodeSandbox**
- **Replit.com**

### Runtime environments

- **Q4)** Runtime environments → Node.js, Bun
  - Node.js → I know
  - Bun → I will learn

## Variables

How to create a variable:

1. `let`
2. `var`
3. `const`

The **Scopes** topic covers all the differences between these three variable types.

```js
let a = 5;
var a = 5;
const a = 5;
```

**Datatypes** — e.g. number, null, object, undefined, string, array, etc.

### Rules for naming variables in JS

- Only alphanumeric characters, `$` and `_` (underscore) are allowed.
- A variable name can't start with a number:
  - `1abc` ✗, `2223abc` ✗, `_abc` ✓, `$abc` ✓, etc.
- Variable names are case sensitive: `money` ≠ `Money`.

<!-- page 2 -->

- You cannot use a keyword as your variable name.

## Lecture 02 — Operators in JS

### Datatypes in JS

1. **Number**
   - `-0` exists in JS.
   - `NaN` → "Not a Number".
2. **String**
3. **Boolean** (`true` / `false`)
4. **Null** (`null`) — it represents no value, intentionally (defined but empty).
   ```js
   let a = null;
   ```
5. **Undefined** (`undefined`) — shows a variable which is declared but never defined.
   ```js
   let a;
   console.log(a); // undefined
   ```
6. **BigInt** — a normal number can store max `(2^53 - 1)` and min `-(2^53 - 1)`.
   - For numbers beyond this range, we use BigInt.
   - To make a BigInt, we append an `n` at the end (BigInt notation):
   ```js
   let bigVal = 1000000000000n;
   ```
7. **Objects** — `{ key: value }` pairs (separated by commas).
   ```js
   let obj1 = { a: 2, b: 4, c: 5 };
   let obj2 = { name: "ritesh", rollno: 24, age: 22 };
   let obj3 = { a: 2 }; // key can be written as a or 'a'
   ```
   - Keys are unique.
8. **Symbol** — skip.

<!-- page 3 -->

Using a programming language we can do computation.

### Operators

Operators are symbols that can do some computation or calculation, e.g. `+`, `-`, `*`, `/`, `%`.

### Arithmetic operators

```js
2 + 3; // 2 and 3 are operands, + is the operator
```

- `/` will return a decimal.
- `%` → modulo
- `2 ** 3` → power calculation (2³)

### Assignment operator

e.g. `=` → `x = 10`

- Helps us to assign values to a variable.

```js
x = x + 5; // right-hand side is evaluated first, then the value is assigned
// or
x += 5; // same as x = x + 5
```

- Other compound assignment operators: `+=`, `-=`, `%=`, `*=`, `**=` (e.g. `x **= 2`).

### Logical operators

AND, OR, NOT → `&&`, `||`, `!` — used for logical computation.

```js
(x == 2) && (y == 4);
((x == 2) && (y == 2)) || (z == 5);

!true;
!(x == 5);
!(x == null); // same as (x != null)
```

- Operands of a logical operator are always booleans; if they are not, they will be converted into booleans.
  - `( … ) && ( … )` → each side treated as a boolean.

<!-- page 4 -->

_Tip: the ECMAScript spec is the best tutorial for JS (or MDN)._

### Truth table for `&&`, `||`, `!`

| A | B |
|---|---|
| T | T |
| F | F |
| T | F |
| F | T |

- `&&` → both should be true → true
- `||` → any one should be true → true
- `!x` → if true → false; if false → true

## Lecture 03 — Short Circuiting & Truthy/Falsy Values

### Short circuiting

Applies to logical operators only.

For `x && y` (AND):

- If `x` is false, then it will never check the `y` operand and it returns the **1st operand**.
- If `x` is true, then it returns the **2nd operand**.

```js
(x == 4) && (y == 5);
// if (x == 4) is true  → returns (y == 5)
// if (x == 4) is false → returns (x == 4)
```

### `ToBoolean()`

It converts its argument to a value of type Boolean.

`ToBoolean(args)`:

- `undefined` → false
- `null` → false _(the note wrote "null → null"; it converts to false)_
- number: `+0`, `-0`, `NaN` → false (rest true)
- string: `""` (empty) → false (rest true)

### Truthy & falsy values

Those values which convert to `true` in the `ToBoolean()` operation are **truthy** values, and the rest are **falsy** values.

<!-- page 5 -->

- **Falsy values:** `null`, `undefined`, `+0` (normal zero), `-0`, `NaN`, `""`, `false`.
- Rest all are truthy.

```js
if (10 && 30) {
  // true && true → returns 30 → which is truthy (true)
}

let a = (10 && 30);
console.log(a); // 30

let b = (-0 && 30);
console.log(b); // -0
```

### OR operator (`||`)

- If the first operand is false, then it returns the second operand.
- If the first operand is true, then it returns the first operand.

| First | Second | Result |
|---|---|---|
| T | T | T |
| T | F | T |
| F | F | F |
| F | T | T |

- First is true → return first.
- First is false → return second.

<!-- page 6 -->

## Comparison Operators

Comparison operators always give a boolean result.

- `>`, `<`, `>=`, `<=`, `==`, `===`, etc.

```js
20 > 10;  // true
10 < 20;  // true
10 > 20;  // false
20 >= 10; // true
10 >= 10; // true  (greater than OR equal to)
```

- `==` → **Abstract Equality** operator (checks value), e.g. `a == b`
- `===` → **Strict Equality** operator

### Abstract equality

Checks if `a` and `b` are equal, or if we can convert `a` or `b` into some other type and make them equal.

```js
"10" == 10; // types are changed (conversion rule): 10 → "10"
// "10" == "10" → true
```

### Strict equality

Checks if `a` and `b` are equal and does **not** convert into any other type.

### Not-equal operators

`a != b` (abstract):

```js
10 != 10;   // false
"10" != 10; // false (after conversion they are equal)
```

`a !== b` (strict):

```js
10 !== 10;   // false → (10 === 10) is yes, both are equal
"10" !== 10; // true  → ("10" ≠ 10) — yes, both are not equal
```

<!-- page 7 -->

_Book: Clean Code_

## Comments

- Comments are the part of code which never gets executed.
- Why we need them: to give some extra information about your code.

```js
// single-line comment

/*
  comments for
  multiple lines
*/
```

## Decision Making

In a programming language we can take a decision to do a particular task based on conditions.

```js
if (user.isLoggedIn) {
  // ...
} else {
  // ...
}
```

Flow: **Logged in?** → No → **Log in** (then back to check) · Yes → **Show the dashboard** → end.

### Conditionals

Conditionals give JS decision-making capability, e.g. `if`, `else`, `else if`, etc.

```js
if (condition) {   // condition evaluates to a boolean
  // block (collection of statements)
} else {
  // else cannot execute without an 'if' condition
}
```

<!-- page 8 -->

```js
if (condition1) {
  // ...
} else if (condition2) {
  // else if can't exist without if, but can exist without else
} else {
  // ...
}
```

- The moment an `if` / `else if` block executes, the remaining blocks of the if / else-if chain won't execute.

### Nested if-else

```js
if (condition) {
  if (condition) {
    // nested if-else
  } else {
    // ...
  }
} else {
  // ...
}
```

## Lecture 04 — Bitwise Operators

Bitwise operators:

1. AND
2. OR
3. XOR
4. NOT
5. Left shift
6. Right shift

### AND (`&`)

Works at bit level (on each bit).

| a | b | a & b |
|---|---|---|
| 0 | 0 | 0 |
| 0 | 1 | 0 |
| 1 | 0 | 0 |
| 1 | 1 | 1 |

- If both are 1 → 1, otherwise → 0.

```js
5 & 6; // 4
//   101  (5)
// & 110  (6)
// -----
//   100  (4)
```

<!-- page 9 -->

### OR (`|`)

- If both are 0 → 0; all other cases give 1.

```js
5 | 6; // 7
//   101  (5)
// | 110  (6)
// -----
//   111  (7)
```

### XOR (`^`, caret)

- Same bit → 0, different bit → 1.

| a | b | a ^ b |
|---|---|---|
| 1 | 1 | 0 |
| 1 | 0 | 1 |
| 0 | 0 | 0 |
| 0 | 1 | 1 |

```js
5 ^ 6; // 3
//   101  (5)
// ^ 110  (6)
// -----
//   011  (3)
```

### NOT (`~`)

- `~5` — it requires 2's complement.

<!-- page 10 -->

### Left shift (`<<`) and right shift (`>>`)

#### Left shift (`<<`)

e.g. `5 << 2` — the right-hand number is how many times (positions) to shift.

```js
5 << 2; // 20
// 101      → shift toward the left by two positions, fill with zeros
// 10100    → bit positions 4 3 2 1 0
// 2^4 + 2^2 = 16 + 4 = 20
```

_(The note shows "2⁴ + 2¹ ⇒ 18" next to a circled 20; the correct result is 20.)_

```js
5 << 3; // 40
// 101000   → bit positions 5 4 3 2 1 0
// 2^5 + 2^3 = 32 + 8 = 40
```

- `1 << x` → 2ˣ

#### Right shift (`>>`)

```js
5 >> 2; // 1
// 0000101 → shifted right by 2 → 0000001 → 1
```

- `x >> 1` → floor(x / 2) (floor value)

<!-- page 11 -->

## Loops

In programming we might have to do a task again and again, so we require something which can do this — e.g. `for () {}`, `while ()`, `do-while ()`, etc. These help us to do a task multiple times.

### while loop

```js
while (condition) {
  // block of code
  // if the condition is false → exit the loop (break)
}
```

- Looping variables are used to loop the task. If we want to break out, we need to change the loop variable's value, and after a certain condition we need to break; otherwise it will get stuck in an ∞ (infinite) loop.

### for loop

```js
for (let i = 0; i < n; i++) { // init; compare; increment/decrement
  // block of code
}
```

- All three parts, two, one, or none of them can be given — all are valid, e.g. `for (;;)`.

### do-while loop

Ex: in a smart mall there is no checking at the entry, but at the exit the bill and products are checked.

```js
do {
  // code
} while (condition);
```

- Exit-controlled loop.
- Runs (executes) at least one time.

<!-- page 12 -->

- **Entry-controlled** loops → `while` / `for`
- **Exit-controlled** loop → `do-while`

## Unary Operators

Unary operators work on only a single operand.

| | Prefix | Postfix |
|---|---|---|
| Increment | `++a` | `a++` |
| Decrement | `--a` | `a--` |

```js
// Prefix:  b = ++a
a = a + 1;
b = a;

// Postfix: b = a++
b = a;
a = a + 1;
```

- **post** → बाद में ("after")
- **pre** → पहले ("before")

```js
let a = 5;
a = ++a; // a = 6
```

```js
let a = 5;
a = a++; // a = 5
```

## break and continue Statements

- `break` terminates the nearest loop immediately.
- `continue` skips that iteration.

### Nearest loop

```js
for (/* ... */) {
  for (/* ... */) {   // nearest loop, so only this one is terminated
    if (/* ... */) {
      break;
    }
  }
}
```

### continue

```js
if (/* ... */) {
  continue; // skip this iteration
}
```

- It brings you back to the nearest loop — it skips the lines below it (niche ke lines ko skip kar dega).

<!-- page 13 -->

## Functions in JS (Most of JS)

- To reuse our logic, we need to put it in a block such that whenever we need it, we can use it (again and again).
- **DRY principle** — write once and use more than once.
- In JS we can make our own functions, and apart from those we have a lot of inbuilt functions as well.
  - e.g. `console.log()` → a method of the `console` object.

### How to make your own function

```js
function nameOfFunction(inputs) {
  // body (code)
  // return statement — if required
}
```

### Parameters vs arguments

```js
function isOdd(num) { // num → parameter
  return num % 2 != 0;
}

isOdd(2); // false   ← 2 and 3 are arguments
isOdd(3); // true
```

- **Arguments** are the actual values that you provide as input to the function while calling it.
- **Parameter** is the placeholder variable that we mention during the function definition; it has no value until we call the function or pass a value.

<!-- page 14 -->

_Side notes: Coinbase (company) · Stackshare.io · OS → Galvin (book)_

## Program, Process & the Call Stack

- **Program** —(run)→ **Process**
  - A lot of things together make a process.
  - A process is stored in RAM (it has access to storage).
  - Each process has two stacks: (i) call stack, (ii) kernel stack.

There are 3 main storage areas in a process:

1. **Call stack** — executing the program
2. **Kernel stack** — context switching
3. **Heap memory** — runtime memory (a big pool of memory)

- Number of cores in the processor → number of processes that run in parallel.
  - For each process, one core (CPU) is required.
- On a single-core machine you can't run things in parallel; using **context switching** you can do multitasking.
  - Context switching switches between processes (process ko switch karta hai) → concurrent processes are running.
- While switching from P1 (instruction) → P2 (instruction), it stores the metadata of the process so that it knows where to resume when it comes back (it is stored in the kernel stack).

### Call stack

It is a linear memory storage (stack → LIFO).

```js
function main() {
  let a = 2;
  let b = 3;
}
// Call stack (function stack frame):
// | a = 2  |
// | b = 3  |
// | main() |
```

<!-- page 15 -->

_Note: JS has its own garbage collector._

- At any point of time in your code, if you call a function, a new entry is added to the call stack.
- In a stack you can add/remove from the top only (the top element).
  - e.g. stack: `fx2()`, `fx()`, `c()`, `b()`, `a()` — only the top can be added/deleted.
  - **LIFO** (Last In, First Out).
- Each entry is called a **stack frame**.

### Default return value

If we do not return manually from a function, then JS automatically returns `undefined`.

```js
function print() {
  console.log("function called");
}

console.log(print()); // return value → undefined
```

### Missing arguments

```js
function fx(x, y) {}

fx(10); // you are not passing a value for y, so by default it is undefined
// x = 10, y = undefined
```

### Default values

```js
function fx(x, y = 5) {}

fx(20); // now x = 20, y = 5
// if a parameter is undefined, it takes the default value
```

- **Note:** if you are passing `null` explicitly, then it will not take the default value, since `null` is a value.

<!-- page 16 -->

- But in the default case, it works sequentially:

```js
function fx(x, y = 20, z) {}

fx(20, 10);
// x = 20, y = 10 → sequential allocation
// z = undefined (not passed)
```

- So for more than 2 params, you need to pass at least that many so that it can take the value.

### Rest parameters (args)

If you don't know the number of parameters that need to be passed:

```js
function fx(...params) {} // rest parameters → it is an array of parameters

fx(1, 2, 3); // params = [1, 2, 3]
// access: params[0], params[1], ... etc.
```

- **NOTE:** `...` → used for both the spread and rest operator.
  - `[...arr]` → spread operator
  - `fx(...arr)` → rest operator _(in a function definition it is rest; in a function call it spreads)_

### Internal (built-in) functions

e.g. related to Math → `Math` (the Math class/object):

- `Math.abs()`, `Math.max()`, `Math.min()`, `Math.floor()`, `Math.ceil()`, `Math.random()`, `Math.round()`

```js
Math.ceil(5.5);  // 6
Math.floor(5.5); // 5
```

<!-- page 17 -->

- `Math.sqrt()` → square root
- `Math.random()` → random number between 0 and 1 (0 inclusive)

## Console Object

The console object is a browser feature.

1. `console.log()` → log method — prints to the terminal/console
2. `console.warn()` → warning
3. `console.error()` → for error handling

## Date Object (Important)

All things related to dates.

```js
const d = new Date();

d.getDate();
d.getDay();
d.getMonth();
d.getFullYear();
d.getHours();
d.getMinutes();
// etc.
```

- **NOTE:** months are counted from 0 → 11.

## Strings

Whenever you want to store text → a string is required.

How to create a string:

```js
"abcd"; // double quotes
'abcd'; // single quotes
`abcd`; // backticks
```

- Using backticks you can pass a variable → **string interpolation** (template string):

```js
`abcd ${name}`; // name → variable
"abcd" + name;  // you can also do it like this
```

### Escape sequences

If you want all three quote characters together, then use an escape sequence → `\` (backslash).

- e.g. `\n` → newline, `\t` → tab space, etc.
- A character escape represents a character that may not be able to be conveniently represented in its literal form.

<!-- page 18 -->

### Concat

Adding (attaching / combining) two strings: `+` or `concat()`.

```js
s1 + s2;
s1.concat(s2);
```

- `concat(_, _)` → the strings which you want to concatenate.
- If you want an extra character between the strings:

```js
s1.concat("-", s2); // output: "s1-s2"
```

### String methods

```js
firstName.toLowerCase();
firstName.toUpperCase();
// etc.
```

- **NOTE:** In JS, functions are **first-class citizens** — you can pass functions as arguments, and you can return a function from another function.

## Arrays

- Arrays are a special object in JS that can store 1 or more values of different types together.
- In memory, arrays are created in 1-D form (sequential / contiguous).
- In JS, arrays are **heterogeneous** (you can store different types of data).

```js
let arr = [];               // empty array
let arr2 = [1, 2, 3, 4, 5];
// etc.
```

<!-- page 19 -->

_Side note: REPL → Read–Evaluate–Print Loop._

- An array is a special object: `let arr = new Array();`
- JS arrays are **0-based index** (in an array object, the indexes act as the keys of the object).
- **NOTE:** `arr[outOfBound]` → `undefined`.
- **NOTE:** if you update a value at an index which does not exist, then from the last index to that index, the in-between values are `undefined`.

```js
let arr = [1, 2, 3];
arr[5] = 6;
// arr = [1, 2, 3, undefined, undefined, 6]
//        0  1  2      3          4      5
```

### `new Array(value)`

```js
const arr1 = new Array(5);       // single value → defines the size
const arr2 = new Array(1, 2, 3); // multiple values → defines the values (elements)

new Array(n).fill(val); // filled with all elements = val (same value)
```

### Inbuilt array functions

1. `arr.length` → property
2. `arr.push()`, `arr.pop()`, `arr.shift()` (remove from front), `arr.unshift()` (add to front)
3. `arr.reverse()`
4. `arr.find()`
5. `arr.indexOf(val)` → exists → index; not found → `-1`

<!-- page 20 -->

_Upcoming topics: Coercion, Scopes & Closures, Functions, OOPs, (async operations)._

## Lecture 05 — Scopes

JavaScript pillars:

1. Scopes and closures
2. Coercion and types
3. Objects & classes
4. Async programming

### Scopes and closures

- Scope, as a word, is closely related to vision, i.e. what particular part you can see and what you cannot see.
- In JS we use the concept of scopes to figure out where a variable or function is accessible/visible.

### Compilation vs interpretation

To understand the whole scoping mechanism, we need to understand the concept of compilation and interpretation in programming languages.

Most languages are divided into two categories:

1. Compiled languages
2. Interpreted languages

The question that should come to your mind is: is JS compiled or interpreted? To understand this, let's take a deeper dive into compilation and interpretation.

- **Compiled languages:** C / C++, etc.
- **Interpreted languages:** Bash (`.sh`) (terminal)
- **Hybrid languages:** compilation + interpretation — they use both, e.g. JS, Java, Python, etc.

### Nature of JS

JS combines the processes of compilation & interpretation. A lot of people think it is interpreted only, but that's not true. Why?

```js
console.log("Hello World");

function abc() {
  let x = 4y; // syntax error
}
```

- Run this and it will give an error. If JS were purely interpreted, `console.log` should run first — but it can't.

<!-- page 21 -->

_Side note: SQL is not a language → it's a standard, which means if you want to create a DBMS (DB), then you need to follow these standards. [DBMS → CMU Database Group]_

- This shows that JS somehow analyzes the whole program first, and only then starts the execution.
- Actually, every JS code is executed in 2 phases:
  - **Phase 1:** compilation and scope resolution phase
  - **Phase 2:** interpretation or execution phase

### Two different kinds of errors

- **Syntax error** — if the code is grammatically correct, then no error.
- **Semantic error** — if the thing that we are using exists, then it's correct; otherwise error.

```js
console.print(); // no syntax error (grammatically fine)...
console.print(); // ...but a semantic error (console.print doesn't exist)
```

### JIT

**Just In Time** is a management strategy that aligns production schedules with raw-material orders from suppliers. The goal is to receive goods only when they are needed for production, which can help reduce inventory cost and waste. JIT may also improve efficiency, productivity & product quality.

### Scope resolution

What do you mean by scope resolution? When we say scope resolution, we mean that we need to allocate the scope/visibility to each and every variable altogether.

### Types of scopes

In JS there are multiple types of scope available:

1. Global scope
2. Function scope
3. Block scope

#### Global scope

As the name suggests, global scope refers to the scope where the variable is accessible from anywhere in the program. Global-scoped variables are accessible throughout your program — in a function, for loop, while loop, anything.

```js
let x = 10;

function print() {
  console.log(x); // accessible
}

print();
```

<!-- page 22 -->

_(Module scope? — noted as a question)_

#### Function scope

If we had defined `x` inside the function `fun`, then we would not have been able to access `x` outside the function. If we define `x` inside the function, it will have a new scope called **function scope** — visible only inside the function (where the variable has been defined).

```js
function print() {
  let x = 20;
}

console.log(x); // not accessible (function scope) → ReferenceError
```

#### Block scope

```js
{
  let x = 10;
}
console.log(x); // ReferenceError
```

- This pair of curly braces creates a block.
- All variables defined inside a block are a.k.a. blocked variables.
- Pairs of curly braces → for loop, while loop, etc.
- A block is a valid set of instructions enclosed in a pair of curly braces.
  - Valid instructions: `let x = 10;` ✓, `let x;`

### How the variable is declared matters

So is the scope of a variable defined only by where it is declared? → **No**, the scope of a variable is also decided by **how** it is declared. There are three ways to declare:

1. `var`
2. `let`
3. `const`

- `var` helps us to declare function-scoped & global-scoped variables.
- `let` (and `const`) help us to declare block-scoped variables.

<!-- page 23 -->

- **Formal declaration:** only with `var`, `let`, `const`.
- **Informal declaration:** `x = 10` (no keyword).

### Advanced analysis

- `var` → function + global scoped.
- Any variable is used in two ways:
  - **LHS** → assign / declare the value
  - **RHS** → consume the variable

### Lexical scoping / parsing

- JS does scope resolution using **lexical scoping (LS)**. It is also called **static scoping**.
- In lexical scoping, we allocate scope to the variable during compile time.
- So in JS, values are assigned to variables in phase 2 (execution phase), but the scope of the variable is decided during phase 1.

### Let's talk about `var` (again)

- We cannot make a variable block-scoped using `var`.
- Now the question is: how does function scope differ from block scope?
  - A variable that is function-scoped has a special property: it can be defined anywhere in the function but will still be accessible throughout the whole function.

```js
function fx() {
  console.log(x); // undefined — x is visible throughout the function
  var x = 10;
  console.log(x); // 10
}
// it works → [undefined, 10]
```

```js
function fx() {
  console.log(x); // ReferenceError
  let x = 10;
  console.log(x);
}
```

### Example — phase 1 (lexical / scope resolution, line by line)

```js
var teacher = "ritesh";   // 1 → global scope
function f1() {           // 2 → change to function scope
  var teacher = "sonu";   // 3 → inside f1's function scope
  console.log(teacher);   // 4
}
function f2() {           // 5 → global scope → function scope
  var student = "Aman";   // 6 → f2's function scope
  console.log(student);   // 7
}
f1();                     // 8 → global scope (nothing happens in phase 1)
f2();                     // 9 → global scope
```

Scopes after phase 1:

- **Global scope:** `f2()`, `f1()`, `teacher = undefined`
- **f1 (function scope):** `teacher = undefined` (different scope)
- **f2 (function scope):** `student = undefined` (different scope)

In the 1st phase there is no value assignment to variables — by default they are `undefined`.

<!-- page 24 -->

- The active scope changes when you enter a function/block.
- Autoglobals? → [illegible]

### Phase 2 — execution

In the 2nd phase, the code is executed line by line:

- log of `f1()` → prints "sonu"
- `f2()` → prints "Aman"

### Example — auto globals

```js
var teacher = "ritesh";           // global scope
function f1() {                   // global scope → function scope
  teacher = "rohan";              // not in f1's scope → found in global scope → modified
  content = "JS";                 // not found in any scope → creates an auto global
  console.log(teacher, content);  // rohan JS
}
f1();
console.log(teacher, content);    // rohan JS (present in global scope via auto global)
```

### Auto global

- Those variables which are informally declared and do not exist in any scope → JS makes them **auto-global** variables (scope: global).
  - This only applies when you use the variable on the **LHS**.
- I mean: if you use it without it being made global (auto), then it will throw an error.

```js
// previous code, but logging before calling f1():
console.log(teacher, content); // in the execution phase, content is not defined anywhere → ReferenceError
f1();
```

### Question

```js
var x = 10;          // global scope
if (true) {          // block scope
  var x = 20;        // global scope (why? because var is not block scoped) — it checks
                     // whether x is in global scope → yes, so it is modified (not in phase 1)
  var y = 30;        // same → created in global scope (if not already there)
  console.log(x, y); // 20 30
}
console.log(x, y);   // 20 30
```

In the execution phase → `x = 20` (modified), `y = 30`.
