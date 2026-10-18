**1. What is the difference between `var`, `let`, and `const`? When would you use each?**

<details>
<summary>Answer</summary>

`var` is function-scoped, hoisted and initialised to `undefined`, and can be redeclared. `let` and `const` are block-scoped and sit in the Temporal Dead Zone until their declaration runs. `const` also blocks reassignment. Use `const` by default, `let` when the binding has to change, and avoid `var` in modern code.

| Feature | `var` | `let` | `const` |
| --- | --- | --- | --- |
| Scope | Function | Block | Block |
| Hoisted | Yes, as `undefined` | Yes, but in TDZ | Yes, but in TDZ |
| Redeclare in same scope | Allowed | Error | Error |
| Reassign | Allowed | Allowed | Error |
| Creates property on `globalThis` (top-level script) | Yes | No | No |
| New binding per loop iteration | No | Yes | Yes (for `for...of`) |

```js
if (true) { var a = 1; let b = 2; }
console.log(a);          // 1
console.log(typeof b);   // undefined (b is block-scoped)

const c = 10;
c = 20;                  // ❌ TypeError: Assignment to constant variable.

for (var i = 0; i < 3; i++) setTimeout(() => console.log("var", i));
for (let j = 0; j < 3; j++) setTimeout(() => console.log("let", j));
// var 3, var 3, var 3, let 0, let 1, let 2
```

- **Pitfall:** the loop example is a classic question. `var` has a single `i` that all callbacks share. `let` creates a new `j` for each iteration, so every closure keeps its own value.
- **Follow-up:** `const` stops you from reassigning the variable, but you can still change the object it points to (see Q13).

</details>

**2. Explain the Temporal Dead Zone (TDZ) with an example.**

<details>
<summary>Answer</summary>

The TDZ is the time between entering a scope and reaching the line where a `let`, `const` or `class` is declared. The binding already exists because it was hoisted, but it has no value yet. Reading or writing it in that window throws a `ReferenceError`.

The engine creates bindings for every declaration when it enters a scope. `var` bindings start out as `undefined`. `let`/`const`/`class` bindings stay uninitialised until the declaration runs. That is why the inner `z` below shadows the outer one before its own declaration line.

```js
console.log(x); // undefined (var is initialised to undefined)
var x = 1;

console.log(y); // ❌ ReferenceError: Cannot access 'y' before initialization
let y = 2;

let z = 1;
{
  console.log(z); // ❌ ReferenceError: Cannot access 'z' before initialization
  let z = 2;      // this inner z is hoisted to the top of the block
}
```

- **Pitfall:** `typeof` does not protect you from the TDZ. `typeof t; let t;` throws, while `typeof undeclaredVar` returns `"undefined"`.
- **Follow-up:** default parameters have a TDZ as well. `function f(a = b, b = 2) {}` throws when you call `f()`, because `b` is not initialised when `a` is evaluated.
- **Why it exists:** it catches use-before-declare bugs and gives `const` a meaning, since a `const` should never be seen as `undefined` first and then as its real value.

</details>

**3. What is hoisting? What gets hoisted and what does not?**

<details>
<summary>Answer</summary>

Hoisting means declarations are registered when their scope is created, before any code in it runs. Which declarations are usable before their line depends on how each one is initialised.

| Declaration | Hoisted? | Value before its line |
| --- | --- | --- |
| `function foo() {}` | Yes | The full function, so it can be called |
| `var x` | Yes | `undefined` |
| `let` / `const` | Yes | Uninitialised (TDZ), so access throws `ReferenceError` |
| `class Foo` | Yes | Uninitialised (TDZ) |
| `var f = function () {}` / arrow | Only `var f` is hoisted | `undefined`, so calling it throws `TypeError` |
| `import` | Yes, and resolved before the module runs | Usable |

Assignments and initialisers are never hoisted. Only the declaration is.

