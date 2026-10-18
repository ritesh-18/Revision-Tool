<!-- page 1 -->

> Top-of-page note: **Type coercion** → **Implicit** (JS converts by default) / **Explicit** (manual conversion).

## Type Coercion (continued)

### 1. What is an abstract operation?

- Abstract operations are **spec-only helper functions** that the JS spec uses to define behaviour, e.g. `ToNumber`, `ToBoolean`, etc.
- They are not exposed to JS directly, but you can approximate them.

### Types of abstract operations

#### (1) `ToBoolean(arg)`

- Converts any data type into a boolean (true/false).
- **Falsy values** (most important): `+0`, `-0`, `NaN`, `undefined`, `false`, `""` (empty string), `null`.
- All the rest are **truthy** values (e.g. `{}`, `Symbol` — both are considered truthy, etc.).
- You can't use `ToBoolean()` directly. If you want to check whether something is true/false, you can use the **logical NOT operator** `!` — similar, but it returns the opposite value.

```js
!("")    // true  (means "" is a falsy value)
!(0)     // true  (0 is falsy)
!(true)  // false
```

#### (2) `ToNumber(arg)`

The abstract operation `ToNumber()` converts `arg` to a value of type Number:

| Argument type | Result |
| --- | --- |
| Undefined | `NaN` (converted value) |
| Null | `+0` |
| Boolean | `true` → `1`, `false` → `+0` |
| Number | no conversion |
| String | see the grammar / conversion algorithm |
| Symbol | throws a `TypeError` exception |
| Object | step 1: `ToPrimitive()`, step 2: `ToNumber()` |

```js
1 - '2'   // => 1 - 2 => -1
```

- Both operands are converted to Number (a sub-method called `ToNumber()` is used for both the left and right operands).

### Primitive vs non-primitive data types