```js
console.log(sum(2, 3)); // 5
function sum(a, b) { return a + b; }

console.log(v);         // undefined
var v = "hi";

mul(2, 3);              // ❌ TypeError: mul is not a function
var mul = function (a, b) { return a * b; };

new User();             // ❌ ReferenceError: Cannot access 'User' before initialization
class User {}
```

- **Pitfall:** nothing is physically moved to the top of the file. It is a two-phase process: the engine creates the bindings first, then runs the code.

</details>

**4. What is the difference between `null` and `undefined`?**

<details>
<summary>Answer</summary>

`undefined` means a value was never assigned. The engine uses it for uninitialised variables, missing properties, missing arguments and functions that return nothing. `null` is a value you assign on purpose to say "no value" or "empty".

| | `undefined` | `null` |
| --- | --- | --- |
| Set by | The engine (by default) | The developer (on purpose) |
| `typeof` | `"undefined"` | `"object"` (historical bug) |
| `Number(x)` | `NaN` | `0` |
| In `JSON.stringify` | Property is dropped | Kept as `null` |
| Triggers a default parameter | Yes | No |

```js
let a;
const obj = { b: null };
console.log(a, obj.b, obj.c);                      // undefined null undefined
console.log(null == undefined, null === undefined); // true false
console.log(JSON.stringify({ x: undefined, y: null })); // {"y":null}

function f(p = "default") { return p; }
console.log(f(undefined), f(null));                // default null
```

- **Practical tip:** `x == null` is the usual way to check for both at once. In APIs, send `null` to say "clear this field" and leave the key out (`undefined`) to say "don't touch it". This is common in PATCH DTOs in NestJS.

</details>

**5. What does `typeof null` return and why?**

<details>
<summary>Answer</summary>

It returns `"object"`. This is a bug from the first version of JavaScript that was never fixed because fixing it would break existing websites. `null` is a primitive, not an object.

In the original engine, each value was stored with a small type tag, and the tag for objects was `000`. `null` was the NULL pointer, which is all zeros, so `typeof` read its tag as "object". A proposal to make `typeof null === "null"` was rejected because it would have broken too much existing code.

```js
console.log(typeof null); // object

// Correct object check
const isObject = (v) => v !== null && typeof v === "object";
console.log(isObject(null), isObject({}), isObject([])); // false true true

console.log(Object.prototype.toString.call(null)); // [object Null]
```

- **Follow-up:** other `typeof` surprises: `typeof []` is `"object"` (use `Array.isArray`), `typeof NaN` is `"number"`, and `typeof function(){}` is `"function"` even though functions are objects.

</details>

**6. Explain type coercion in JavaScript. Give 3 unexpected examples.**

<details>
<summary>Answer</summary>

Type coercion means JavaScript automatically converts a value to another type (string, number or boolean) when an operator or context expects it. Explicit coercion is when you write it yourself: `Number(x)`, `String(x)`, `Boolean(x)`. Implicit coercion is when an operator does it for you: `+`, `-`, `==`, `if (x)`.

Key rules:
- `+`: if either operand becomes a string after conversion to a primitive, it concatenates. Otherwise it adds numbers.
- `-`, `*`, `/`, `%`: always convert both operands to numbers.
- Objects are converted to primitives through `valueOf` and then `toString`. `[]` becomes `""` and `{}` becomes `"[object Object]"`.
- Logical and boolean contexts use truthiness.

```js
console.log("5" - 2);        // 3
console.log("5" + 2);        // 52
console.log([] + {});        // [object Object]
console.log([] == ![]);      // true
console.log("b" + "a" + +"a" + "a"); // baNaNa
console.log([1, 2] + [3]);   // 1,23
console.log(null + 1, undefined + 1); // 1 NaN
```

Why they happen:
1. `[] == ![]`: `![]` is `false` because arrays are truthy. Then `[] == false` becomes `"" == 0`, which becomes `0 == 0`, so the result is `true`.
2. `+"a"` is `NaN`, and concatenating it gives `"baNaNa"`.
3. `[1,2] + [3]`: each array becomes a string (`"1,2"` and `"3"`), and the strings are joined.

- **Pitfall:** `Number("12px")` is `NaN`, but `parseInt("12px")` is `12`. `Number("")` is `0`, which can hide empty form inputs.

</details>

**7. What is the difference between `==` and `===`? When is `==` acceptable to use?**

<details>
<summary>Answer</summary>

`===` (strict equality) compares type and value with no conversion. `==` (loose equality) first converts the operands to a common type using the Abstract Equality algorithm, then compares. Use `===` everywhere. The one widely accepted use of `==` is `x == null`, which checks for both `null` and `undefined` in one go.

```js
console.log(1 == "1", 1 === "1");            // true false
console.log(0 == "", 0 == "0", "" == "0");   // true true false  (not transitive!)
console.log(null == undefined, null == 0);   // true false
console.log(NaN == NaN, Object.is(NaN, NaN)); // false true

const v = null;
if (v == null) { /* v is null OR undefined */ }
```

Notes:
- `null` and `undefined` are loosely equal only to each other, and not to `0`, `""` or `false`. That is what makes `x == null` safe.
- Neither operator compares objects by content. Both check whether the two references point to the same object.
- `Object.is` is even stricter than `===`: `Object.is(NaN, NaN)` is `true` and `Object.is(0, -0)` is `false`.

- **Pitfall:** `null >= 0` is `true`, but `null == 0` is `false`. Relational operators convert `null` to a number, while `==` has its own special rule for `null`.

</details>

**8. List all falsy values in JavaScript.**

<details>
<summary>Answer</summary>

There are exactly 8 falsy values: `false`, `0`, `-0`, `0n` (BigInt zero), `""` (empty string), `null`, `undefined` and `NaN`. Every other value is truthy. (The browser-only `document.all` is a legacy oddity that is also falsy.)

```js
const falsy = [false, 0, -0, 0n, "", null, undefined, NaN];
console.log(falsy.every((v) => !v)); // true

// Surprisingly truthy
console.log(Boolean("0"), Boolean("false"), Boolean([]), Boolean({}), Boolean(" "));
// true true true true true

console.log([0, 1, "", "a", null].filter(Boolean)); // [ 1, 'a' ]
```

- **Pitfall:** `new Boolean(false)` is an object, so it is truthy. Empty arrays and empty objects are truthy too. Check `arr.length` or `Object.keys(obj).length` instead.
- **Pitfall in React:** `{items.length && <List />}` renders `0` when the list is empty. Write `items.length > 0 &&` instead.

</details>

**9. What is the difference between `||` and `??`?**

<details>
<summary>Answer</summary>

`||` returns the right-hand side when the left side is any falsy value (`0`, `""`, `false`, `NaN`, `null`, `undefined`). `??` (nullish coalescing) returns the right-hand side only when the left side is `null` or `undefined`. Use `??` for default values when `0`, `""` or `false` are valid values.

```js
const cfg = { retries: 0, name: "", timeout: null };

console.log(cfg.retries || 3);    // 3     (0 wrongly treated as "missing")
console.log(cfg.retries ?? 3);    // 0
console.log(cfg.name || "anon");  // anon
console.log(cfg.name ?? "anon");  // ""   (empty string kept)
console.log(cfg.timeout ?? 5000); // 5000

// Logical assignment versions
let x;      x ??= 10; // 10
let y = 0;  y ||= 5;  // 5
let z = 0;  z ??= 5;  // 0
```

- **Pitfall:** you cannot mix `??` with `||` or `&&` without parentheses. `null || undefined ?? "d"` is a `SyntaxError`. You have to write `(null || undefined) ?? "d"`.
- **Real use:** pagination defaults like `page ?? 1` and `limit ?? 20`, so that an explicit value like `0` is not replaced by the default.

</details>

**10. What is optional chaining (`?.`) and how does it differ from `&&` chaining?**