- **Primitive data types**: those data types which are atomic in nature (can't be further divided), e.g. number, etc.
- **Non-primitive data types**: those which are created by using primitive data types, e.g. object, array, etc.

<!-- page 2 -->

> Top-of-page note: for the `+` operator — if any one of left/right is a string then concatenate, otherwise addition.

- **Primitive values**: Number, String, undefined, null, boolean.
- `ToPrimitive()` converts a value into a primitive value.

### The `+` operator

- If any one operand is a string → **concatenate**: `1 + '2'` → `'12'`.
- Else → convert into number (`ToNumber()`) and **add**: `1 + 2` → `3`.
- Before this, it checks whether left/right is primitive (`ToPrimitive()`); only then does the above apply. Otherwise it behaves differently:

```js
[1, 2] + [3, 4]      // "1,23,4"  (both arrays become strings "1,2" and "3,4", then concatenated)

1 + null             // 1 + (+0) = 1
1 + undefined        // undefined is converted to Number → 1 + NaN => NaN
anything + NaN       // NaN  (for numeric addition)
```

> Note: the notebook writes the array result as `[1,23,4]`; the actual result is the string `"1,23,4"`.

## Abstract Equality Comparison (`==`) and Strict Equality Comparison (`===`)

### (1) Abstract equality (`==`)

- `x == y`, where x and y are values; produces true/false.
- **Step 1**: if `Type(x)` is the same as `Type(y)`, then do a strict equality comparison (`===`).
- Otherwise (implicit conversion) do these operations:
  1. If `x` is `null` and `y` is `undefined` → `true` (`null == undefined` → true; also `undefined == null` → true).
  2. `string == number` → the string is converted into a number with `ToNumber()`.

<!-- page 3 -->

> Top-of-page notes:
> - `NaN === NaN` → false
> - `NaN == NaN` → false
> - `NaN == undefined` → false (`ToNumber(undefined)` is `NaN`)
> - "Assert" means validate (to figure out).

3. `boolean == R` → the boolean is converted with `ToNumber()`: `true` → `1`, `false` → `0`.
4. `(String | Number | Symbol) == Object` → the object is converted into a primitive. Same for the swapped version (`Object == String/Number/Symbol`).

### (2) Strict equality (`===`)

- If the types are different → return `false`.
- Else (for `Type(x)` = Number): if left or right is `NaN` → return `false`.

```js
let x = +0, y = -0;
x === y   // true
```

## New video on type casting: `ToPrimitive()`

- It takes two different arguments: (i) the input argument, (ii) an optional argument `preferredType`.
- It converts your object into a non-object; and if this value is capable of converting to more than one primitive type, it may use the optional hint `preferredType` to favour that type.

1. If `preferredType` is not defined → by default the hint is `"default"`. If it is String → hint `"string"`; same for Number → `"number"`.
2. If your hint is `"default"`, then make it `"number"`.
3. Now call → `OrdinaryToPrimitive(input, hint)`.

**Diagram (flow of `OrdinaryToPrimitive`)**, described in words:

- It checks `typeof hint === "string"`, and then the content of the hint (`"string"` or `"number"`):
  - hint `"string"` → method order `["toString", "valueOf"]` — if you want to convert an object into a string, it will call `toString` first, then `valueOf`.
  - hint `"number"` → method order `["valueOf", "toString"]` — but here, if the hint is Number, it will first convert with `valueOf`, then with `toString`.
- It loops over these methods and calls each one. For the output it checks "is it an object?":
  - **false** (it's a primitive) → return that value (once one output is obtained, it stops).
  - **true** → try the next method (e.g. first `toString`, then `valueOf`).
- If the loop ends without a primitive → output is a `TypeError`.

<!-- page 4 -->

```js
let x = {};
x.toString()   // '[object Object]'
x.valueOf()    // {}  → returns the default object itself
```

### Important example

```js
let x = 10;
let y = { a: 10 };
x - y   // NaN ? but why?
```

Steps:

1. Do `ToNumber(x)` / `ToNumber(y)`.
2. Internally checks: is anyone an object? Yes (`y`) → with hint = `"number"` → `ToPrimitive(y)`.
3. Method order `[valueOf, toString]`:
   - `valueOf(y)` = `y` → an object, so move on.
   - `toString(y)` = `'[object Object]'` → but this is not a number.
4. (The notebook notes: again call `toString` with hint = string → same.) Then `ToNumber('[object Object]')` → `NaN`.
5. Solution: `10 - NaN` → `NaN`.

- **Most important**: if you override the `valueOf` / `toString` method, then it behaves differently.

```js
10 - undefined    // NaN  → converted with ToNumber(undefined) = NaN
10 - NaN          // NaN
10 * undefined    // NaN
10 / undefined    // NaN
10 + undefined    // NaN
NaN - NaN         // NaN
```

<!-- page 5 -->

> Top-of-page note: `typeof null` → `"object"`.

```js
10 - null     // 10  → ToNumber(null) = +0
null - null   // 0
null * null   // 0
null / null   // NaN
```

- Why is `null / null` NaN? The notebook's reasoning: `null / null` → `0 / 0` → "Error [undefined]" → `ToNumber(undefined)` → `NaN`.
  > Note: more precisely, both nulls become `0`, and `0 / 0` is itself `NaN` in JS (no error / undefined involved).

```js
null + NaN          // NaN
undefined + null    // NaN + null => NaN
```

```js
[2, 3] + [4, 5]     // "2,34,5"
// toString([2,3]) → '2,3'; '2,3' + '4,5' → '2,34,5'
```

```js
[2, 3] - [4, 5]     // NaN ? why
```

- `-` needs `ToNumber` on objects → `ToPrimitive([2,3])` with hint Number.
- `valueOf([2,3])` → returns the array itself (an object), so next:
- `[2,3].toString()` → not `'[object Object]'` (crossed out in notes) — it returns `'2,3'`.
- `ToNumber('2,3')` → `NaN` (because of the comma).

### Functions

```js
function f() {}
f.valueOf()    // returns the function itself (f)
f.toString()   // returns the function in string format
```

- Example: `'Str1' + fx` → becomes `'Str1'` followed by the function's source text.

### Objects with operators

```js
{} + {}        // '[object Object][object Object]'
{} + [1, 2]    // '[object Object]1,2'   (marked important)
{} * {}        // NaN
{} * []        // NaN
// converted into Number: '[object Object]' → ToNumber() → NaN * NaN
```

> Note: `[]` alone actually converts to `0` (`'' → 0`), so `{} * []` is `NaN * 0` = `NaN`. Also, typed at the start of a console line, a leading `{}` may be parsed as an empty block rather than an object.

<!-- page 6 -->

## Comparison Operators

Question: why does `1 < 2 < 3` give `true` but `3 > 2 > 1` give `false`?

- How comparison operators work: they always return a boolean; evaluated left → right (operator precedence / associativity).

```js
1 < 2 < 3
// (1 < 2) → true → ToNumber(true) = 1
// (1 < 3) → true

3 > 2 > 1
// (3 > 2) → true → ToNumber(true) = 1
// (1 > 1) → false
```

### Template literals (type coercion into string)

```js
let y = 10;
`Hello value of y is ${y}`   // "Hello value of y is 10"

let y2 = {};
`Hello value of y is ${y2}`  // "Hello value of y is [object Object]"
```

- Why? `toString({})` → `'[object Object]'`; `valueOf()` (1st) returns the same object, so `toString` is the 2nd operation.
- Notes say: for `{}` the hint is Number by default.
  > Note: template literals actually use the `"string"` hint, so `toString` is called first. The result is the same here.

### Unary plus and double NOT

```js
let s = "123";
let num = +s;       // 123 → Number (through number conversion)

let s2 = "123";
let boolVal = !!s2; // !("123") → false; !false → true
// used for boolean conversion
```

<!-- page 7 -->

> Top-of-page note: **undefined vs not defined**
> - *not defined*: the variable does not exist.
> - *undefined*: the variable actually exists, but its value is not initialised (or it's accessed before initialisation).

## Manual (Explicit) Type Conversion

```js
Number("123")   // 123
Number("")      // 0
Number("-0")    // -0

String(10)      // '10'
String(0)       // '0'
String(-0)      // '0'
```

- `+0` / `-0` have many use cases (e.g. in the game world — acceleration direction, + / -).

### Question: write a function which takes a value and returns whether the value is `NaN` or not

- But you can't compare `NaN == NaN` (it is false). Then how?
- `typeof NaN` → `"number"`.
- `isNaN()` → checks whether the value's final conversion is `NaN`; if so it returns `true` (e.g. for a non-numeric string).
- `Number.isNaN()` → checks strictly (only `NaN` itself returns `true`).

```js
isNaN("abc")         // true  (converted to NaN)
Number.isNaN("abc")  // false
Number.isNaN(NaN)    // true
```

### Detecting `-0`

```js
-0 == 0     // true
-0 === 0    // true
-0 > 0      // false
-0 < 0      // false
```

- Then how do we know if it is `-0` or `0`?

```js
Object.is(-0, 0)   // false
Math.sign(-0)      // -0
Math.sign(0)       // 0
```

## Autoboxing

```js
let x = 10;
x.toString()   // "10"
```

- But this is only allowed with objects (so how is it possible?).
- So in JS there is a concept called **autoboxing**.

<!-- page 8 -->

> Top-of-page note: data types in JS — Boolean, BigInt, Number, Undefined, Null, Symbol, String.

- For a moment, JS converts (wraps) the primitive value (variable) into an object so that you can use methods which are only present on objects, e.g. `toString()`, `valueOf()`. This is known as **autoboxing**.
- But it is not applicable directly with primitive (number) literals — except strings:

```js
10.toString()      // ✗ SyntaxError
(10).toString()    // ✓
"abc".toString()   // ✓
"abc".valueOf()    // ✓   (with string literals you can use both)
```

- Whenever we try to access a method or property on a primitive, that primitive is wrapped into an object. That is called **autoboxing**.

<!-- page 9 -->

## (Most Important) Lecture — Async / Await (Async functionality)

### Introduction to callbacks

- A function which can accept a function as an argument is known as a **HOF** (higher-order function).
- The function which is being passed into it as an argument is known as a **callback function**.
- **Callback function**: functions which are passed as an argument to a HOF.

```js
arr.map(function fn(e) { /* ... */ });
// arr.map → HOF, fn → callback function
```

- **Benefits of callbacks**: we can decide at runtime what to send as the implementation of the callback.
- **Disadvantages of callbacks**:
  1. Callback hell (minor disadvantage — a readability problem).
  2. Inversion of control (major disadvantage).

### 1) Callback hell

```js
f1(function () {
  f2(function () {
    f3(function () {
      // ...
    });
  });
});
// pyramid structure → "callback hell"
```

- When our HOF calls (with an argument) another function, that function again calls a callback function, and this callback again calls another callback function — this creates deeply nested, hard-to-read and hard-to-maintain code. This is nothing but **callback hell**.

<!-- page 10 -->

### 2) Inversion of control

Example: **SuperPay** (payment for merchants) provides an SDK; our site is `nightcode.io` [partly illegible].

```js
superpay.makePayment(creds, function f() { /* ... */ });
// here we are putting our trust in SuperPay (the SDK function)
```

- Here we are building trust with SuperPay that only one payment will happen, it will not run/execute multiple times, and it will not fail the `makePayment` function.
- What if it does not follow these things? This is nothing but **inversion of control**: we have handed over to another function the job of calling our implementation (the control goes to another function).
- **Inversion of control** is a phenomenon in which we give the control of executing our callback function to some other HOF, which may or may not call it the right way.

## Async Programming

There are two ways to write a program:

1. **Synchronous program** — line-by-line execution (first one finishes, then the next executes; queue-like).
2. **Asynchronous program** — also line by line, but if line 1 is not fully executed, line 2 can start executing, etc.; it does not depend on previous execution (not a sequential order of execution).

**Q. What is the default nature of JS?**

- Any native piece of JS code is always synchronous in nature (native code = code which is defined in the documentation / spec).

<!-- page 11 -->

### JS is synchronous in nature because it is single-threaded

- In a single-core CPU: two or more processes can't be executed in parallel; it can execute only one process at a time.

### Async code

```js
setTimeout(function () {       // runtime feature
  console.log("Time up");      // (2) executes second
}, 10);
console.log("Hello World");    // (1) executes first
```

- Why does it behave as async here? Because `setTimeout()` is not a native piece of JS code (it's an async function provided by the runtime).
- How does this type execute (behind the scenes)?
  - The runtime environment provides → event loop, queues (microtask queue, macrotask queue), call stack.
  - The event loop checks whether the call stack is free or not; if it is free, then it executes the non-JS-native code.

## Async JS and its features

### Closure properties

```js
function fx() {
  let a = 10;
  return function () {
    console.log(a);
  };
}

const res = fx();
res();              // prints 10 — how?
console.dir(res);   // for more details
```

<!-- page 12 -->

- (In `console.dir`) you will get scopes → **Closure** (`a`) — it remembers those variables which we want — **Script**, **Global**.
- **Definition**: a **closure** is a mechanism through which any inner function remembers all those variables which are defined in its outer scope (even after the outer function is out of scope).

### Q. How to resolve the problems of callback functions?

Solution: **Promises in JS** (an official part of JS).

- Resolves both problems — but technically it can't resolve callback hell (you can get "promise hell"), but it fully resolves IoC.
- **Promises** are readability enhancers. They are special JS objects which help us control future-related tasks.
- Two parts: (i) how to create a promise, (ii) how to consume a promise.
- **Note**: generally we prefer using promises when we have to deal with a future task.

### Problem

Implement a set of dummy functions which can mimic the behaviour of the following functions:

1. **download**: this function should mimic downloading some content from a URL.
2. **writeFile**: this function should mimic writing the content to a file.
3. **upload**: this function should mimic uploading the file to a server.

Now, after you've implemented these functions, try to use them in a scenario where we first download a file, then write it to a disk, and then upload it to the server.

<!-- page 13 -->

> Top-of-page note (**optional chaining**): `?.` → checks if it is present, then does it, otherwise skips. E.g. `callback?.(param)` → checks whether the callback was passed or not.

- After downloading / writing / uploading we need to call a callback function, so that we are able to perform some operation. E.g. after downloading we have some operations to perform with this data, so we can pass a callback function and call it after completion of downloading the file.

```js
function download(url, callback) {
  console.log("data is downloading from this url", url);
  setTimeout(() => {
    const data = "dummy data";            // (not in notes – added so `data` exists)
    console.log("data are downloaded");
    callback(data);
  }, 3000);
}

function writeFile(data, filename, callback) {
  console.log(`write data in ${filename}`);
  setTimeout(() => {
    console.log("writing to a file is done");
    const status = true;
    callback(status);
  }, time);
}

function uploadFile(filename, url, callback) {
  console.log("...");                      // [illegible]
  setTimeout(() => {
    console.log("file uploaded");
    const status = true;
    callback(status);
  }, time);
}

function process(url) {
  download(url, (data) => {
    writeFile(data, "file.txt", (status) => {
      uploadFile("file.txt", url, (status) => {
        console.log("All done");
      });
    });
  });
}
```

> Note: `time` is a placeholder delay in the notes. The notebook writes the first function as `function(url, callback)` without a name, and `process` as `function process(url, (data) => ...`; rewritten above as valid JS.

<!-- page 14 -->

- The previous example (`process` function) has the callback hell problem along with IoC.
- How to resolve → **Promise**.

## How to create a Promise

- In JS we have a `Promise` constructor.

```js
const p1 = new Promise(/* executor callback (resolve, reject) */);
```

- This constructor expects a callback in the arguments → this callback is called the **executor callback**.
- **Why is it called the executor callback?** Because when we create a promise object, at that point of time our constructor executes this callback. That means this callback is executed by the promise constructor immediately.

**Q. How does this callback look?**

```js
new Promise((res, rej) => {
  // block of code
});
// res → resolve, rej → reject (these are also callback functions)
```

- Our job is to give the definition of the callback function.

```js
const p1 = new Promise((resolve, reject) => {
  resolve("Promise has been resolved");
});
```

**Q. How does a promise object look?**

- Diagram: a box with two internal slots — **value** (PromiseResult) and **status** (PromiseState).
- Status can be: **pending**, **fulfilled**, **rejected** (a promise has three states; at a time only one state).
- **pending**: whenever a promise object is created (by default it is in the pending state).

<!-- page 15 -->

### Status

- Diagram: from **pending**, the promise goes to exactly one state — either **fulfilled** or **rejected**. A promise object can change its state only once (at most one state).
  - **fulfilled** → the operation was successful (the operations inside the callback function).
  - **rejected** → the operation was unsuccessful.
- "Operation" refers to an algorithm written inside a function (the callback).
- `resolve()` → if you call this function inside the callback → status: **fulfilled**.
- `reject()` → status: **rejected**.

### Value — PromiseValue (very important)

- Initial value: `undefined`.
- Using `resolve()` / `reject()` you can change the promise value:

```js
resolve(dataValue);
// takes an argument which changes the value from undefined → data value
```

### Internal methods and hidden properties

- A promise has some internal methods: `finally()`, `catch()`, `then()`, etc.
- Some hidden properties: `onFulfillment: []`, `onRejection: []` — both are arrays.

**Q. What is the use of these arrays?**

- These arrays are internally managed by the Promise and are initially empty.
- We can store some functions (callbacks) in both of these arrays. How? Using the `.then()` function available on a promise object.
- These functions remain in their respective arrays as long as the promise is pending.
- If the promise moves to the fulfilled state, all the functions stored in the `onFulfillment` array are queued in a new queue in memory called the **microtask queue**, and the `onRejection` array does nothing.
- If the promise goes to the rejected state, then all the functions in the `onRejection` array go to the microtask queue, and the `onFulfillment` array does nothing.

<!-- page 16 -->

> Top-of-page note: "[So far so good] → so far everything is fine" (Hindi remark; partly unclear).

### Q. How to consume a promise?

- A promise acts as a placeholder object for something that will come in the future.
- Once the future execution is done, we might want to execute some algorithm (based on whether the future task failed or succeeded).
- To achieve this, the promise object has the `.then()` function.

```js
const pr = new Promise(executor);
pr.then(onFulfilled, onRejected);
// onFulfilled → mandatory (function) → goes to the onFulfillment array
// onRejected  → optional (function)  → goes to the onRejection array
```

```js
pr.then(a, b);
pr.then(c, d);
pr.then(e, f);
// onFulfillment: [a, c, e]
// onRejection:   [b, d, f]
```

### Event loop, microtask queue and macrotask queue

- **Macrotask queue**: all callbacks of timers.
- **Microtask queue**: all functions of a promise which are present in `onFulfillment[]` / `onRejection[]`.
- Diagram: the event loop picks from both queues; priority → microtask queue first, then macrotask queue.

- When the promise is fulfilled, push all the `onFulfillment[]` functions into the microtask queue and skip the rejected-array functions (do nothing), and vice versa.
- The event loop executes the microtasks first (higher priority).
- Then after that the macrotask queue executes (in FIFO order).
- After promise fulfilment → it returns (generates) the promise value; you can get it from the `.then()` function: `function (promiseValue) { }`.

> Side note in the margin: "This is not always true; it's a simplified explanation."

<!-- page 17 -->

```js
p.then(function (promiseValue) {});
```

- For every `.then()` we can get the same promise value.

(The rest of this page is blank; the faint text visible is bleed-through from the other side of the sheet.)