<details>
<summary>Answer</summary>

`?.` safely reads a property, calls a method or indexes into a value. If the value to its left is `null` or `undefined`, the whole chain stops and returns `undefined` instead of throwing. The difference from `&&` is that `&&` stops on any falsy value and returns that value (`0`, `""`, `null`...), while `?.` only stops on nullish values and always returns `undefined`.

```js
const user = { profile: { name: "Asha", age: 0 }, greet() { return "hi"; } };
const guest = null;

console.log(user?.profile?.name);                          // Asha
console.log(guest?.profile?.name);                         // undefined
console.log(guest && guest.profile && guest.profile.name); // null

// Falsy-but-valid values
console.log(user.profile.age && user.profile.age.toFixed(1)); // 0   (stopped early)
console.log(user.profile?.age?.toFixed(1));                   // 0.0

// Method calls and index access
console.log(user.logout?.()); // undefined (method doesn't exist)
console.log(user.greet?.());  // hi
const arr = null;
console.log(arr?.[0]);        // undefined
```

| | `a && a.b` | `a?.b` |
| --- | --- | --- |
| Stops on | Any falsy value | Only `null` / `undefined` |
| Returns when stopped | The falsy value itself | `undefined` |
| Evaluates `a` | Twice | Once |

- **Pitfall:** `?.` only protects the step it is written on. `user?.missing.deep` still throws `TypeError: Cannot read properties of undefined (reading 'deep')`. You cannot assign through it either: `obj?.a = 1` is a `SyntaxError`.
- Combine it with `??` for defaults: `user?.settings?.theme ?? "light"`.

</details>

**11. Explain the difference between a primitive type and a reference type.**

<details>
<summary>Answer</summary>

Primitives (`string`, `number`, `bigint`, `boolean`, `undefined`, `null`, `symbol`) are immutable values, and they are copied by value. Reference types (objects, arrays, functions, Maps, and so on) live on the heap. A variable holding one stores a reference to it, so copying the variable copies the reference, not the object.

| | Primitive | Reference |
| --- | --- | --- |
| Mutable | No (operations create new values) | Yes |
| Assignment copies | The value | The reference |
| `===` compares | Values | Identity (same object?) |
| Passed to a function | A copy of the value | A copy of the reference |

```js
let a = 10;
let b = a;   // copy of the value
b++;
console.log(a, b);                  // 10 11

const o1 = { n: 1 };
const o2 = o1; // copy of the reference
o2.n = 2;
console.log(o1.n);                  // 2
console.log({ n: 1 } === { n: 1 }); // false

function mutate(obj, num) { obj.n = 99; num = 99; }
let num = 1;
mutate(o1, num);
console.log(o1.n, num);             // 99 1

function reassign(obj) { obj = { n: 0 }; }
reassign(o1);
console.log(o1.n);                  // 99
```

- **Follow-up:** "Is JavaScript pass-by-reference?" No. It is always pass-by-value. For objects, the value that gets copied is a reference, sometimes called "call by sharing". That is why `reassign` above has no effect on the caller, while `mutate` does.

</details>

**12. What happens when you assign an object to another variable in JavaScript?**

<details>
<summary>Answer</summary>

Only the reference is copied. Both variables point to the same object in memory, so a change made through one variable shows up through the other. To get an independent object you have to copy it: shallow copy with spread or `Object.assign`, or deep copy with `structuredClone`.

```js
const user = { name: "Ravi", address: { city: "Pune" } };

const alias   = user;                  // same object
const shallow = { ...user };           // new top-level object, shared nested objects
const deep    = structuredClone(user); // fully independent

alias.name = "Kiran";
shallow.address.city = "Delhi";

console.log(user.name);          // Kiran
console.log(shallow.name);       // Ravi  (copied before the change)
console.log(user.address.city);  // Delhi (nested object is shared)
console.log(deep.address.city);  // Pune
console.log(alias === user, shallow === user, shallow.address === user.address);
// true false true
```

| Method | Depth | Notes |
| --- | --- | --- |
| `b = a` | None (alias) | Same object |
| `{ ...a }`, `Object.assign({}, a)`, `[...arr]` | Shallow | Nested objects are still shared |
| `structuredClone(a)` | Deep | Handles `Date`, `Map`, `Set` and cycles. Throws on functions and DOM nodes |
| `JSON.parse(JSON.stringify(a))` | Deep | Drops `undefined` and functions, turns `Date` into a string |

- **Why it matters in React:** React compares state by reference. If you mutate an object and call `setState` with the same reference, the component does not re-render. Always create new objects or arrays.

</details>

**13. How does `const` work with objects and arrays?**

<details>
<summary>Answer</summary>

`const` makes the binding immutable, not the value. You cannot point the variable at a new object, but you can still change the object's properties or the array's elements. To make the value itself read-only, use `Object.freeze`, which is shallow.

```js
const arr = [1, 2];
arr.push(3);
console.log(arr);          // [ 1, 2, 3 ]

const obj = { a: 1 };
obj.a = 2; obj.b = 3; delete obj.a;
console.log(obj);          // { b: 3 }

arr = [];                  // ❌ TypeError: Assignment to constant variable.

const frozen = Object.freeze({ x: 1, inner: { y: 1 } });
frozen.x = 2;              // silently ignored (throws TypeError in strict mode)
frozen.inner.y = 2;        // allowed, because freeze is shallow
console.log(frozen.x, frozen.inner.y); // 1 2
```

- **Pitfall:** in strict mode (ES modules and classes run in strict mode), writing to a frozen property throws `TypeError: Cannot assign to read only property 'x' of object`.
- **Follow-up:** for deep immutability, freeze recursively. In TypeScript, `as const` or `Readonly<T>` / `ReadonlyArray<T>` give you immutability at compile time only.

</details>

**14. What is the difference between `function declaration` and `function expression`?**

<details>
<summary>Answer</summary>

A function declaration (`function foo() {}` written as a statement) is fully hoisted, so you can call it before its line. A function expression (a function used as a value, e.g. `const foo = function () {}` or an arrow) is created only when that line runs, so it follows the hoisting rules of the variable it is assigned to.

| | Declaration | Expression |
| --- | --- | --- |
| Syntax | `function name() {}` as a statement | `const f = function () {}`, `() => {}` |
| Hoisting | Whole function | Only the variable (`undefined` for `var`, TDZ for `let`/`const`) |
| Name | Required | Optional (can be anonymous or named) |
| Typical use | Top-level helpers | Callbacks, closures, conditional definitions, IIFEs |

```js
console.log(declared(2)); // 4
function declared(n) { return n * 2; }

expressed(2); // ❌ ReferenceError: Cannot access 'expressed' before initialization
const expressed = function (n) { return n * 2; };

// Named function expression: the name is visible only inside the function
const fact = function inner(n) { return n <= 1 ? 1 : n * inner(n - 1); };
console.log(fact(5));      // 120
console.log(typeof inner); // undefined
```

- **Follow-up:** named function expressions show readable names in stack traces and can call themselves safely even if the outer variable is reassigned.

</details>

**15. Can you call a function before it's declared? Explain why or why not.**

<details>
<summary>Answer</summary>

Yes, if it is a function declaration. During the creation phase the engine puts the whole function object into scope, so it can be called from anywhere in that scope. No, if it is a function expression or an arrow function. The variable holding it is either `undefined` (`var`, so you get a `TypeError`) or in the TDZ (`let`/`const`, so you get a `ReferenceError`).

```js
greet(); // hello
function greet() { console.log("hello"); }

hi();    // ❌ TypeError: hi is not a function   (hi is undefined)
var hi = () => console.log("hi");

hey();   // ❌ ReferenceError: Cannot access 'hey' before initialization
const hey = () => console.log("hey");
```

- **Pitfall:** avoid function declarations inside blocks (`if (x) { function f() {} }`). Their hoisting differs between strict mode and sloppy mode, and between engines.
- **Follow-up:** a function can still refer to a `const` that is declared later, as long as the function is called after that declaration has run. The TDZ depends on when code runs, not where it is written.

</details>

**16. What is an IIFE and what is it used for?**

<details>
<summary>Answer</summary>

An IIFE (Immediately Invoked Function Expression) is a function that is defined and called in the same step: `(function () { ... })()`. It creates a private scope that runs once. It was used to avoid polluting the global scope and to build the module pattern. Today it is mostly used for top-level `async` code and one-off initialisation.

The wrapping parentheses make the parser read `function` as an expression instead of a declaration, which lets you call it right away.

```js
// Module pattern: private state through closure
const counter = (function () {
  let count = 0; // private
  return {
    inc: () => ++count,
    get: () => count,
  };
})();
counter.inc(); counter.inc();
console.log(counter.get()); // 2
console.log(counter.count); // undefined

// Async IIFE (common in scripts without top-level await)
(async () => {
  const data = await Promise.resolve("loaded");
  console.log(data);        // loaded
})();
```

Uses:
- Data privacy / encapsulation (module pattern)
- Avoiding global variables (before ES modules existed)
- Running `async` setup code in CommonJS
- Capturing loop variables in old `var`-based code

- **Pitfall:** if the previous line has no semicolon, a line starting with `(` gets joined to it as a function call. That is why you sometimes see `;(function(){})()`.

</details>

**17. What is a pure function? Give an example of a pure and impure function.**

<details>
<summary>Answer</summary>

A pure function (1) always returns the same output for the same inputs and (2) has no side effects. It does not change its arguments or outside state, and it does no I/O, logging, randomness or time reads. Pure functions are easy to test, safe to memoise and simple to reason about.

```js
// Pure
const add = (a, b) => a + b;
const withItem = (cart, item) => [...cart, item]; // returns a new array

// Impure
let total = 0;
const addToTotal = (n) => (total += n);                            // changes outer state
const pushItem = (cart, item) => { cart.push(item); return cart; }; // changes its input
const stamp = () => Date.now();                                    // result differs on each call

const cart = ["pen"];
console.log(withItem(cart, "book"));       // [ 'pen', 'book' ]
console.log(cart);                         // [ 'pen' ]  (unchanged)
pushItem(cart, "ink");
console.log(cart);                         // [ 'pen', 'ink' ]
console.log(addToTotal(5), addToTotal(5)); // 5 10  (same input, different output)
```

- **Why interviewers care:** React reducers and render functions are expected to be pure. `useMemo`, `React.memo` and Redux all rely on it. In NestJS, keeping business logic in pure functions makes unit tests simple because you don't need to mock anything.
- **Follow-up:** real apps need side effects. The goal is to keep them at the edges (controllers, effects) and keep the core logic pure.

</details>

**18. What is the difference between `arguments` and rest parameters?**

<details>
<summary>Answer</summary>

`arguments` is an old array-like object (it is not a real array) that exists automatically in non-arrow functions and holds every argument passed in. Rest parameters (`...args`) give you a real array containing only the arguments that were not assigned to named parameters. Use rest parameters in modern code.

| | `arguments` | Rest `...args` |
| --- | --- | --- |
| Type | Array-like object | Real `Array` |
| Array methods | No (convert with `Array.from`) | Yes |
| Contains | All arguments | Only the remaining ones |
| In arrow functions | Not available (uses the outer function's `arguments`) | Works |
| Counted in `fn.length` | N/A | No |

```js
function oldSum() {
  // Array.isArray(arguments) === false
  return Array.prototype.reduce.call(arguments, (s, n) => s + n, 0);
}
function newSum(first, ...rest) {
  // Array.isArray(rest) === true
  return rest.reduce((s, n) => s + n, first);
}
console.log(oldSum(1, 2, 3), newSum(1, 2, 3)); // 6 6

// Arrow functions use the outer function's arguments
function outer() { const inner = () => arguments[0]; return inner("x"); }
console.log(outer("from outer")); // from outer

// In sloppy mode with simple params, arguments is linked to the named params
function sloppy(a) { arguments[0] = 99; return a; }
console.log(sloppy(1)); // 99
```

- **Pitfall:** the link between `arguments` and named parameters only exists in sloppy mode with simple parameter lists. Strict mode, or any rest, default or destructured parameter, removes it.

</details>

**19. What is currying? Write a curried `add(1)(2)(3)` function.**

<details>
<summary>Answer</summary>

Currying turns a function that takes several arguments, `f(a, b, c)`, into a chain of functions that each take one argument: `f(a)(b)(c)`. Each call returns a new function that remembers the arguments so far through a closure. It is useful for partial application: you fix some arguments now and supply the rest later.

```js
// 1. Fixed arity
const add = (a) => (b) => (c) => a + b + c;
console.log(add(1)(2)(3)); // 6

// 2. Generic curry for any fixed-arity function
function curry(fn) {
  return function curried(...args) {
    if (args.length >= fn.length) return fn.apply(this, args);
    return (...next) => curried.apply(this, [...args, ...next]);
  };
}
const add3 = curry((a, b, c) => a + b + c);
console.log(add3(1)(2)(3), add3(1, 2)(3), add3(1)(2, 3)); // 6 6 6

// 3. Unlimited chain, ended by an empty call
function sum(a) {
  return (b) => (b === undefined ? a : sum(a + b));
}
console.log(sum(1)(2)(3)(4)()); // 10

// Partial application in practice
const logWith = curry((level, msg) => `[${level}] ${msg}`);
const warn = logWith("WARN");
console.log(warn("disk low")); // [WARN] disk low
```

How `curry` works: it compares the number of arguments collected so far with `fn.length`, the function's declared parameter count. When there are enough, it calls `fn`. Otherwise it returns a function that collects more arguments. Each call does O(n) work to copy the arguments.

- **Pitfall:** `fn.length` does not count default or rest parameters, so a generic `curry` does not work well with them.

</details>

**20. What does the `in` operator do? How is it different from `hasOwnProperty`?**

<details>
<summary>Answer</summary>

`"key" in obj` returns `true` if the property exists anywhere on the object or its prototype chain. `obj.hasOwnProperty("key")` returns `true` only if the property is defined directly on the object itself. Prefer `Object.hasOwn(obj, key)` (ES2022) over `hasOwnProperty`.

```js
class Animal { speak() {} }
const dog = new Animal();
dog.name = "Rex";

console.log("name" in dog);               // true  (own)
console.log("speak" in dog);              // true  (inherited from the prototype)
console.log(dog.hasOwnProperty("speak")); // false
console.log(Object.hasOwn(dog, "name"));  // true
console.log("toString" in {});            // true  (from Object.prototype)

// Existence vs. value
const o = { x: undefined };
console.log("x" in o, o.x !== undefined); // true false

// Objects with no prototype
const bare = Object.create(null);
bare.id = 1;
bare.hasOwnProperty("id");                // ❌ TypeError: bare.hasOwnProperty is not a function
console.log(Object.hasOwn(bare, "id"));   // true

console.log(1 in [10, 20], 2 in [10, 20]); // true false  (checks indexes, not values)
```

| | `in` | `hasOwnProperty` / `Object.hasOwn` |
| --- | --- | --- |
| Checks prototype chain | Yes | No |
| Works on `Object.create(null)` | Yes | Only `Object.hasOwn` does |
| Typical use | Type narrowing / feature detection (`"fetch" in window`) | Iterating own keys, validating input |

- **TS follow-up:** `in` narrows union types: `if ("email" in user)` tells TypeScript which member of the union you have.
- **Pitfall:** `in` with an array checks indexes, not values. Use `includes` to check for a value.

</details>
